"""
Configuración de base de datos.
"""

import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger(__name__)

# Instancia global de SQLAlchemy
db = SQLAlchemy()

def init_db(app):
    """
    Inicializar la base de datos con la aplicación Flask.
    
    Args:
        app: Instancia de Flask
    """
    # Inicializar SQLAlchemy con la app
    db.init_app(app)
    
    # Crear tablas en el contexto de la aplicación
    with app.app_context():
        try:
            db.create_all()
            logger.info("✅ Base de datos inicializada correctamente")
        except Exception as e:
            logger.error(f"❌ Error inicializando base de datos: {e}")
            # Continuar sin base de datos para desarrollo básico
            pass

def reset_db(app):
    """
    Resetear la base de datos (eliminar y recrear todas las tablas).
    
    Args:
        app: Instancia de Flask
    """
    with app.app_context():
        try:
            db.drop_all()
            db.create_all()
            logger.info("✅ Base de datos reseteada correctamente")
        except Exception as e:
            logger.error(f"❌ Error reseteando base de datos: {e}")
            raise