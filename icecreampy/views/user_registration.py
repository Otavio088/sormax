from flask import Blueprint, flash, redirect, render_template, request, session
from icecreampy.models.accounts import Account
from icecreampy.ext.database import db
import hashlib

bp = Blueprint('user_registration', __name__)

@bp.route('/register-user', methods=['GET'])
def open():
    if session.get('loggedin'):
        return redirect('/home')

    return render_template('register-user.html')

@bp.route('/validation', methods=['POST'])
def register():
    if (request.method == 'POST'):
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        passwordconfirm = request.form.get('passwordconfirm')

        if password != passwordconfirm:
            flash('Senhas incompatíveis!')
            return redirect('/register-user')

        existing_user = Account.query.filter_by(username=username)

        if existing_user:
            flash('Nome de usuário já utilizado!')
            return redirect('/register-user')

        hash = hashlib.sha256(password.encode()).hexdigest()
        
        user = Account(username=username, password=hash, email=email)

        db.session.add(user)
        db.session.commit()

        flash('Usuário Cadastrado com sucesso!')
        return redirect('/register-user')

    return redirect('/')
