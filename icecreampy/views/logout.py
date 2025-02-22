from flask import Blueprint, redirect, session

bp = Blueprint('logout', __name__)

@bp.route('/logout')
def logout():
    session.clear()

    return redirect('/')