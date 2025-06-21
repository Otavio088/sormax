from flask import Flask
import os
from dotenv import load_dotenv
from icecreampy.ext import database
from icecreampy.views import index, autentication, user_registration, home, category_routes, costs, calculate, consult

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')

database.init_app(app)

app.register_blueprint(index.bp)
app.register_blueprint(autentication.bp)
app.register_blueprint(user_registration.bp)
app.register_blueprint(home.bp)
app.register_blueprint(category_routes.bp)
app.register_blueprint(costs.bp)
app.register_blueprint(calculate.bp)
app.register_blueprint(consult.bp)


if __name__ == '__main__':
    app.run(debug=True)
