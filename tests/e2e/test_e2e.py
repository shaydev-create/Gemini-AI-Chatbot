# Test end-to-end básico

import pytest

from app.core.application import get_flask_app


@pytest.fixture
def app():
    """Crear aplicación Flask para tests E2E."""
    import os
    from unittest.mock import MagicMock, patch

    from app.models import db

    # Configurar variable de entorno para testing
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test-api-key-for-testing"}):
        app_instance = get_flask_app("testing")

        # Mockear el servicio Gemini para evitar errores de inicialización
        mock_gemini_service = MagicMock()
        mock_gemini_service.generate_response.return_value = "Mocked Gemini response"
        app_instance.gemini_service = mock_gemini_service

        # Crear tablas de la base de datos
        with app_instance.app_context():
            db.drop_all()
            db.create_all()
            yield app_instance
            db.session.remove()
            db.drop_all()
            db.engine.dispose()


@pytest.fixture
def client(app):
    """Cliente de test."""
    return app.test_client()


def test_e2e_main_page(client):
    """Test E2E para verificar que la página principal carga correctamente."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"<!DOCTYPE html>" in response.data


def test_e2e_chat_page(client):
    """Test E2E para verificar que la página de chat carga correctamente."""
    response = client.get("/chat")
    assert response.status_code == 200
    assert b"<!DOCTYPE html>" in response.data
