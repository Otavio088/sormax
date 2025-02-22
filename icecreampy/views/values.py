from flask import Blueprint, render_template, request, session

bp = Blueprint('values', __name__)

@bp.route('/values', methods=['GET', 'POST'])
def values():
    if request.method == 'POST':
        session['variable_names'] = [request.form.get(f'variable{i}', f'{i+1}') for i in range(session['num_variables'])]
        session['restriction_names'] = [request.form.get(f'restriction{i}', f'{i+1}') for i in range(session['num_restrictions'])]

    return render_template('values.html')