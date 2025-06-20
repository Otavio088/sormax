from flask import Blueprint, request, redirect, session, render_template, flash
from icecreampy.models.fixed_costs import FixedCost
from icecreampy.ext.database import db

bp = Blueprint('costs', __name__)

@bp.route('/costs')
def costs():
    if not session.get('loggedin'):
        return redirect('/')

    costs = FixedCost.query.all()
    return render_template('costs.html', costs=[c.to_json() for c in costs])

@bp.route('/costs_save', methods=['POST'])
def save_costs():
    if not session.get('loggedin'):
        return redirect('/')

    try:
        ids = request.form.getlist('id[]')
        delete_ids = request.form.getlist('delete_id[]')
        names = request.form.getlist('name[]')
        prices = request.form.getlist('price_month[]')

        for del_id in delete_ids:
            cost = FixedCost.query.get(int(del_id))
            if cost:
                db.session.delete(cost)

        for i in range(len(names)):
            current_id = ids[i] if i < len(ids) else ''
            if current_id:
                cost = FixedCost.query.get(int(current_id))
                if cost:
                    cost.name = names[i]
                    cost.price_month = float(prices[i])
            else:
                cost = FixedCost(name=names[i], price_month=float(prices[i]))
                db.session.add(cost)

        db.session.commit()
        flash("Custos atualizados com sucesso!", "success")

    except Exception as e:
        print("Erro ao salvar custos:", str(e))
        flash("Erro ao salvar custos!", "error")

    return redirect('/costs')
