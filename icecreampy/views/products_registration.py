from flask import Blueprint, render_template, session, redirect

bp = Blueprint('products_registration', __name__)

@bp.route('/register-products', methods=['GET', 'POST'])
def products_registration():
    if not session.get('loggedin'):
        return redirect('/')

    return render_template('register-products.html')

def register_category():
    return