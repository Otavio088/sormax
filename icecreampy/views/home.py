from flask import Blueprint, render_template, session, redirect

bp = Blueprint('home', __name__)

@bp.route('/home', methods=['GET'])
def home():
    if not session.get('loggedin'):
        return redirect('/')
    
    keep_keys = {'loggedin', 'id', 'username'}

    session_keys = list(session.keys())

    for key in session_keys:
        if key not in keep_keys:
            session.pop(key)

    return render_template('home.html')