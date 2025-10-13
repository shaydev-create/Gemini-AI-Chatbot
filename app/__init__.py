"""
Módulo principal de la aplicación Gemini AI Chatbot.
"""

__version__ = "1.0.0"
__author__ = "Gemini AI Chatbot Team"

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO

db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()
