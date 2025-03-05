from flask import Blueprint, render_template, request, session, redirect

bp = Blueprint('names', __name__)

@bp.route('/names', methods=['POST', 'GET'])
def informations():
    if not session.get('loggedin'):
        return redirect('/')

    if request.method == 'POST':
        session['num_variables'] = int(request.form.get('num_variables'))
        session['num_restrictions'] = int(request.form.get('num_restrictions'))

    if not session.get('num_variables'):
        return redirect('/quantity')

    return render_template('names.html')