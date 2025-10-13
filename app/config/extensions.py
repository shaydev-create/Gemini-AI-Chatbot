"""
Inicialización de las extensiones de Flask para evitar importaciones circulares.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO

db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()
