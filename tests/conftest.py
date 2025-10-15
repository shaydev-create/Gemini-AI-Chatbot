import pytest

from app.auth import AuthManager
from app.core.application import get_flask_app
from app.models import User, db


@pytest.fixture(scope="function")
def app():
    """Crea y configura una nueva instancia de la aplicacion Flask para cada modulo de prueba."""
    import os
    from unittest.mock import MagicMock, patch

    # Configurar variable de entorno para testing
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test-api-key-for-testing"}):
        app_instance = get_flask_app("testing")

        # Mockear el servicio Gemini para evitar errores de inicialización
        mock_gemini_service = MagicMock()
        mock_gemini_service.generate_response.return_value = "Mocked Gemini response"
        app_instance.gemini_service = mock_gemini_service
        app_instance.config["GEMINI_SERVICE"] = mock_gemini_service

        # Crear tablas de la base de datos
        with app_instance.app_context():
            db.drop_all()
            db.create_all()
            yield app_instance
            db.session.remove()
            db.drop_all()
            db.engine.dispose()


@pytest.fixture(scope="function")
def client(app):
    """Fixture que proporciona un cliente de prueba para la aplicacion Flask."""
    return app.test_client()


@pytest.fixture(scope="module")
def auth_manager():
    """Fixture que proporciona una instancia de AuthManager."""
    return AuthManager()


@pytest.fixture(scope="function")
def test_user(app):
    """Fixture que crea un usuario de prueba para los tests."""
    with app.app_context():
        # Eliminar usuario de prueba si existe
        existing_user = User.query.filter_by(username="testuser").first()
        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()

        # Crear nuevo usuario de prueba
        user = User(username="testuser", email="test@example.com", role="user")
        user.set_password("TestPassword123!")
        db.session.add(user)
        db.session.commit()

        yield user

        # Limpiar después del test
        db.session.delete(user)
        db.session.commit()
