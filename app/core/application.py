"""
Factory de aplicación Flask para el Gemini AI Chatbot.
Configuración modular y escalable.
"""

import os
import logging
from pathlib import Path
from flask import Flask
from flask_compress import Compress
from flask_jwt_extended import JWTManager

# Importaciones locales
from config.settings import Config
from config.database import init_db
from app.api import register_api_routes
from app.core.middleware import setup_middleware, setup_error_handlers

def create_app(config_class=Config):
    """
    Factory para crear la aplicación Flask.
    
    Args:
        config_class: Clase de configuración a usar
        
    Returns:
        Flask: Instancia de la aplicación configurada
    """
    # Obtener rutas de templates y static
    app_dir = Path(__file__).parent.parent
    template_dir = app_dir / 'templates'
    static_dir = app_dir / 'static'
    
    app = Flask(__name__,
                template_folder=str(template_dir),
                static_folder=str(static_dir))
    
    # Configuración
    app.config.from_object(config_class)
    
    # Configurar logging
    setup_logging(app)
    
    # Inicializar extensiones
    setup_extensions(app)
    
    # Registrar blueprints y rutas
    register_api_routes(app)
    
    # Configurar middleware
    setup_middleware(app)
    setup_error_handlers(app)
    
    # Configurar JWT
    setup_jwt(app)
    
    # Inicializar base de datos
    with app.app_context():
        try:
            init_db(app)
            app.logger.info("Base de datos inicializada correctamente")
        except Exception as e:
            app.logger.error(f"Error inicializando base de datos: {e}")
    
    app.logger.info("Aplicación Flask creada exitosamente")
    return app

def setup_logging(app):
    """Configurar sistema de logging."""
    if not app.debug and not app.testing:
        # Configuración para producción
        if app.config.get('LOG_FILE'):
            file_handler = logging.FileHandler(app.config['LOG_FILE'])
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Gemini AI Chatbot startup')

def setup_extensions(app):
    """Inicializar extensiones de Flask."""
    # Compresión
    Compress(app)
    
    # JWT
    jwt = JWTManager(app)
    
    app.logger.info("Extensiones inicializadas")

def setup_jwt(app):
    """Configurar JWT callbacks."""
    jwt = app.extensions.get('flask-jwt-extended')
    
    if jwt:
        @jwt.expired_token_loader
        def expired_token_callback(jwt_header, jwt_payload):
            return {
                'message': 'Token expirado',
                'error': 'token_expired'
            }, 401
        
        @jwt.invalid_token_loader
        def invalid_token_callback(error):
            return {
                'message': 'Token inválido',
                'error': 'invalid_token'
            }, 401
        
        @jwt.unauthorized_loader
        def missing_token_callback(error):
            return {
                'message': 'Token requerido',
                'error': 'authorization_required'
            }, 401