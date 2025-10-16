import os

import pytest

from app.auth import AuthManager
from app.core.application import get_flask_app
from app.models import User, db


@pytest.fixture
def app():
    os.environ["GEMINI_API_KEY"] = "test-api-key-for-testing"
    app_instance = get_flask_app("testing")

    from unittest.mock import MagicMock

    mock_gemini_service = MagicMock()
    mock_gemini_service.generate_response.return_value = "Mocked Gemini response"
    app_instance.gemini_service = mock_gemini_service
    app_instance.config["GEMINI_SERVICE"] = mock_gemini_service

    # Crear tablas para los tests
    with app_instance.app_context():
        db.create_all()
        yield app_instance
        db.session.rollback()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def auth_manager(app):
    """Fixture para AuthManager."""
    with app.app_context():
        return AuthManager()


@pytest.fixture
def test_user(app):
    """Fixture para crear un usuario de prueba."""
    with app.app_context():
        user = User(username="testuser", email="test@example.com", role="user")
        user.set_password("TestPassword123!")  # Contraseña que cumple los requisitos
        db.session.add(user)
        db.session.commit()
        # Refrescar para mantener conectado a la sesión
        db.session.refresh(user)
        yield user
        # Cleanup al final
        try:
            db.session.delete(user)
            db.session.commit()
        except Exception:
            db.session.rollback()
