from flask import Blueprint, request, redirect, session, flash
from icecreampy.models.accounts import Account
import hashlib

bp = Blueprint('autentication', __name__)

@bp.route('/autentication', methods=['POST'])
def validation():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        hash = hashlib.sha256(password.encode()).hexdigest()

        user = Account.query.filter_by(username = username, password = hash).first()
        print('entrou!')
        if user:
            session['loggedin'] = True
            session['id'] = user.id
            session['username'] = user.username

            return redirect('/home')
        print('entrou!')
        flash('Usuário ou senha incorretos!')

    return redirect('/')

@bp.route('/logout')
def logout():
    session.clear()

    return redirect('/')