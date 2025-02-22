from flask import Flask
import os, toml
from dotenv import load_dotenv
from icecreampy.ext import database
from icecreampy.views import index, autentication, logout, home, quantity, names, values, calculate

load_dotenv()
config = toml.load('settings.toml')

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY', config['flask']['secret_key'])

database.init_app(app, config)

app.register_blueprint(index.bp)
app.register_blueprint(autentication.bp)
app.register_blueprint(logout.bp)
app.register_blueprint(home.bp)
app.register_blueprint(quantity.bp)
app.register_blueprint(names.bp)
app.register_blueprint(values.bp)
app.register_blueprint(calculate.bp)


if __name__ == '__main__':
    app.run(debug=True)