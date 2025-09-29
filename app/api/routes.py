"""
Rutas API principales del Gemini AI Chatbot.
"""

from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    send_from_directory,
    Response,
)
from datetime import datetime
import logging

from app.services.gemini_service import GeminiService
from app.core.decorators import rate_limit_decorator

# from app.core.cache import cache_manager  # Import no usado
from app.core.metrics import metrics_manager

logger = logging.getLogger(__name__)



# Blueprint para rutas principales
main_bp = Blueprint("main", __name__)
api_bp = Blueprint("api", __name__, url_prefix="/api")


# Endpoint /api/chat para test de autenticación
@api_bp.route("/chat", methods=["POST"])
def chat_api():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"success": False, "message": "No autorizado"}), 401
    data = request.get_json()
    return jsonify({"success": True, "message": "Mensaje recibido", "data": data}), 200


def register_api_routes(app):
    """Registrar todas las rutas API."""
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    # Registrar blueprint de autenticación
    from app.api.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    # Registrar ruta para archivos de prueba e2e en modo desarrollo
    @app.route('/tests/e2e/<path:filename>')
    def serve_e2e_test_files(filename):
        """Servir archivos de prueba e2e en modo desarrollo."""
        import os
        from flask import current_app, send_from_directory, Response
        
        # Obtener la ruta absoluta del directorio de pruebas e2e
        project_root = os.path.abspath(os.path.dirname(os.path.dirname(current_app.root_path)))
        tests_e2e_dir = os.path.join(project_root, 'tests', 'e2e')
        current_app.logger.info(f"Directorio de pruebas e2e: {tests_e2e_dir}")
        
        try:
            # Para archivos JavaScript, leer el contenido y devolverlo con el tipo MIME correcto
            if filename.endswith('.js'):
                with open(os.path.join(tests_e2e_dir, filename), 'r', encoding='utf-8') as f:
                    content = f.read()
                    return Response(content, mimetype='application/javascript')
            # Para otros archivos, usar send_from_directory
            return send_from_directory(tests_e2e_dir, filename)
        except Exception as e:
            current_app.logger.error(f"Error al servir archivo {filename}: {str(e)}")
            return jsonify({"error": f"No se pudo cargar el archivo: {str(e)}"}), 500


# Rutas principales
@main_bp.route("/")
def index():
    """Página principal."""
    return render_template("index.html")


@main_bp.route("/chat")
def chat():
    """Página del chat."""
    return render_template("chat.html")


@main_bp.route("/privacy_policy")
def privacy_policy():
    """Página de política de privacidad."""
    return render_template("privacy_policy.html")


# Rutas de utilidad
@main_bp.route("/manifest.json")
def manifest():
    """PWA manifest."""
    manifest_data = {
        "name": "Gemini AI Chatbot",
        "short_name": "Gemini Chat",
        "description": "Chatbot inteligente con Gemini AI",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#4285f4",
        "icons": [
            {
                "src": "/static/icon-192.png",
                "sizes": "192x192",
                "type": "image/png",
            },
            {
                "src": "/static/icon-512.png",
                "sizes": "512x512",
                "type": "image/png",
            },
        ],
    }
    return (
        jsonify(manifest_data),
        200,
        {"Content-Type": "application/manifest+json"},
    )


@main_bp.route("/sw.js")
def service_worker():
    """Service worker."""
    from flask import current_app
    import os

    # Obtener la ruta absoluta del directorio static del proyecto
    # (no app/static)
    project_root = os.path.dirname(current_app.root_path)
    static_dir = os.path.join(
        project_root,
        "static",
    )

    try:
        response = send_from_directory(
            static_dir,
            "sw.js",
        )
        response.headers["Content-Type"] = (
            "application/javascript"
        )
        response.headers["Cache-Control"] = "no-cache"
        response.headers["Service-Worker-Allowed"] = "/"
        return response
    except FileNotFoundError:
        # Si no se encuentra el archivo, devolver un Service Worker básico
        basic_sw = """
// Service Worker básico
console.log('Service Worker básico cargado');
    sitemap = (
        f"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        f"<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n"
        f"    <url>\n"
        f"        <loc>{base_url}/</loc>\n"
        f"        <lastmod>{current_date}</lastmod>\n"
        f"        <changefreq>weekly</changefreq>\n"
        f"        <priority>1.0</priority>\n"
        f"    </url>\n"
        f"    <url>\n"
        f"        <loc>{base_url}/chat</loc>\n"
        f"        <lastmod>{current_date}</lastmod>\n"
        f"        <changefreq>weekly</changefreq>\n"
        f"        <priority>0.8</priority>\n"
        f"    </url>\n"
        f"    <url>\n"
        f"        <loc>{base_url}/privacy_policy</loc>\n"
        f"        <lastmod>{current_date}</lastmod>\n"
        f"        <changefreq>monthly</changefreq>\n"
        f"        <priority>0.7</priority>\n"
        f"    </url>\n"
        f"    <url>\n"
        f"        <loc>{base_url}/manifest.json</loc>\n"
        f"        <lastmod>{current_date}</lastmod>\n"
        f"        <changefreq>monthly</changefreq>\n"
        f"        <priority>0.5</priority>\n"
        f"    </url>\n"
        f"</urlset>"
    )
    console.log('Service Worker instalado');
});
self.addEventListener('activate', event => {
    console.log('Service Worker activado');
});
"""
        response = current_app.response_class(
            basic_sw, mimetype="application/javascript"
        )
        response.headers["Content-Type"] = "application/javascript"
        response.headers["Cache-Control"] = "no-cache"
        response.headers["Service-Worker-Allowed"] = "/"
        return response


