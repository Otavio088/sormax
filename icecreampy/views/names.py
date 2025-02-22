from flask import Blueprint, render_template, request, session

bp = Blueprint('names', __name__)

@bp.route('/names', methods=['POST', 'GET'])
def informations():
    if request.method == 'POST':
        session['num_variables'] = int(request.form.get('num_variables'))
        session['num_restrictions'] = int(request.form.get('num_restrictions'))

    return render_template('names.html')