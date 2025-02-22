from flask import Blueprint, render_template, request, session

bp = Blueprint('quantity', __name__)

@bp.route('/quantity', methods=['GET', 'POST'])
def variables():
    if request.method == 'POST':
        session['optimization_type'] = request.form.get('optimization_type')
    
    return render_template('quantity.html')