@main_bp.route("/robots.txt")
def robots_txt():
    """Robots.txt para SEO."""
    return (
        """User-agent: *\nAllow: /\nSitemap: /sitemap.xml""",
        200,
        {"Content-Type": "text/plain; charset=utf-8"},
    )


@main_bp.route("/sitemap.xml")
def sitemap_xml():
    """XML sitemap para SEO con soporte HTTPS."""
    # Determinar el protocolo y host base
    protocol = "https" if request.is_secure else "http"
    host = request.host
    base_url = f"{protocol}://{host}"

    # Fecha actual para lastmod
    current_date = datetime.now().strftime("%Y-%m-%d")

    sitemap = (
            f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f'    <url>\n'
            f'        <loc>{base_url}/</loc>\n'
            f'        <lastmod>{current_date}</lastmod>\n'
            f'        <changefreq>weekly</changefreq>\n'
            f'        <priority>1.0</priority>\n'
            f'    </url>\n'
            f'    <url>\n'
            f'        <loc>{base_url}/chat</loc>\n'
            f'        <lastmod>{current_date}</lastmod>\n'
            f'        <changefreq>weekly</changefreq>\n'
            f'        <priority>0.8</priority>\n'
            f'    </url>\n'
            f'    <url>\n'
            f'        <loc>{base_url}/privacy_policy</loc>\n'
            f'        <lastmod>{current_date}</lastmod>\n'
            f'        <changefreq>monthly</changefreq>\n'
            f'        <priority>0.7</priority>\n'
            f'    </url>\n'
            f'    <url>\n'
            f'        <loc>{base_url}/manifest.json</loc>\n'
            f'        <lastmod>{current_date}</lastmod>\n'
            f'        <changefreq>monthly</changefreq>\n'
            f'        <priority>0.5</priority>\n'
            f'    </url>\n'
            f'</urlset>'
        )

    return sitemap, 200, {"Content-Type": "application/xml; charset=utf-8"}


@main_bp.route("/favicon.ico")
def favicon():
    """Favicon."""
    from flask import current_app
    import os

    # Obtener la ruta absoluta del directorio static del proyecto
    project_root = os.path.dirname(current_app.root_path)
    static_dir = os.path.join(project_root, "static")

    try:
        response = send_from_directory(static_dir, "favicon.ico")
        response.headers["Content-Type"] = "image/x-icon"
        response.headers["Cache-Control"] = (
            "public, max-age=86400"  # Cache por 1 día
        )
        response.headers["Cache-Control"] = (
            "public, max-age=86400"  # Cache por 1 día
        )
        return response
    except FileNotFoundError:
        # Si no se encuentra, devolver 204 No Content
        from flask import Response

        return Response(status=204)


# Rutas API
@api_bp.route("/chat/send", methods=["POST"])
@rate_limit_decorator
def send_message():
    """Enviar mensaje al chatbot."""
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Mensaje requerido",
                        "error_code": "MISSING_MESSAGE",
                    }
                ),
                400,
            )

        user_message = data["message"].strip()

        # Validaciones de entrada
        if len(user_message) > 4000:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": (
                            "Mensaje demasiado largo "
                            "(máximo 4000 caracteres)"
                        ),
                        "error_code": "MESSAGE_TOO_LONG",
                    }
                ),
                400,
            )

        if not user_message:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Mensaje vacío",
                        "error_code": "EMPTY_MESSAGE",
                    }
                ),
                400,
            )

        # Procesar mensaje con Gemini
        gemini_service = GeminiService()
        result = gemini_service.generate_response(user_message)

        return jsonify(result)
    except Exception:
        logger.error("Error en send_message")
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Error interno del servidor",
                    "error_code": "INTERNAL_ERROR",
                }
            ),
            500,
        )

    # Mock endpoint para subida de archivos
@api_bp.route("/upload", methods=["POST"])
def upload():
    # Simular respuesta sin autenticación
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"success": False, "message": "No autorizado"}), 401
    return jsonify({"success": True, "message": "Archivo subido"}), 200

@api_bp.route("/health")
def health_check():
    """Health check endpoint con métricas."""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "metrics": metrics_manager.get_metrics(),
        }
    )


@api_bp.route("/metrics")
def get_metrics():
    """Endpoint para obtener métricas de rendimiento."""
    return jsonify(metrics_manager.get_metrics())


def create_basic_routes(app):
    """Crear rutas básicas si no existen blueprints."""

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/chat")
    def chat():
        return render_template("chat.html")
