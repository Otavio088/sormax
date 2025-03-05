from flask import Blueprint, render_template, request, session, redirect

bp = Blueprint('quantity', __name__)

@bp.route('/quantity', methods=['GET', 'POST'])
def variables():
    if not session.get('loggedin'):
        return redirect('/')

    if request.method == 'POST':
        session['optimization_type'] = request.form.get('optimization_type')
    
    if not session.get('optimization_type'):
        return redirect('/home')

    return render_template('quantity.html')