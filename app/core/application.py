import os

from flask import Flask
from flask_babel import Babel

from app.api.admin import admin_bp as admin_blueprint
from app.api.auth import auth_bp as auth_blueprint
from app.api.routes import api_bp as api_blueprint
from app.config.extensions import db, jwt, migrate, socketio
from app.config.settings import DevelopmentConfig, ProductionConfig, TestingConfig
from app.main import main as main_blueprint
from app.utils.translation_utils import register_translation_functions


def create_app(config_class=DevelopmentConfig) -> None:
    """
    Fábrica de aplicaciones para crear y configurar la instancia de la aplicación Flask.
    """
    app = Flask(
        __name__,
        template_folder=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "templates"
        ),
        static_folder=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "static"
        ),
    )

    # Cargar configuración
    if os.environ.get("FLASK_ENV") == "production":
        app.config.from_object(ProductionConfig)
    elif os.environ.get("FLASK_ENV") == "testing":
        app.config.from_object(TestingConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    # Inicializar extensiones
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins="*", async_mode="threading")

    def get_locale() -> None:
        # Aquí puedes añadir lógica para seleccionar el idioma, por ejemplo, desde la sesión del usuario
        # o una cabecera HTTP. Por ahora, se fija a 'es'.
        return "es"

    _ = Babel(app, locale_selector=get_locale)

    # Registrar blueprints
    app.register_blueprint(main_blueprint)
    app.register_blueprint(api_blueprint, url_prefix="/api")
    app.register_blueprint(auth_blueprint, url_prefix="/auth")
    app.register_blueprint(admin_blueprint, url_prefix="/admin")

    # Registrar funciones de traducción para Jinja2
    register_translation_functions(app)

    # Inicializar servicio de Gemini - VERSIÓN RESTAURADA
    try:
        from app.services.gemini_service import GeminiService

        # Usar la versión simple que funcionaba antes
        # Usar app.config en lugar de atributo directo para mejor compatibilidad
        app.config["GEMINI_SERVICE"] = GeminiService()
        app.logger.info("Servicio de Gemini inicializado exitosamente.")
    except Exception as e:
        app.logger.warning(f"No se pudo inicializar el servicio de Gemini: {e}")
        app.config["GEMINI_SERVICE"] = None

    with app.app_context():
        # Crea las tablas de la base de datos si no existen
        db.create_all()

    app.logger.info("Aplicación creada y configurada exitosamente.")

    return app, socketio


def get_flask_app(config_class=DevelopmentConfig) -> None:
    """
    Devuelve solo la instancia Flask para pruebas (pytest, Flask test client).
    Acepta tanto clases de configuración como nombres de configuración (string).
    """
    # Si se pasa un string, buscar la clase de configuración correspondiente
    if isinstance(config_class, str):
        from app.config.settings import config

        config_class = config.get(config_class, DevelopmentConfig)

    app, _ = create_app(config_class)
    return app
