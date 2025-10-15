"""
Inicialización de las extensiones de Flask para evitar importaciones circulares.
"""

from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
socketio = SocketIO()
