from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def init_app(app, config):
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #True
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', config['database']['uri'])
    db.init_app(app)