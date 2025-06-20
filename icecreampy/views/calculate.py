from flask import Blueprint, flash, render_template, request, session, redirect
from icecreampy.models.category import Category
from icecreampy.models.products import Product
from icecreampy.models.products_restrictions import ProductRestriction
from icecreampy.models.result import Result
from icecreampy.models.result_products import ResultProduct
from icecreampy.models.fixed_costs import FixedCost
from icecreampy.ext.database import db
from decimal import Decimal, ROUND_HALF_UP
import pulp

bp = Blueprint('calculate', __name__)

@bp.route('/calculate', methods=['POST'])
def calculate():
    if not session.get('loggedin'):
        return redirect('/')

    try:
        # IDs produtos selecionados e categoria
        product_ids = request.form.getlist('products[]')
        category_id = request.form.get('category_id_max')

        # Dados completo dos produtos e categoria
        category = Category.query.get(category_id)
        products = Product.query.filter(Product.id.in_(product_ids)).all()

        # Verifica se existem produtos selecionados
        if not products:
            flash("Selecione pelo menos um produto!")
            return redirect('/maximize-products')
        
        # Preços dos produtos por unidade
        variable_prices = [
            float(product.price_total) for product in products
        ]

        # Restrições da categoria e os tipos
        restrictions = category.restrictions
        restriction_units = [
            r.unit_type for r in restrictions
        ]
        available_restrictions = [
            float(r.quantity_available) for r in restrictions
        ]

        # Matriz de restrições necessárias (produtos x insumos)
        necessary_restrictions = []
        for restriction in restrictions:
            restriction_row = []

            for product in products:
                # Busca a quantidade usada deste insumo no produto
                pr = ProductRestriction.query.filter_by(
                    product_id=product.id,
                    restriction_id=restriction.id
                ).first()
                restriction_row.append(float(pr.quantity_used) if pr else 0.0)

            necessary_restrictions.append(restriction_row)

        # Agora monta o problema de maximização
        prob = pulp.LpProblem('Maximize_Production', pulp.LpMaximize)
        
        # Variáveis de decisão (quantidade de cada produto a produzir)
        x = [
            pulp.LpVariable(f"x{product.id}", lowBound=0, cat='Continuous')
            for product in products
        ]
        
        # Função objetivo de maximizar o lucro
        prob += pulp.lpSum([
            variable_prices[i] * x[i] for i in range(len(products))
        ]), "Total_Profit"
        
        # Restrições (não ultrapassa insumos disponíveis)
        for i in range(len(restrictions)):
            prob += pulp.lpSum([
                necessary_restrictions[i][j] * x[j] for j in range(len(products))
            ]) <= available_restrictions[i], f"Restriction_{restrictions[i].name}"
        
        # Resolver o problema
        prob.solve()
        
        # Processar resultados
        if prob.status != pulp.LpStatusOptimal:
            flash("Não foi possível encontrar uma solução ótima com os recursos disponíveis.")
            return redirect('/maximize-products')
        
        # Obtem valores ótimos
        quantities = [round(pulp.value(var) or 0, 2) for var in x]
        gross_profit = round(pulp.value(prob.objective) or 0, 2)
        
        # Calcular uso de insumos
        used_restrictions = []
        for i in range(len(restrictions)):
            total = sum(quantities[j] * necessary_restrictions[i][j] for j in range(len(products)))
            total = min(total, available_restrictions[i])  # Nunca passa do disponível
            used_restrictions.append(round(total, 2))

        # Preparar dados para o template de resultados
        products_data = []
        for i, product in enumerate(products):
            products_data.append({
                'id': product.id,
                'name': product.name,
                'price': float(product.price_total),
                'quantity': int(quantities[i]),
                'total': round(float(product.price_total) * quantities[i], 2)
            })
        
        restrictions_data = []
        for i, restriction in enumerate(restrictions):
            restrictions_data.append({
                'name': restriction.name,
                'available': available_restrictions[i],
                'used': used_restrictions[i],
                'unit': restriction.unit_type
            })

        chart_data = {
            'product_names': [product['name'] for product in products_data],
            'quantities': [product['quantity'] for product in products_data],
            'prices': [product['price'] for product in products_data],
            'restrictions': [r['name'] for r in restrictions_data],
            'available_restrictions': [r['available'] for r in restrictions_data],
            'used_restrictions': [r['used'] for r in restrictions_data],
            'restriction_units': [r['unit'] for r in restrictions_data],
        }

        # Cálculo do custo fixo proporcional ao tempo de produção
        total_fixed_costs = sum(
            (fc.price_month / Decimal('30')) * Decimal(category.days_production)
            for fc in FixedCost.query.all()
        ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # Custo variável total (insumos)
        total_variable_costs = Decimal('0.00')
        for i, product in enumerate(products):
            quantity = Decimal(str(quantities[i]))
            restrictions_used = ProductRestriction.query.filter_by(product_id=product.id).all()
            for ru in restrictions_used:
                if ru.restriction and ru.restriction.unit_price:
                    unit_price = Decimal(str(ru.restriction.unit_price))
                    total_variable_costs += unit_price * Decimal(str(ru.quantity_used)) * quantity

        total_variable_costs = total_variable_costs.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # Cálculo do lucro líquido
        net_profit = Decimal(str(gross_profit)) - total_fixed_costs
        net_profit = Decimal(str(net_profit)) - total_variable_costs
        net_profit = net_profit.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        return render_template('result.html', 
                            products=products_data,
                            restriction_units=restriction_units,
                            restrictions=restrictions_data,
                            gross_profit=gross_profit,
                            total_fixed_costs=total_fixed_costs,
                            total_variable_costs=total_variable_costs,
                            net_profit=net_profit,
                            category_name=category.name,
                            chart_data=chart_data,
                            flag_save=True
                )        

    except Exception as e:
        print(f"Erro: {str(e)}")
        flash("Ocorreu um erro ao calcular a maximização.")
        return redirect('/maximize-products')

@bp.route('/save', methods=['POST'])
def save():
    if not session.get('loggedin'):
        return redirect('/')

    try:
        gross_profit = float(request.form.get('gross_profit', 0))
        net_profit = float(request.form.get('net_profit', 0))
        total_fixed_costs = float(request.form.get('total_fixed_costs', 0))
        total_variable_costs = float(request.form.get('total_variable_costs', 0))
        product_ids = request.form.getlist('products_save[]')

        if not product_ids:
            flash("Nenhum produto selecionado para salvar!", "error")
            return redirect(request.referrer)

        # 1. Salvar na tabela results
        new_result = Result(
            user_id=session.get('id'),
            gross_profit=gross_profit,
            net_profit=net_profit,
            total_fixed_costs=total_fixed_costs,
            total_variable_costs=total_variable_costs
        )
        db.session.add(new_result)
        db.session.flush()  # Para obter new_result.id

        # 2. Salvar cada produto relacionado na tabela result_products
        for product_id in product_ids:
            quantity_str = request.form.get(f'quantity_{product_id}', '0')
            quantity = int(float(quantity_str))  # Garante inteiro

            product = Product.query.get(product_id)
            if product:
                total_value = round(float(product.price_total) * quantity, 2)
                new_result_product = ResultProduct(
                    result_id=new_result.id,
                    product_id=product.id,
                    quantity_production=quantity,
                    total_value=total_value
                )
                db.session.add(new_result_product)

        db.session.commit()
        flash("Resultados salvos com sucesso!", "success")
        return redirect('/maximize-products')

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao salvar resultados: {str(e)}")
        flash("Erro ao salvar resultados!", "error")
        return redirect(request.referrer)
