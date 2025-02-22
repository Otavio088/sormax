from flask import Blueprint, render_template, request, redirect, session, flash
from icecreampy.models.accounts import accounts
from icecreampy.ext.database import db
import hashlib

bp = Blueprint('autentication', __name__)

@bp.route('/autentication', methods=['POST'])
def validation():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        hash = hashlib.sha256(password.encode()).hexdigest()

        user = accounts.query.filter_by(username = username, password = hash).first()

        if user:
            session['loggedin'] = True
            session['id'] = user.id
            session['username'] = user.username

            return redirect('/home')

        flash('Usuário ou senha incorretos!')
        return redirect('/')