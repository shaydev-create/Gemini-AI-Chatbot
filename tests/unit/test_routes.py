from unittest.mock import patch

import pytest

from app.core.application import get_flask_app


@pytest.fixture
def app():
    """Crea una instancia de una aplicación Flask para pruebas de rutas."""
    import os
    from unittest.mock import MagicMock, patch

    # Set test environment variables to avoid GeminiService initialization errors
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
        app = get_flask_app("testing")

        # Mock the GeminiService instance that was created during app initialization
        mock_service = MagicMock()

        # Crear una corutina mock para el método asíncrono
        async def mock_generate_response(*args, **kwargs):
            return "Mocked response"

        mock_service.generate_response = mock_generate_response
        app.gemini_service = mock_service

        return app


@pytest.fixture
def client(app):
    """Un cliente de prueba para la aplicación Flask."""
    return app.test_client()


# --- Pruebas para Rutas Principales (main_bp) ---


def test_index_route(client):
    """Prueba que la ruta principal '/' renderiza la plantilla correcta."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Gemini AI Chatbot" in response.data.decode("utf-8")


def test_chat_route(client):
    """Prueba que la ruta '/chat' renderiza la plantilla de chat."""
    response = client.get("/chat")
    assert response.status_code == 200
    assert "Gemini AI Chat" in response.data.decode("utf-8")


def test_privacy_policy_route(client):
    """Prueba que la ruta '/privacy_policy_es' renderiza la política de privacidad."""
    response = client.get("/privacy_policy_es")
    assert response.status_code == 200
    assert "Política de Privacidad" in response.data.decode("utf-8")


# --- Pruebas para Rutas de Utilidad (main_bp) ---


def test_manifest_route(client):
    """Prueba que la ruta '/static/manifest.json' devuelve un JSON válido."""
    response = client.get("/static/manifest.json")
    assert response.status_code == 200
    assert response.content_type == "application/json"
    data = response.get_json()
    assert "name" in data


def test_robots_txt_route(client):
    """Prueba que la ruta '/static/robots.txt' devuelve texto plano."""
    response = client.get("/static/robots.txt")
    assert response.status_code == 200
    assert response.content_type == "text/plain; charset=utf-8"
    assert b"User-agent: *" in response.data


def test_sitemap_xml_route(client):
    """Prueba que la ruta '/static/sitemap.xml' devuelve XML."""
    response = client.get("/static/sitemap.xml")
    assert response.status_code == 200
    assert response.content_type == "text/xml; charset=utf-8"


@patch("app.main.routes.send_from_directory")
def test_favicon_route(mock_send, app):
    """Prueba que la ruta '/favicon.ico' intenta servir el archivo."""
    # El mock debe devolver un objeto Response para que se puedan añadir cabeceras
    mock_send.return_value = app.response_class("favicon content", mimetype="image/x-icon")
    client = app.test_client()
    response = client.get("/favicon.ico")
    assert response.status_code == 200
    assert response.data == b"favicon content"
    assert response.headers["Content-Type"] == "image/x-icon"


def test_favicon_not_found(client):
    """Prueba que la ruta '/favicon.ico' devuelve el contenido correcto."""
    response = client.get("/favicon.ico")
    assert response.status_code == 200
    assert response.content_type == "image/x-icon"  # Flask detecta la extensión .ico


# --- Pruebas para Rutas API (api_bp) ---


def test_chat_api_authorized(client):
    """Prueba el endpoint /api/chat/send con autorización."""
    response = client.post(
        "/api/chat/send",
        headers={"Authorization": "Bearer test-token"},
        json={"message": "test"},
    )
    assert response.status_code == 200
    assert "response" in response.json
    assert "session_id" in response.json


def test_chat_api_unauthorized(client):
    """Prueba el endpoint /api/chat/send sin autorización."""
    response = client.post("/api/chat/send", json={"message": "test"})
    assert response.status_code == 200  # Authentication is optional, not required
    assert "response" in response.json
    assert "session_id" in response.json


def test_send_message_success(client, app):
    """Prueba el envío de un mensaje exitoso a /api/chat/send."""

    # Configurar el mock del servicio en la configuración de la app
    from unittest.mock import MagicMock

    mock_service = MagicMock()
    mock_service.generate_response.return_value = "Hola, soy Gemini."

    with app.test_request_context():
        app.config["GEMINI_SERVICE"] = mock_service
        response = client.post("/api/chat/send", json={"message": "Hola"})
        assert response.status_code == 200
        assert response.json["response"] == "Hola, soy Gemini."
        assert "session_id" in response.json


def test_send_message_missing_data(client):
    """Prueba el envío sin datos a /api/chat/send."""
    response = client.post("/api/chat/send", json={})
    assert response.status_code == 400
    assert "message" in response.json
    assert "El campo 'message' es requerido." in response.json["message"]


def test_send_message_empty_message(client):
    """Prueba el envío de un mensaje vacío a /api/chat/send."""
    response = client.post("/api/chat/send", json={"message": "  "})
    assert response.status_code == 400
    assert "message" in response.json
    assert "El mensaje no puede estar vacío." in response.json["message"]


def test_send_message_too_long(client):
    """Prueba el envío de un mensaje demasiado largo a /api/chat/send."""
    long_message = "a" * 4001
    response = client.post("/api/chat/send", json={"message": long_message})
    assert response.status_code == 400
    assert "message" in response.json
    assert "El mensaje excede el límite de 4000 caracteres." in response.json["message"]


def test_send_message_internal_error(client, app):
    """Prueba el manejo de un error interno en /api/chat/send."""

    # Configurar el mock del servicio para que lance una excepción
    from unittest.mock import MagicMock

    mock_service = MagicMock()
    mock_service.generate_response.side_effect = Exception("Internal Error")

    with app.test_request_context():
        app.config["GEMINI_SERVICE"] = mock_service
        response = client.post("/api/chat/send", json={"message": "Hola"})
        assert response.status_code == 500
        assert "message" in response.json
        assert "Error interno al procesar la solicitud." in response.json["message"]


def test_upload_authorized(client):
    """Prueba el endpoint /api/upload con autorización (no implementado)."""
    response = client.post("/api/upload", headers={"Authorization": "Bearer test-token"})
    assert response.status_code == 404


def test_upload_unauthorized(client):
    """Prueba el endpoint /api/upload sin autorización (no implementado)."""
    response = client.post("/api/upload")
    assert response.status_code == 404


def test_health_check_route(app, client):
    """Prueba que la ruta /api/health funciona correctamente."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "metrics" in data
    assert "uptime_seconds" in data["metrics"]


def test_get_metrics_route(app, client):
    """Prueba que la ruta /api/metrics funciona correctamente (no implementado)."""
    response = client.get("/api/metrics")
    assert response.status_code == 404
