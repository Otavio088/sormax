from flask_sqlalchemy import SQLAlchemy
import os

import sys

if sys.platform.startswith('win'):
    import pymysql
    pymysql.install_as_MySQLdb()

db = SQLAlchemy()

def init_app(app):
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #True
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    db.init_app(app)