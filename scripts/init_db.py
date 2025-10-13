"""
Script para inicializar la base de datos con el contexto de la aplicación Flask.
"""
from app.core.application import create_app
from app.models import db

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()
    print("Base de datos inicializada correctamente.")
