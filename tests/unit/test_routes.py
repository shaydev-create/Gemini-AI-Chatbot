import json
from unittest.mock import patch

import pytest
from app.api.routes import api_bp
from app.core.metrics import MetricsManager
from flask import Flask


@pytest.fixture
def app():
    """Crea una instancia de una aplicación Flask para pruebas de rutas."""
    app = Flask(__name__, template_folder='../../app/templates', static_folder='../../static')
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret'

    # Mock de dependencias
    app.config['metrics_manager'] = MetricsManager() # Usar una instancia real para pruebas

    # Mock para la función de traducción en el contexto de la plantilla
    @app.context_processor
    def utility_processor():
        def translate(text):
            return text  # Simplemente devuelve el texto original
        return dict(translate=translate)

    # api_bp.app  # Línea corregida, elimina el paréntesis suelto

    # Añadir una ruta de 'static' para que send_from_directory funcione en pruebas
    # Esto es un workaround para el contexto de las pruebas
    @app.route('/static/<path:filename>')
    def static_files(filename):
        return f"Contenido de {filename}", 200

    return app

@pytest.fixture
def client(app):
    """Un cliente de prueba para la aplicación Flask."""
    return app.test_client()

# --- Pruebas para Rutas Principales (main_bp) ---

def test_index_route(client):
    """Prueba que la ruta principal '/' renderiza la plantilla correcta."""
    response = client.get('/')
    assert response.status_code == 200
    assert 'Gemini AI Chatbot' in response.data.decode('utf-8')

def test_chat_route(client):
    """Prueba que la ruta '/chat' renderiza la plantilla de chat."""
    response = client.get('/chat')
    assert response.status_code == 200
    assert 'Gemini AI Chat' in response.data.decode('utf-8')

def test_privacy_policy_route(client):
    """Prueba que la ruta '/privacy_policy' renderiza la política de privacidad."""
    response = client.get('/privacy_policy')
    assert response.status_code == 200
    assert 'Política de Privacidad' in response.data.decode('utf-8')

# --- Pruebas para Rutas de Utilidad (main_bp) ---

def test_manifest_route(client):
    """Prueba que la ruta '/manifest.json' devuelve un JSON válido."""
    response = client.get('/manifest.json')
    assert response.status_code == 200
    assert response.content_type == 'application/manifest+json'
    data = json.loads(response.data)
    assert data['short_name'] == 'Gemini Chat'

def test_robots_txt_route(client):
    """Prueba que la ruta '/robots.txt' devuelve texto plano."""
    response = client.get('/robots.txt')
    assert response.status_code == 200
    assert response.content_type == 'text/plain; charset=utf-8'
    assert b'User-agent: *' in response.data

def test_sitemap_xml_route(client):
    """Prueba que la ruta '/sitemap.xml' devuelve un XML válido."""
    response = client.get('/sitemap.xml')
    assert response.status_code == 200
    assert response.content_type == 'application/xml; charset=utf-8'
    assert b'<loc>http://localhost/</loc>' in response.data
    assert b'<loc>http://localhost/chat</loc>' in response.data

@patch('app.api.routes.send_from_directory')
def test_favicon_route(mock_send, app):
    """Prueba que la ruta '/favicon.ico' intenta servir el archivo."""
    # El mock debe devolver un objeto Response para que se puedan añadir cabeceras
    mock_send.return_value = app.response_class("favicon content", mimetype='image/x-icon')
    client = app.test_client()
    response = client.get('/favicon.ico')
    assert response.status_code == 200
    assert response.data == b"favicon content"
    assert response.headers["Content-Type"] == "image/x-icon"

@patch('app.api.routes.send_from_directory', side_effect=FileNotFoundError)
def test_favicon_not_found(mock_send, client):
    """Prueba el comportamiento cuando '/favicon.ico' no se encuentra."""
    response = client.get('/favicon.ico')
    assert response.status_code == 204

# --- Pruebas para Rutas API (api_bp) ---

def test_chat_api_authorized(client):
    """Prueba el endpoint /api/chat con autorización."""
    response = client.post('/api/chat', headers={'Authorization': 'Bearer test-token'}, json={'message': 'test'})
    assert response.status_code == 200
    assert response.json['success'] is True

def test_chat_api_unauthorized(client):
    """Prueba el endpoint /api/chat sin autorización."""
    response = client.post('/api/chat', json={'message': 'test'})
    assert response.status_code == 401
    assert response.json['success'] is False

@patch('app.api.routes.GeminiService')
def test_send_message_success(mock_gemini_service, client):
    """Prueba el envío de un mensaje exitoso a /api/chat/send."""
    mock_instance = mock_gemini_service.return_value
    mock_instance.generate_response.return_value = {"success": True, "response": "Hola, soy Gemini."}

    response = client.post('/api/chat/send', json={'message': 'Hola'})
    assert response.status_code == 200
    assert response.json['success'] is True
    assert response.json['response'] == "Hola, soy Gemini."
    mock_instance.generate_response.assert_called_with('Hola')

def test_send_message_missing_data(client):
    """Prueba el envío sin datos a /api/chat/send."""
    response = client.post('/api/chat/send', json={})
    assert response.status_code == 400
    assert response.json['error_code'] == 'MISSING_MESSAGE'

def test_send_message_empty_message(client):
    """Prueba el envío de un mensaje vacío a /api/chat/send."""
    response = client.post('/api/chat/send', json={'message': '  '})
    assert response.status_code == 400
    assert response.json['error_code'] == 'EMPTY_MESSAGE'

def test_send_message_too_long(client):
    """Prueba el envío de un mensaje demasiado largo a /api/chat/send."""
    long_message = 'a' * 4001
    response = client.post('/api/chat/send', json={'message': long_message})
    assert response.status_code == 400
    assert response.json['error_code'] == 'MESSAGE_TOO_LONG'

@patch('app.api.routes.GeminiService', side_effect=Exception("Internal Error"))
def test_send_message_internal_error(mock_gemini_service, client):
    """Prueba el manejo de un error interno en /api/chat/send."""
    response = client.post('/api/chat/send', json={'message': 'Hola'})
    assert response.status_code == 500
    assert response.json['error_code'] == 'INTERNAL_ERROR'

def test_upload_authorized(client):
    """Prueba el endpoint /api/upload con autorización."""
    response = client.post('/api/upload', headers={'Authorization': 'Bearer test-token'})
    assert response.status_code == 200
    assert response.json['message'] == 'Archivo subido'

def test_upload_unauthorized(client):
    """Prueba el endpoint /api/upload sin autorización."""
    response = client.post('/api/upload')
    assert response.status_code == 401

def test_health_check_route(app, client):
    """Prueba que la ruta /api/health funciona correctamente."""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.json
    assert data['status'] == 'healthy'
    assert 'timestamp' in data
    assert 'metrics' in data
    assert 'uptime_seconds' in data['metrics']

def test_get_metrics_route(app, client):
    """Prueba que la ruta /api/metrics funciona correctamente."""
    response = client.get('/api/metrics')
    assert response.status_code == 200
    data = response.json
    assert 'counters' in data
    assert 'uptime_seconds' in data
