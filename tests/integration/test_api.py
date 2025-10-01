"""
Tests de integración para la aplicación.
"""

import pytest
import json
from app.core.application import create_app
from config.settings import TestingConfig


@pytest.fixture
def app():
    """Crear aplicación para tests."""
    app = create_app(TestingConfig)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Cliente de test."""
    return app.test_client()


class TestAPIIntegration:
    """Tests de integración para la API."""

    def test_health_endpoint(self, client):
        """Test endpoint de salud."""
        response = client.get('/api/health')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'version' in data
        assert 'metrics' in data

    def test_metrics_endpoint(self, client):
        """Test endpoint de métricas."""
        response = client.get('/api/metrics')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'uptime_seconds' in data
        assert 'counters' in data
        assert 'timestamp' in data

    def test_main_page(self, client):
        """Test página principal."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'html' in response.data.lower()

    def test_chat_page(self, client):
        """Test página de chat."""
        response = client.get('/chat')
        assert response.status_code == 200
        assert b'html' in response.data.lower()

    def test_manifest_json(self, client):
        """Test manifest.json."""
        response = client.get('/manifest.json')
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'application/manifest+json'

    def test_robots_txt(self, client):
        """Test robots.txt."""
        response = client.get('/robots.txt')
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'text/plain; charset=utf-8'
        assert b'User-agent' in response.data

    def test_sitemap_xml(self, client):
        """Test sitemap.xml."""
        response = client.get('/sitemap.xml')
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'application/xml; charset=utf-8'
        assert b'<?xml version' in response.data
        assert b'<urlset' in response.data

    def test_send_message_missing_data(self, client):
        """Test envío de mensaje sin datos."""
        response = client.post('/api/chat/send',
                               data=json.dumps({}),
                               content_type='application/json')
        assert response.status_code == 400

        data = json.loads(response.data)
        assert data['success'] is False
        assert 'requerido' in data['message']

    def test_send_message_empty(self, client):
        """Test envío de mensaje vacío."""
        response = client.post('/api/chat/send',
                               data=json.dumps({'message': ''}),
                               content_type='application/json')
        assert response.status_code == 400

        data = json.loads(response.data)
        assert data['success'] is False
        assert 'vacío' in data['message']

    def test_send_message_too_long(self, client):
        """Test envío de mensaje muy largo."""
        long_message = 'a' * 5000
        response = client.post('/api/chat/send',
                               data=json.dumps({'message': long_message}),
                               content_type='application/json')
        assert response.status_code == 400

        data = json.loads(response.data)
        assert data['success'] is False
        assert 'largo' in data['message']

    def test_send_message_valid_format(self, client):
        """Test formato de respuesta válida."""
        # Este test asume que no hay API key configurada en testing
        response = client.post('/api/chat/send',
                               data=json.dumps({'message': 'Hola'}),
                               content_type='application/json')

        # Puede ser 200 (éxito) o 500 (error de API)
        assert response.status_code in [200, 500]

        data = json.loads(response.data)
        assert 'success' in data
        assert 'message' in data

    def test_rate_limiting(self, client):
        """Test rate limiting básico."""
        # Hacer muchas requests rápidas
        responses = []
        for i in range(65):  # Más del límite de 60
            response = client.post('/api/chat/send',
                                   data=json.dumps({'message': f'Test {i}'}),
                                   content_type='application/json')
            responses.append(response.status_code)

        # Al menos una debería ser 429 (rate limited)
        assert 429 in responses
