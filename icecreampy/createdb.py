# create_db.py

import os
import pymysql
from flask import Flask
from dotenv import load_dotenv
from urllib.parse import urlparse

from icecreampy.ext.database import db, init_app
import icecreampy.models  # Garante que os modelos sejam registrados

load_dotenv()  # Carrega variáveis do .env

def create_database():
    db_uri = os.getenv("DATABASE_URI")
    parsed = urlparse(db_uri)

    user = parsed.username
    password = parsed.password
    host = parsed.hostname or "localhost"
    db_name = parsed.path.lstrip('/')  # Remove barra inicial

    # Conecta ao MySQL sem banco selecionado
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        charset='utf8mb4',
        autocommit=True  # Garante que o CREATE DATABASE seja salvo
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            print(f"Banco de dados '{db_name}' criado com sucesso.")
    finally:
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
