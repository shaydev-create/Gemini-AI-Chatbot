from typing import Any, Optional
"""
Módulo principal de la aplicación Gemini AI Chatbot.
"""

__version__: str = "1.0.0"
__author__: str = "Gemini AI Chatbot Team"

from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()
migrate=Migrate()
socketio=SocketIO()