import mysql.connector
import os
from flask import Flask
from dotenv import load_dotenv

from icecreampy.ext.database import db, init_app
import icecreampy.models  # importa todos os modelos para registrar

load_dotenv()  # Carrega as variáveis do .env

def create_database():
    db_uri = os.getenv('DATABASE_URI')
    db_name = db_uri.split('/')[-1].split('?')[0]

    connection = mysql.connector.connect(
        host='localhost',
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    cursor = connection.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    print(f"Banco de dados '{db_name}' criado/verificado com sucesso.")
    cursor.close()
    connection.close()

def create_tables():
    app = Flask(__name__)
    init_app(app)

    with app.app_context():
        db.create_all()
        print("Tabelas criadas com sucesso.")

if __name__ == '__main__':
    create_database()
    create_tables()
