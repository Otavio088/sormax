from flask import Blueprint, flash, render_template, request, session, redirect, url_for
from icecreampy.ext.database import db
from icecreampy.models.result import Result
from icecreampy.models.result_products import ResultProduct
from icecreampy.models.products import Product

bp = Blueprint('consult', __name__)

@bp.route('/consult', methods=['GET'])
def consult():
    if not session.get('loggedin'):
        return redirect('/')

    try:
        results = db.session.query(Result).order_by(Result.id.desc()).all()
        results_data = []

        for index, result in enumerate(results, start=1):
            result_products = db.session.query(ResultProduct).filter_by(id_result=result.id).all()
            product_list = []

            for rp in result_products:
                product = db.session.get(Product, rp.id_product)
                if product:
                    product_list.append({
                        'name': product.name,
                        'quantity': rp.quantity_production,
                        'total_value': float(rp.total_value)
                    })

            results_data.append({
                'id': result.id,
                'name': f"Resultado",
                'profit': float(result.result),
                'products': product_list
            })

        return render_template('consult.html', results=results_data)

    except Exception as e:
        print("Erro ao buscar resultados:", str(e))
        flash("Erro ao carregar resultados!", "error")
        return redirect('/')

@bp.route('/result/<int:result_id>', methods=['GET'])
def view_result(result_id):
    if not session.get('loggedin'):
        return redirect('/')

    result = db.session.get(Result, result_id)
    if not result:
        flash("Resultado não encontrado", "error")
        return redirect('/consult')

    result_products = ResultProduct.query.filter_by(id_result=result.id).all()
    products_data = []
    product_ids = []

    for rp in result_products:
        product = db.session.get(Product, rp.id_product)
        if product:
            products_data.append({
                'id': product.id,
                'name': product.name,
                'price': float(product.price),
                'quantity': int(rp.quantity_production),
                'total': float(rp.total_value)
            })
            product_ids.append(product.id)

    category = None
    if product_ids:
        product = db.session.get(Product, product_ids[0])
        if product and product.restrictions:
            # Pega a primeira restrição associada ao produto
            first_restriction = product.restrictions[0].restriction
            if first_restriction:
                category = first_restriction.category

    restrictions = category.restrictions if category else []

    restrictions_data = []
    for restriction in restrictions:
        used = 0
        for p in products_data:
            product = db.session.get(Product, p['id'])
            rel = next((r for r in product.restrictions if r.restriction_id == restriction.id), None)
            if rel:
                used += rel.quantity_used * p['quantity']

        used = min(used, restriction.quantity_available)

        restrictions_data.append({
            'name': restriction.name,
            'available': float(restriction.quantity_available),
            'used': round(used, 2),
            'unit': restriction.unit_type
        })

    chart_data = {
        'product_names': [p['name'] for p in products_data],
        'quantities': [p['quantity'] for p in products_data],
        'prices': [p['price'] for p in products_data],
        'restrictions': [r['name'] for r in restrictions_data],
        'available_restrictions': [float(r['available']) for r in restrictions_data],
        'used_restrictions': [float(r['used']) for r in restrictions_data],
        'restriction_units': [r['unit'] for r in restrictions_data],
    }
    print('chart_data: ', chart_data)
    return render_template(
        'result.html',
        products=products_data,
        restriction_units=[r['unit'] for r in restrictions_data],
        restrictions=restrictions_data,
        max_profit=float(result.result),
        category_name=category.name,
        chart_data=chart_data,
    )

@bp.route('/delete-result/<int:result_id>', methods=['POST'])
def delete_result(result_id):
    if not session.get('loggedin'):
        return redirect('/login')

    try:
        # Deleta todos os ResultProduct associados
        ResultProduct.query.filter_by(id_result=result_id).delete()
        
        # Dleta o Result principal
        result = Result.query.get(result_id)
        if result:
            db.session.delete(result)
            db.session.commit()
            
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao deletar resultado: {str(e)}", "error")
        print(f"Erro ao deletar resultado: {str(e)}")
    
    return redirect('/consult')