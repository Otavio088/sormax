from flask import Blueprint, request, redirect, session, render_template, flash
from icecreampy.models.fixed_costs import FixedCost
from icecreampy.ext.database import db
from icecreampy.models.fixed_costs import FixedCost

bp = Blueprint('costs', __name__)

@bp.route('/costs')
def costs():
    if not session.get('loggedin'):
        return redirect('/')
    
    costs = FixedCost.query.all()

    result = [cost.to_json() for cost in costs]
    
    return render_template('costs.html', costs=result)

@bp.route('/costs_save', methods=['POST'])
def save_costs():
    if not session.get('loggedin'):
        return redirect('/')

    try:
        ids = request.form.getlist('id[]')
        delete_ids = request.form.getlist('delete_id[]')
        names = request.form.getlist('name[]')
        unit_types = request.form.getlist('unit_type[]')
        quantities = request.form.getlist('quantity_available[]')
        prices = request.form.getlist('unit_price[]')

        # Deletar custos cujo id está em delete_ids
        for del_id in delete_ids:
            if del_id:
                cost = FixedCost.query.get(int(del_id))
                if cost:
                    db.session.delete(cost)

        for i in range(len(names)):
            current_id = ids[i] if i < len(ids) else ''

            # Aqui atualiza ou cria
            if current_id:
                cost = FixedCost.query.get(int(current_id))
                if cost:
                    cost.name = names[i]
                    cost.unit_type = unit_types[i]
                    cost.quantity_available = quantities[i]
                    cost.unit_price = prices[i]
            else:
                cost = FixedCost(
                    name=names[i],
                    unit_type=unit_types[i],
                    quantity_available=quantities[i],
                    unit_price=prices[i]
                )
                db.session.add(cost)

        db.session.commit()
        flash("Custos atualizados com sucesso!", "success")

    except Exception as e:
        print("Erro ao buscar resultados:", str(e))
        flash("Erro ao carregar resultados!", "error")
    
    return redirect('/costs')
