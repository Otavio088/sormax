from flask import Blueprint, redirect, render_template, session

bp = Blueprint('index', __name__)

@bp.route('/', methods=['GET'])
def open():
    if session.get('loggedin'):
        return redirect('/home')

    return render_template('index.html')