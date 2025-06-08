from flask import Blueprint, flash, render_template, request, session, redirect
from icecreampy.models.category import Category
from icecreampy.models.products import Product
from icecreampy.models.products_restrictions import ProductRestriction
import pulp

bp = Blueprint('calculate', __name__)

@bp.route('/calculate', methods=['POST', 'GET'])
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
