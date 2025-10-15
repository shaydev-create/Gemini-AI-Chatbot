import logging
import os
from datetime import timedelta
from pathlib import Path
from typing import Any, Optional

# Configuración del logger
logger=logging.getLogger(__name__)

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """Configuración base de la que heredan todas las demás."""

    # Clave secreta para proteger sesiones y cookies.
    # Es vital que esta clave sea segura y no se exponga.
    # Se lee de una variable de entorno para mayor seguridad.
    SECRET_KEY: str = os.environ.get("SECRET_KEY")

    # Desactiva el seguimiento de modificaciones de SQLAlchemy para mejorar el rendimiento.
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # Carpeta para subir archivos.
    UPLOAD_FOLDER: str = str(BASE_DIR / "uploads")

    # Directorio para archivos de log.
    LOG_DIR: str = str(BASE_DIR / "logs")

    # Habilita la protección contra CSRF en los formularios.
    WTF_CSRF_ENABLED: bool = True

    # Clave de API para el servicio Gemini de Google.
    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY")

    # Modelo de Gemini a utilizar por defecto.
    GEMINI_MODEL: str = "gemini-flash-latest"

    # Modelo de visión de Gemini.
    GEMINI_VISION_MODEL: str = os.environ.get("GEMINI_VISION_MODEL")

    # Límites de tasa de solicitudes por defecto.
    RATE_LIMIT_DEFAULT: str = os.environ.get(
        "RATE_LIMIT_DEFAULT", "200 per day;50 per hour"
    )

    # Configuración de cookies de sesión para mayor seguridad.
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SECURE: bool = False  # En desarrollo es False
    SESSION_COOKIE_SAMESITE: str = "Lax"

    # Duración de la sesión permanente.
    PERMANENT_SESSION_LIFETIME: timedelta = timedelta(days=7)

    # Configuración de JWT
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY", "default-jwt-secret-key")
    JWT_TOKEN_LOCATION: list[str] = ["headers"]
    JWT_HEADER_NAME: str = "Authorization"
    JWT_HEADER_TYPE: str = "Bearer"
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(hours=1)

    @staticmethod
    def init_app(app) -> None:
        """Método para inicializaciones específicas de la app."""
        pass


class DevelopmentConfig(Config):
    """Configuración para el entorno de desarrollo."""

    import secrets

    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "DEV_DATABASE_URL"
    ) or "sqlite:///./fresh_gemini_dev.db"

    # En desarrollo, si no se define una SECRET_KEY, se genera una temporal.
    # Esto es conveniente para desarrollo local pero invalida las sesiones al reiniciar.
    if not Config.SECRET_KEY:
        SECRET_KEY: str = secrets.token_hex(16)
        logger.warning(
            "⚠️ La SECRET_KEY no estaba definida. Se ha generado una clave temporal. "
            "Las sesiones se invalidarán al reiniciar la aplicación."
        )


class TestingConfig(Config):
    """Configuración para el entorno de pruebas."""

    TESTING: bool = True
    SECRET_KEY: str = os.environ.get(
        "TEST_SECRET_KEY", "test-secret-key-change-in-production"
    )
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED: bool = False
    # ID de proyecto de Vertex AI para los tests.
    VERTEXAI_PROJECT_ID: str = os.environ.get("TEST_PROJECT_ID", "test-project-id")
    # Desactivar límites de tasa en tests.
    RATE_LIMIT_ENABLED: bool = False


class ProductionConfig(Config):
    """Configuración para el entorno de producción."""

    # En producción, la URL de la base de datos debe estar definida.
    SQLALCHEMY_DATABASE_URI: str = os.environ.get("DATABASE_URL")

    # En producción, las cookies de sesión deben ser seguras.
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_SAMESITE: str = "Strict"

    def __init__(self) -> None:
        """Asegura que las variables críticas de entorno estén definidas en producción."""
        super().__init__()
        if not self.SECRET_KEY:
            raise ValueError(
                "❌ No se ha configurado la SECRET_KEY en el entorno de producción."
            )
        if not self.SQLALCHEMY_DATABASE_URI:
            raise ValueError(
                "❌ No se ha configurado la DATABASE_URL en el entorno de producción."
            )


# Diccionario para acceder a las configuraciones por nombre.
config: dict[str, type[Config]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}