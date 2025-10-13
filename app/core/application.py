import os
from flask import Flask
from flask_babel import Babel
from app.config.settings import DevelopmentConfig, ProductionConfig
from app.main import main as main_blueprint
from app.api.routes import api_bp as api_blueprint
from app.auth import auth as auth_blueprint
from app.config.extensions import db, migrate, socketio
from app.utils.translation_utils import register_translation_functions

def create_app(config_class=DevelopmentConfig):
    """
    Fábrica de aplicaciones para crear y configurar la instancia de la aplicación Flask.
    """
    app = Flask(__name__,
                template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates'),
                static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static'))

    # Cargar configuración
    if os.environ.get('FLASK_ENV') == 'production':
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')

    def get_locale():
        # Aquí puedes añadir lógica para seleccionar el idioma, por ejemplo, desde la sesión del usuario
        # o una cabecera HTTP. Por ahora, se fija a 'es'.
        return 'es'

    babel = Babel(app, locale_selector=get_locale)

    # Registrar blueprints
    app.register_blueprint(main_blueprint)
    app.register_blueprint(api_blueprint, url_prefix='/api')
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # Registrar funciones de traducción para Jinja2
    register_translation_functions(app)

    # Inicializar servicio de Gemini - VERSIÓN RESTAURADA
    try:
        from app.services.gemini_service import GeminiService
        
        # Usar la versión simple que funcionaba antes
        app.gemini_service = GeminiService()
        app.logger.info("Servicio de Gemini inicializado exitosamente.")
    except Exception as e:
        app.logger.warning(f"No se pudo inicializar el servicio de Gemini: {e}")
        app.gemini_service = None

    with app.app_context():
        # Crea las tablas de la base de datos si no existen
        db.create_all()

    app.logger.info("Aplicación creada y configurada exitosamente.")
    return app, socketio
