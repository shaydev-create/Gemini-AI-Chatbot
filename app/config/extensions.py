"""
Inicialización de las extensiones de Flask para evitar importaciones circulares.
"""

from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()
