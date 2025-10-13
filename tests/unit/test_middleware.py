from unittest.mock import patch

import pytest
from app.core.middleware import setup_error_handlers, setup_middleware
from flask import Flask, jsonify


@pytest.fixture
def app():
    """Crea una instancia de una aplicación Flask mínima para pruebas."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret"
    # Habilitamos CSRF globalmente, pero lo eximiremos en pruebas específicas
    app.config["WTF_CSRF_ENABLED"] = True

    # Rutas de prueba
    @app.route("/")
    def index():
        return "OK", 200

    @app.route("/api/chat/send", methods=["POST"])
    def chat_send():
        return jsonify({"status": "success"}), 200

    @app.route("/error")
    def error_route():
        raise ValueError("Test error")

    # Aplicar middleware y manejadores de errores
    setup_middleware(app)
    setup_error_handlers(app)

    return app


@pytest.fixture
def client(app):
    """Un cliente de prueba para la aplicación Flask."""
    return app.test_client()


# --- Pruebas para setup_middleware ---


@patch("app.core.middleware.metrics_manager")
def test_before_request_logic(mock_metrics, client):
    """Prueba que el middleware before_request funciona correctamente."""
    with patch("app.core.middleware.logger") as mock_logger:
        response = client.get("/")
        assert response.status_code == 200

        # Verificar que se registra el request
        mock_logger.info.assert_called()
        # Comprobamos la primera llamada, antes del log de after_request
        assert "Request: GET / from" in mock_logger.info.call_args_list[0][0][0]

        # Verificar que se incrementan las métricas
        mock_metrics.increment_counter.assert_called_with("total_requests")


@patch("app.core.middleware.metrics_manager")
def test_before_request_api_logic(mock_metrics, app):
    """Prueba que el middleware before_request funciona para rutas API."""
    # Deshabilitamos CSRF para esta prueba de API
    app.config["WTF_CSRF_ENABLED"] = False
    client = app.test_client()

    with patch("app.core.middleware.logger"):  # Silenciamos el logger
        response = client.post("/api/chat/send", json={"message": "hello"})
        assert response.status_code == 200

        # Verificar que se incrementan las métricas de API
        mock_metrics.increment_counter.assert_any_call("total_requests")
        mock_metrics.increment_counter.assert_any_call("api_requests")


@patch("app.core.middleware.metrics_manager")
def test_after_request_logic(mock_metrics, client):
    """Prueba que el middleware after_request añade cabeceras y registra métricas."""
    with patch("app.core.middleware.logger") as mock_logger:
        response = client.get("/")
        assert response.status_code == 200

        # Verificar cabeceras de seguridad
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert "default-src 'self'" in response.headers["Content-Security-Policy"]
        assert response.headers["X-XSS-Protection"] == "1; mode=block"

        # Verificar que se registra el tiempo de respuesta
        mock_metrics.record_response_time.assert_called_once()

        # Verificar log de respuesta
        mock_logger.info.assert_called()
        assert "Response: 200" in mock_logger.info.call_args_list[1][0][0]


def test_csrf_protection_exempt(app):
    """Prueba que la ruta /api/chat/send está exenta de protección CSRF."""
    # Deshabilitamos CSRF para esta prueba de API
    app.config["WTF_CSRF_ENABLED"] = False
    client = app.test_client()

    # Esta petición fallaría con 400 si CSRF estuviera activo sin un token
    response = client.post("/api/chat/send", json={"message": "hello"})
    assert response.status_code == 200
    assert response.json == {"status": "success"}


@patch("app.core.middleware.logger")
def test_teardown_db_with_error(mock_logger, app):
    """Prueba que el teardown registra un error si se produce."""
    with app.app_context():
        # Simular un error durante el teardown
        app.do_teardown_appcontext(ValueError("Teardown error"))

    mock_logger.error.assert_called_with("Application context error: Teardown error")


# --- Pruebas para setup_error_handlers ---


def test_404_not_found_handler(client):
    """Prueba el manejador de errores 404."""
    with patch("app.core.middleware.logger") as mock_logger:
        response = client.get("/non-existent-route")
        assert response.status_code == 404
        json_data = response.get_json()
        assert json_data["error"] == "Recurso no encontrado"
        assert json_data["status_code"] == 404

        # Verificar log
        mock_logger.warning.assert_called_with("404 error: /non-existent-route")


def test_500_internal_error_handler(app):
    """Prueba el manejador de errores 500."""
    # Forzamos que el manejador de excepciones de la app se use en lugar de propagar la excepción
    app.config["PROPAGATE_EXCEPTIONS"] = False
    client = app.test_client()

    with patch("app.core.middleware.logger") as mock_logger:
        response = client.get("/error")  # Esta ruta levanta una excepción
        assert response.status_code == 500
        json_data = response.get_json()
        assert json_data["error"] == "Error interno del servidor"
        assert json_data["status_code"] == 500

        # Verificar log
        mock_logger.error.assert_called_with("500 error: Test error")


def test_429_rate_limit_handler(app):
    """Prueba el manejador de errores 429."""
    # Para probar esto, necesitamos registrar el manejador y luego abortar con 429
    from flask import abort

    @app.route("/trigger-429")
    def trigger_429():
        abort(429)

    with app.test_client() as client:
        with patch("app.core.middleware.logger") as mock_logger:
            response = client.get("/trigger-429")
            assert response.status_code == 429
            json_data = response.get_json()
            assert json_data["error"] == "Demasiadas solicitudes. Intenta mÃ¡s tarde."
            assert json_data["status_code"] == 429

            # Verificar log
            mock_logger.warning.assert_called()
            assert "Rate limit exceeded from" in mock_logger.warning.call_args[0][0]
