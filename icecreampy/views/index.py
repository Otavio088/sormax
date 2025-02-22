from flask import Blueprint, render_template

bp = Blueprint('index', __name__)

@bp.route('/', methods=['GET'])
def auth():
    return render_template('index.html')