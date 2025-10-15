"""
Módulo principal de la aplicación Gemini AI Chatbot.
"""

from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

__version__: str = "1.0.0"
__author__: str = "Gemini AI Chatbot Team"

db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()

# Entry point para Vercel
from app.core.application import create_app

# Crear la aplicación para Vercel
app, socketio = create_app()

# Para compatibilidad con Vercel
if __name__ == "__main__":
    app.run(debug=False)
