"""
Middleware personalizado para el Gemini AI Chatbot.
"""

from flask import request, g
import time
import logging

from app.core.metrics import metrics_manager

logger = logging.getLogger(__name__)

def setup_middleware(app):
    """Configurar middleware personalizado."""
    
    @app.before_request
    def before_request():
        """Ejecutar antes de cada request."""
        g.start_time = time.time()
        
        # Log del request
        logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")
        
        # Incrementar contador de requests
        metrics_manager.increment_counter('total_requests')
        
        # Log específico para API
        if request.path.startswith('/api/'):
            metrics_manager.increment_counter('api_requests')
    
    @app.after_request
    def after_request(response):
        """Ejecutar después de cada request."""
        # Calcular tiempo de respuesta
        if hasattr(g, 'start_time'):
            response_time = time.time() - g.start_time
            metrics_manager.record_response_time(response_time)
            
            # Log del response
            logger.info(f"Response: {response.status_code} in {response_time:.3f}s")
        
        # Headers de seguridad adicionales
        response.headers['X-Request-ID'] = request.headers.get('X-Request-ID', 'unknown')
        
        return response
    
    @app.teardown_appcontext
    def teardown_db(error):
        """Limpiar contexto de aplicación."""
        if error:
            logger.error(f"Application context error: {error}")

def setup_error_handlers(app):
    """Configurar manejadores de errores personalizados."""
    
    @app.errorhandler(404)
    def not_found(error):
        """Manejar errores 404."""
        logger.warning(f"404 error: {request.path}")
        return {
            'error': 'Recurso no encontrado',
            'status_code': 404,
            'path': request.path
        }, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Manejar errores 500."""
        logger.error(f"500 error: {error}")
        return {
            'error': 'Error interno del servidor',
            'status_code': 500
        }, 500
    
    @app.errorhandler(429)
    def rate_limit_error(error):
        """Manejar errores de rate limiting."""
        logger.warning(f"Rate limit exceeded from {request.remote_addr}")
        return {
            'error': 'Demasiadas solicitudes. Intenta más tarde.',
            'status_code': 429,
            'retry_after': 60
        }, 429