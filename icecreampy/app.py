from flask import Flask
import os
from dotenv import load_dotenv
from icecreampy.ext import database
from icecreampy.views import index, autentication, user_registration, home, products_registration, quantity, names, values, calculate

load_dotenv(override=True)

print("DATABASE_URI:", os.getenv('DATABASE_URI'))
app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')

database.init_app(app)

app.register_blueprint(index.bp)
app.register_blueprint(autentication.bp)
app.register_blueprint(user_registration.bp)
app.register_blueprint(home.bp)
app.register_blueprint(products_registration.bp)

app.register_blueprint(quantity.bp)
app.register_blueprint(names.bp)
app.register_blueprint(values.bp)
app.register_blueprint(calculate.bp)


if __name__ == '__main__':
    app.run(debug=True)
