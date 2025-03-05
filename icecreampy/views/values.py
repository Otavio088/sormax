from flask import Blueprint, render_template, request, session, redirect

bp = Blueprint('values', __name__)

@bp.route('/values', methods=['GET', 'POST'])
def values():
    if not session.get('loggedin'):
        return redirect('/')

    if request.method == 'POST':
        session['variable_names'] = [request.form.get(f'variable{i}', f'{i+1}') for i in range(session['num_variables'])]
        session['restriction_names'] = [request.form.get(f'restriction{i}', f'{i+1}') for i in range(session['num_restrictions'])]

    if not session.get('variable_names'):
        return redirect('/names')

    return render_template('values.html')