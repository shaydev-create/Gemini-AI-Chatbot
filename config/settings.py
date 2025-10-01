"""
Configuración centralizada de la aplicación.
"""

import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class Config:
    """Configuración base de la aplicación."""

    # Configuración básica
    SECRET_KEY = os.getenv('SECRET_KEY', 'tu-clave-secreta-aqui')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = False

    # Configuración de servidor
    HOST = os.getenv('HOST', '127.0.0.1')
    PORT = int(os.getenv('PORT', 8080))
    USE_HTTPS = os.getenv('USE_HTTPS', 'True').lower() == 'true'

    # Configuración JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']

    # Configuración de base de datos
    DATABASE_URL = os.getenv(
        'DATABASE_URL',
        'postgresql://usuario:password@localhost:5432/gemini_chatbot')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Para desarrollo local, puedes usar SQLite: 'sqlite:///gemini_chatbot.db'
    # Para producción, usa PostgreSQL o MySQL
    # Migraciones automáticas: Flask-Migrate

    # Configuración de archivos
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'

    # Configuración de rendimiento
    SEND_FILE_MAX_AGE_DEFAULT = timedelta(hours=12)
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False

    # Configuración de compresión
    COMPRESS_MIMETYPES = [
        'text/html',
        'text/css',
        'text/xml',
        'text/javascript',
        'application/json',
        'application/javascript',
        'application/xml+rss',
        'application/atom+xml',
        'image/svg+xml'
    ]
    COMPRESS_LEVEL = 6
    COMPRESS_MIN_SIZE = 500

    # Configuración de API externa
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    GEMINI_API_KEY = os.getenv('GOOGLE_API_KEY')  # Alias para compatibilidad

    # Configuración de cache
    CACHE_EXPIRY = 3600  # 1 hora
    API_CACHE_EXPIRY = 1800  # 30 minutos
    MAX_CACHE_SIZE = 1000

    # Configuración de rate limiting
    RATE_LIMIT = 60  # requests per minute
    RATE_WINDOW = 60  # seconds

    # Configuración de logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    @staticmethod
    def init_app(app):
        """Inicializar configuración específica de la aplicación."""
        pass


class DevelopmentConfig(Config):
    """Configuración para desarrollo."""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Configuración para testing."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Configuración para producción."""
    DEBUG = False
    TESTING = False

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # Log de errores por email en producción
        import logging
        from logging.handlers import SMTPHandler

        if not app.debug and not app.testing:
            if app.config.get('MAIL_SERVER'):
                auth = None
                if app.config.get('MAIL_USERNAME') or app.config.get(
                        'MAIL_PASSWORD'):
                    auth = (
                        app.config.get('MAIL_USERNAME'),
                        app.config.get('MAIL_PASSWORD'))

                secure = None
                if app.config.get('MAIL_USE_TLS'):
                    secure = ()

                mail_handler = SMTPHandler(
                    mailhost=(
                        app.config.get('MAIL_SERVER'),
                        app.config.get('MAIL_PORT')),
                    fromaddr=app.config.get('MAIL_DEFAULT_SENDER'),
                    toaddrs=app.config.get(
                        'ADMINS',
                        []),
                    subject='Gemini AI Chatbot Error',
                    credentials=auth,
                    secure=secure)
                mail_handler.setLevel(logging.ERROR)
                app.logger.addHandler(mail_handler)


# Mapeo de configuraciones
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
