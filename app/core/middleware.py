"""
Middleware personalizado para el Gemini AI Chatbot.
"""

import logging
import time

from flask import g, request
from flask_wtf.csrf import CSRFProtect

from app.core.metrics import metrics_manager

logger = logging.getLogger(__name__)


def setup_middleware(app):
    """Configurar middleware personalizado."""
    # ProtecciÃ³n CSRF
    csrf = CSRFProtect(app)
    app.logger.info("CSRF protection enabled")

    # Eximir rutas API especÃ­ficas de la protecciÃ³n CSRF
    @csrf.exempt
    def csrf_exempt_api_routes():
        pass

    # Eximir la ruta /api/chat/send de la protecciÃ³n CSRF
    @app.before_request
    def exempt_api_routes():
        if request.path == "/api/chat/send" and request.method == "POST":
            csrf.protect_csrf = False

    @app.before_request
    def before_request():
        """Ejecutar antes de cada request."""
        g.start_time = time.time()

        # Log del request
        logger.info(
            f"Request: {request.method} {request.path} from {request.remote_addr}"



        )

        # Incrementar contador de requests
        metrics_manager.increment_counter("total_requests")

        # Log especÃ­fico para API
        if request.path.startswith("/api/"):
            metrics_manager.increment_counter("api_requests")

    @app.after_request
    def after_request(response):
        """Ejecutar despuÃ©s de cada request."""
        # Calcular tiempo de respuesta
        if hasattr(g, "start_time"):
            response_time = time.time() - g.start_time
            metrics_manager.record_response_time(response_time)

            # Log del response
            logger.info(
                f"Response: {response.status_code} in {response_time:.3f}s"


            )

        # Headers de seguridad adicionales
        response.headers["X-Request-ID"] = request.headers.get(
            "X-Request-ID", "unknown"
        )
        # Cabeceras de seguridad para XSS
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; img-src 'self' data:;"
        )
        response.headers["X-XSS-Protection"] = "1; mode=block"

        return response

    @app.teardown_appcontext
    def teardown_db(error):
        """Limpiar contexto de aplicaciÃ³n."""
        if error:
            logger.error(f"Application context error: {error}")


def setup_error_handlers(app):
    """Configurar manejadores de errores personalizados."""

    @app.errorhandler(404)
    def not_found(error):
        """Manejar errores 404."""
        logger.warning(f"404 error: {request.path}")
        return {
            "error": "Recurso no encontrado",
            "status_code": 404,
            "path": request.path,
        }, 404

    @app.errorhandler(500)
    def internal_error(error):
        """Manejar errores 500."""
        original_exception = getattr(error, "original_exception", error)
        logger.error(f"500 error: {original_exception}")
        return {"error": "Error interno del servidor", "status_code": 500}, 500

    @app.errorhandler(429)
    def rate_limit_error(error):
        """Manejar errores de rate limiting."""
        logger.warning(f"Rate limit exceeded from {request.remote_addr}")
        return {
            "error": "Demasiadas solicitudes. Intenta mÃ¡s tarde.",
            "status_code": 429,
            "retry_after": 60,
        }, 429
