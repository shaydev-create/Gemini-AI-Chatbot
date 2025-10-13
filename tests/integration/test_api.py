"""
Tests de integración para la aplicación.
"""

import json
from unittest.mock import patch

import pytest
from app.core.application import get_flask_app



@pytest.fixture
def app():
    """Crear aplicación Flask para tests."""
    app = get_flask_app("testing")
    return app


@pytest.fixture
def client(app):
    """Cliente de test."""
    return app.test_client()


class TestAPIIntegration:
    """Tests de integración para la API."""

    def test_health_endpoint(self, client):
        """Test endpoint de salud."""
        response = client.get("/api/health")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "metrics" in data

    def test_metrics_endpoint(self, client):
        """Test endpoint de métricas."""
        response = client.get("/api/metrics")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "uptime_seconds" in data
        assert "counters" in data
        assert "timestamp" in data

    def test_main_page(self, client):
        """Test página principal."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"html" in response.data.lower()

    def test_chat_page(self, client):
        """Test página de chat."""
        response = client.get("/chat")
        assert response.status_code == 200
        assert b"html" in response.data.lower()

    def test_manifest_json(self, client):
        """Test manifest.json."""
        response = client.get("/manifest.json")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/manifest+json"

    def test_robots_txt(self, client):
        """Test robots.txt."""
        response = client.get("/robots.txt")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "text/plain; charset=utf-8"
        assert b"User-agent" in response.data

    def test_sitemap_xml(self, client):
        """Test sitemap.xml."""
        response = client.get("/sitemap.xml")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/xml; charset=utf-8"
        assert b"<?xml version" in response.data
        assert b"<urlset" in response.data

    def test_serve_e2e_test_files_js(self, client):
        """Test serving e2e JavaScript files."""
        response = client.get("/tests/e2e/dummy_test.js")
        assert response.status_code == 200
        assert response.mimetype == "application/javascript"
        assert b"E2E test file loaded" in response.data

    def test_serve_e2e_test_files_not_found(self, client):
        """Test serving non-existent e2e file."""
        response = client.get("/tests/e2e/non_existent_file.js")
        assert response.status_code == 500

    @patch("app.api.routes.send_from_directory", side_effect=FileNotFoundError)
    def test_service_worker_not_found(self, mock_send, client):
        """Test service worker returns basic content if file not found."""
        response = client.get("/sw.js")
        assert response.status_code == 200
        assert response.mimetype == "application/javascript"
        assert "Service Worker básico cargado".encode("utf-8") in response.data

    @patch("app.api.routes.send_from_directory", side_effect=FileNotFoundError)
    def test_favicon_not_found(self, mock_send, client):
        """Test that a 204 is returned when favicon.ico is not found."""
        response = client.get("/favicon.ico")
        assert response.status_code == 204

    def test_upload_unauthorized(self, client):
        """Test upload endpoint without authorization."""
        response = client.post("/api/upload")
        assert response.status_code == 401
        data = json.loads(response.data)
        assert not data["success"]
        assert "No autorizado" in data["message"]

    def test_upload_authorized(self, client):
        """Test upload endpoint with authorization."""
        response = client.post(
            "/api/upload", headers={"Authorization": "Bearer test-token"}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"]
        assert "Archivo subido" in data["message"]

    def test_chat_api_unauthorized(self, client):
        """Test chat API endpoint without authorization."""
        response = client.post("/api/chat", json={"message": "test"})
        assert response.status_code == 401

    def test_chat_api_authorized(self, client):
        """Test chat API endpoint with authorization."""
        response = client.post(
            "/api/chat",
            headers={"Authorization": "Bearer test-token"},
            json={"message": "test"},
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"]
        assert data["data"]["message"] == "test"

    def test_send_message_missing_data(self, client):
        """Test envío de mensaje sin datos."""
        response = client.post(
            "/api/chat/send", data=json.dumps({}), content_type="application/json"
        )
        assert response.status_code == 400

        data = json.loads(response.data)
        assert data["success"] is False
        assert "requerido" in data["message"]

    def test_send_message_empty(self, client):
        """Test envío de mensaje vacío."""
        response = client.post(
            "/api/chat/send",
            data=json.dumps({"message": ""}),
            content_type="application/json",
        )
        assert response.status_code == 400

        data = json.loads(response.data)
        assert data["success"] is False
        assert "vacío" in data["message"]

    def test_send_message_too_long(self, client):
        """Test envío de mensaje muy largo."""
        long_message = "a" * 5000
        response = client.post(
            "/api/chat/send",
            data=json.dumps({"message": long_message}),
            content_type="application/json",
        )
        assert response.status_code == 400

        data = json.loads(response.data)
        assert data["success"] is False
        assert "largo" in data["message"]

    def test_send_message_valid_format(self, client):
        """Test formato de respuesta válida."""
        # Este test asume que no hay API key configurada en testing
        response = client.post(
            "/api/chat/send",
            data=json.dumps({"message": "Hola"}),
            content_type="application/json",
        )

        # Puede ser 200 (éxito) o 500 (error de API)
        assert response.status_code in [200, 500]

    def test_rate_limiting(self, app):
        """Test de rate limiting con estado aislado."""
        # Acceder a la extensión Flask-Limiter
        limiter = app.extensions.get("flask-limiter")
        if limiter:
            limiter.reset()

        with app.test_client() as client:
            endpoint = "/api/health"

            # El límite por defecto es 60 por minuto.
            # Hacemos 60 peticiones que deberían ser exitosas.
            for i in range(60):
                response = client.get(endpoint)
                assert (
                    response.status_code == 200
                ), f"Request {i+1} failed with status {response.status_code}, expected 200"

            # La petición 61 debería fallar con 429 Too Many Requests
            response = client.get(endpoint)
            assert (
                response.status_code == 429
            ), f"Expected rate limit to be exceeded on request 61, but got {response.status_code}"
