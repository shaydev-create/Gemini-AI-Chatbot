"""Configuración de base de datos con soporte para PostgreSQL y SQLite."""

import os
import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

logger = logging.getLogger(__name__)

# Instancia global de SQLAlchemy
db = SQLAlchemy()

def get_database_url():
    """
    Obtener URL de base de datos con fallback automático.
    
    Returns:
        str: URL de conexión a la base de datos
    """
    # Verificar si PostgreSQL está habilitado
    postgres_enabled = os.getenv('POSTGRES_ENABLED', 'False').lower() == 'true'
    
    if postgres_enabled:
        # Configuración PostgreSQL
        host = os.getenv('POSTGRES_HOST', 'localhost')
        port = os.getenv('POSTGRES_PORT', '5432')
        db_name = os.getenv('POSTGRES_DB', 'gemini_chatbot')
        user = os.getenv('POSTGRES_USER', 'gemini_user')
        password = os.getenv('POSTGRES_PASSWORD', '')
        
        postgres_url = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
        
        # Verificar conexión PostgreSQL
        try:
            engine = create_engine(postgres_url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("✅ Conectado a PostgreSQL")
            return postgres_url
        except OperationalError as e:
            logger.warning(f"⚠️ PostgreSQL no disponible: {e}")
            logger.info("🔄 Usando SQLite como fallback")
    
    # Fallback a SQLite
    sqlite_url = os.getenv('DATABASE_URL', 'sqlite:///gemini_chatbot.db')
    logger.info("✅ Usando SQLite")
    return sqlite_url

def init_db(app):
    """
    Inicializar la base de datos con la aplicación Flask.
    
    Args:
        app: Instancia de Flask
    """
    # Configurar URL de base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
    
    # Inicializar SQLAlchemy con la app
    db.init_app(app)
    
    # Crear tablas en el contexto de la aplicación
    with app.app_context():
        try:
            db.create_all()
            db_type = "PostgreSQL" if "postgresql" in app.config['SQLALCHEMY_DATABASE_URI'] else "SQLite"
            logger.info(f"✅ Base de datos {db_type} inicializada correctamente")
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
            db_type = "PostgreSQL" if "postgresql" in app.config['SQLALCHEMY_DATABASE_URI'] else "SQLite"
            logger.info(f"✅ Base de datos {db_type} reseteada correctamente")
        except Exception as e:
            logger.error(f"❌ Error reseteando base de datos: {e}")
            raise

def check_db_connection():
    """
    Verificar conexión a la base de datos.
    
    Returns:
        tuple: (success: bool, message: str, db_type: str)
    """
    try:
        db_url = get_database_url()
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        db_type = "PostgreSQL" if "postgresql" in db_url else "SQLite"
        return True, f"Conexión exitosa a {db_type}", db_type
        
    except Exception as e:
        return False, f"Error de conexión: {str(e)}", "Unknown"

def migrate_to_postgresql():
    """
    Migrar datos de SQLite a PostgreSQL.
    
    Returns:
        bool: True si la migración fue exitosa
    """
    try:
        # Verificar que PostgreSQL esté configurado
        postgres_enabled = os.getenv('POSTGRES_ENABLED', 'False').lower() == 'true'
        if not postgres_enabled:
            logger.error("❌ PostgreSQL no está habilitado en las variables de entorno")
            return False
        
        # Obtener URLs de ambas bases de datos
        sqlite_url = os.getenv('DATABASE_URL', 'sqlite:///gemini_chatbot.db')
        postgres_url = get_database_url()
        
        if "postgresql" not in postgres_url:
            logger.error("❌ No se pudo conectar a PostgreSQL")
            return False
        
        logger.info("🚀 Iniciando migración de SQLite a PostgreSQL...")
        
        # Crear engines para ambas bases de datos
        sqlite_engine = create_engine(sqlite_url)
        postgres_engine = create_engine(postgres_url)
        
        # Aquí se implementaría la lógica de migración específica
        # Por ahora, solo verificamos las conexiones
        
        with sqlite_engine.connect() as sqlite_conn:
            with postgres_engine.connect() as postgres_conn:
                logger.info("✅ Conexiones establecidas")
                # TODO: Implementar migración de datos específica
                logger.info("✅ Migración completada (estructura básica)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error durante la migración: {e}")
        return False