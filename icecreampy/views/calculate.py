from flask import Blueprint, flash, render_template, request, session, redirect
from icecreampy.models.category import Category
from icecreampy.models.products import Product
from icecreampy.models.products_restrictions import ProductRestriction
from icecreampy.models.result import Result
from icecreampy.models.result_products import ResultProduct
from icecreampy.ext.database import db
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
            float(product.price) for product in products
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
        max_profit = round(pulp.value(prob.objective) or 0, 2)
        
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
                'price': float(product.price),
                'quantity': int(quantities[i]),
                'total': round(float(product.price) * quantities[i], 2)
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

        return render_template('result.html', 
                            products=products_data,
                            restriction_units=restriction_units,
                            restrictions=restrictions_data,
                            max_profit=max_profit,
                            category_name=category.name,
                            chart_data=chart_data,
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
        max_profit = float(request.form.get('max_profit', 0))
        product_ids = request.form.getlist('products_save[]')

        if not product_ids:
            flash("Nenhum produto selecionado para salvar!", "error")
            return redirect(request.referrer)

        # 1. Salvar na tabela results
        new_result = Result(
            id_user=session.get('id'),
            result=max_profit
        )
        db.session.add(new_result)
        db.session.flush()  # Para obter new_result.id

        # 2. Salvar cada produto relacionado na tabela result_products
        for product_id in product_ids:
            quantity_str = request.form.get(f'quantity_{product_id}', '0')
            quantity = int(float(quantity_str))  # Garante inteiro

            product = Product.query.get(product_id)
            if product:
                total_value = round(float(product.price) * quantity, 2)
                new_result_product = ResultProduct(
                    id_result=new_result.id,
                    id_product=product.id,
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
