# -*- coding: utf-8 -*-
"""
🧪 TESTS UNITARIOS - GEMINI AI CHATBOT

Suite completa de tests para validar todas las funcionalidades del sistema.
"""

import pytest
from app.auth import AuthManager
from app.models import User, db


@pytest.fixture(scope="function")
def init_database(app):
    """
    Fixture para inicializar y limpiar la base de datos para cada función de test.
    Usa el contexto de la aplicación del fixture 'app' de conftest.
    """
    with app.app_context():
        db.create_all()

        # Crear un usuario de prueba estándar
        test_user = User(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
        )
        test_user.set_password("testpassword123")
        test_user.email_verified = True
        test_user.status = "active"
        db.session.add(test_user)
        db.session.commit()

        yield db  # Proporciona la instancia de la BD al test

        db.session.remove()
        db.drop_all()


class TestUserModel:
    """Tests para el modelo User."""

    def test_user_creation(self, app, init_database):
        """Test creación de usuario."""
        with app.app_context():
            user = User(username="newuser", email="new@example.com")
            user.set_password("password123")

            init_database.session.add(user)
            init_database.session.commit()

            assert user.id is not None
            assert user.username == "newuser"
            assert user.check_password("password123")

    def test_password_hashing(self, app):
        """Test hashing de contraseñas."""
        with app.app_context():
            user = User(username="test", email="test@test.com")
            user.set_password("secret")

            assert user.password_hash != "secret"
            assert user.check_password("secret")
            assert not user.check_password("wrong")

    def test_account_locking(self, app, init_database):
        """Test bloqueo de cuenta."""
        with app.app_context():
            user = (
                init_database.session.query(User)
                .filter_by(email="test@example.com")
                .one()
            )

            # Incrementar intentos fallidos
            for _ in range(5):
                user.increment_failed_login()

            # Bloquear cuenta
            user.lock_account(15)

            assert user.is_account_locked()

            # Desbloquear
            user.unlock_account()
            assert not user.is_account_locked()


class TestAuthentication:
    """Tests para autenticación."""

    def test_login_success(self, client, init_database):
        """Test login exitoso."""
        response = client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "testpassword123"},
        )
        assert response.status_code == 200
        assert "access_token" in response.json

    def test_login_invalid_credentials(self, client, init_database):
        """Test login con credenciales inválidas."""
        response = client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401

    def test_register_user(self, client, init_database):
        """Test registro de nuevo usuario."""
        response = client.post(
            "/auth/register",
            json={
                "username": "newuser2",
                "email": "new2@example.com",
                "password": "a_strong_password_123",
            },
        )
        assert response.status_code == 201
        assert "Usuario registrado" in response.json["message"]


class TestPasswordStrength:
    """Tests para la validación de fortaleza de contraseña."""

    def test_password_strength_valid(self):
        """Test de contraseña válida."""
        auth_manager = AuthManager()
        is_strong, message = auth_manager.validate_password_strength("Str0ngP@ssw0rd!")
        assert is_strong
        assert message == "La contraseña es segura."

    def test_password_strength_invalid_length(self):
        """Test de contraseña con longitud inválida."""
        auth_manager = AuthManager()
        is_strong, message = auth_manager.validate_password_strength("Sh0rt")
        assert not is_strong
        assert "La contraseña debe tener al menos 8 caracteres." in message

    def test_password_strength_missing_digit(self):
        """Test de contraseña sin dígitos."""
        auth_manager = AuthManager()
        is_strong, message = auth_manager.validate_password_strength("NoDigitsHere!")
        assert not is_strong
        assert "La contraseña debe contener al menos un dígito." in message

    def test_password_strength_missing_uppercase(self):
        """Test de contraseña sin mayúsculas."""
        is_strong, message = AuthManager().validate_password_strength("nouppercase1!")
        assert not is_strong
        assert "La contraseña debe contener al menos una letra mayúscula." in message

    def test_password_strength_missing_lowercase(self):
        """Test de contraseña sin minúsculas."""
        is_strong, message = AuthManager().validate_password_strength("NOLOWERCASE1!")
        assert not is_strong
        assert "La contraseña debe contener al menos una letra minúscula." in message

    def test_password_strength_missing_special_char(self):
        """Test de contraseña sin caracteres especiales."""
        is_strong, message = AuthManager().validate_password_strength("NoSpecialChar1")
        assert not is_strong
        assert "La contraseña debe contener al menos un carácter especial" in message

    def test_login_success(self, client, init_database):
        """Test login exitoso."""
        response = client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "testpassword123"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "access_token" in data

    def test_login_invalid_credentials(self, client, init_database):
        """Test login con credenciales inválidas."""
        response = client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "wrongpassword"},
        )

        assert response.status_code == 401

    def test_register_user(self, client, init_database, app):
        """Test registro de usuario."""
        response = client.post(
            "/auth/register",
            json={
                "username": "newuser_register",
                "email": "newuser_register@example.com",
                "password": "newpassword123",
                "first_name": "New",
                "last_name": "User",
            },
        )

        assert response.status_code == 201

        # Verificar que el usuario fue creado
        with app.app_context():
            user = User.query.filter_by(email="newuser_register@example.com").first()
            assert user is not None
            assert user.username == "newuser_register"


@pytest.mark.usefixtures("init_database")
class TestPasswordValidation:
    def test_strong_password(self, client):
        """Test a strong password passes validation."""
        is_valid, message = AuthManager().validate_password_strength("Str0ngP@ssw0rd!")
        assert is_valid
        assert message == "La contraseña es segura."

    def test_weak_password(self, client):
        """Test a weak password fails validation."""
        is_valid, message = AuthManager().validate_password_strength("weak")
        assert not is_valid
        assert message == "La contraseña debe tener al menos 8 caracteres."


class TestChatAPI:
    """Tests para API de chat."""

    def test_chat_without_auth(self, client):
        """Test chat sin autenticación."""
        response = client.post("/api/chat", json={"message": "Hello"})

        assert response.status_code == 401

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"


class TestFileUpload:
    """Tests para carga de archivos."""

    def test_upload_without_auth(self, client):
        """Test upload sin autenticación."""
        response = client.post("/api/upload")
        assert response.status_code == 401
