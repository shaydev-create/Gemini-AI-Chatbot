"""Configuración de base de datos con soporte para PostgreSQL y SQLite."""

import logging

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError, SQLAlchemyError

db = SQLAlchemy()
logger = logging.getLogger(__name__)


def init_db(app) -> None:
    """
    Inicializar la base de datos con la aplicación Flask.

    Esta función asume que la URL de la base de datos ya ha sido configurada
    en `app.config['SQLALCHEMY_DATABASE_URI']` a través de las clases
    de configuración en `settings.py`.

    Args:
        app: Instancia de Flask
    """
    try:
        db.init_app(app)
        logger.info("✅ Base de datos inicializada con la app Flask.")
    except Exception as e:
        logger.exception(f"❌ Error al inicializar la base de datos: {e}")
        raise


def reset_db(app) -> None:
    """
    Resetear la base de datos (eliminar y recrear todas las tablas).

    Args:
        app: Instancia de Flask
    """
    with app.app_context():
        try:
            db.drop_all()
            db.create_all()
            logger.info("✅ Base de datos reseteada (tablas eliminadas y creadas).")
        except SQLAlchemyError as e:
            logger.exception(
                f"❌ Error de SQLAlchemy al resetear la base de datos: {e}"
            )
            raise
        except Exception as e:
            logger.exception(f"❌ Error inesperado al resetear la base de datos: {e}")
            raise


def check_db_connection(db_url: str) -> tuple[bool, str]:
    """
    Verificar conexión a la base de datos.

    Args:
        db_url (str): URL de la base de datos a verificar.

    Returns:
        tuple: (success: bool, message: str)
    """
    engine = create_engine(db_url)
    try:
        with engine.connect() as _:
            logger.info(f"✅ Conexión exitosa a la base de datos: {db_url}")
            return True, "Conexión exitosa"
    except OperationalError as e:
        logger.error(f"❌ Error de conexión a la base de datos: {e}")
        return False, f"Error de conexión: {e}"
    except Exception as e:
        logger.error(f"❌ Error inesperado al conectar con la base de datos: {e}")
        return False, f"Error inesperado: {e}"
    finally:
        engine.dispose()


def migrate_to_postgresql() -> None:
    """
    Migrar datos de SQLite a PostgreSQL.

    Returns:
        bool: True si la migración fue exitosa
    """
    # Esta función ahora es más compleja de mantener sin get_database_url.
    # La migración de datos es un proceso delicado que debería ser un script
    # de gestión separado (ej. con Alembic o un script custom).
    # Por ahora, la deshabilitamos para no romper los tests.
    logger.warning("La función migrate_to_postgresql está deshabilitada temporalmente.")
    return False
