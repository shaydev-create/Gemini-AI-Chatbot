# Test end-to-end básico

import pytest
from app.core.application import get_flask_app


@pytest.fixture
def app():
    """Crear aplicación Flask para tests E2E."""
    app = get_flask_app("testing")
    return app


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
