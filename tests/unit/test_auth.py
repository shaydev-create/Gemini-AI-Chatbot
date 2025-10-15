import pytest

from app.core.application import get_flask_app
from app.models import User


@pytest.fixture
def app():
    """Fixture para crear una instancia de la aplicación Flask para pruebas."""
    app = get_flask_app("testing")

    # Crear tablas de la base de datos
    with app.app_context():
        from app.config.extensions import db

        db.create_all()

    yield app

    # Limpiar la base de datos después de cada test
    with app.app_context():
        from app.config.extensions import db

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Fixture para crear un cliente de pruebas."""
    return app.test_client()


@pytest.fixture
def new_user_data():
    """Fixture para proporcionar datos de usuario de prueba."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPassword123!",
    }


def test_register_success(app, client, new_user_data):
    """Prueba el registro exitoso de un nuevo usuario."""
    with app.app_context():
        response = client.post("/auth/register", json=new_user_data)
        assert response.status_code == 201
        assert "message" in response.json
        assert "Usuario registrado con éxito" in response.json["message"]

        # Verificar que el usuario está en la base de datos
        user = User.query.filter_by(email=new_user_data["email"]).first()
        assert user is not None
        assert user.username == new_user_data["username"]


def test_register_missing_data(client):
    """Prueba el registro con datos faltantes."""
    response = client.post("/auth/register", json={})
    assert response.status_code == 400
    assert "message" in response.json
    assert "Se requieren nombre de usuario" in response.json["message"]


def test_register_existing_email(app, client, new_user_data):
    """Prueba el registro con un email que ya existe."""
    with app.app_context():
        client.post("/auth/register", json=new_user_data)  # Registrar primero
        response = client.post("/auth/register", json=new_user_data)  # Intentar de nuevo
        assert response.status_code == 409
        assert "message" in response.json


def test_login_success(app, client, new_user_data):
    """Prueba un inicio de sesión exitoso."""
    # Primero, registrar el usuario
    with app.app_context():
        client.post("/auth/register", json=new_user_data)

        # Activar el usuario manualmente (ya que por defecto queda en estado "pending")
        from app.config.extensions import db
        from app.models import User

        user = User.query.filter_by(email=new_user_data["email"]).first()
        user.status = "active"
        db.session.commit()

        login_data = {
            "username": new_user_data["username"],
            "password": new_user_data["password"],
        }
        response = client.post("/auth/login", json=login_data)

        assert response.status_code == 200
        assert "access_token" in response.json


def test_login_invalid_credentials(app, client, new_user_data):
    """Prueba un inicio de sesión con contraseña incorrecta."""
    with app.app_context():
        client.post("/auth/register", json=new_user_data)

        login_data = {
            "username": new_user_data["username"],
            "password": "wrongpassword",
        }
        response = client.post("/auth/login", json=login_data)

        assert response.status_code == 401
        assert "message" in response.json


def test_login_nonexistent_user(app, client):
    """Prueba un inicio de sesión con un usuario que no existe."""
    with app.app_context():
        login_data = {"username": "nonexistent", "password": "password"}
        response = client.post("/auth/login", json=login_data)

        assert response.status_code == 401
        assert "message" in response.json


def test_login_missing_data(app, client):
    """Prueba un inicio de sesión con datos faltantes."""
    with app.app_context():
        response = client.post("/auth/login", json={})
        assert response.status_code == 400
        assert "message" in response.json
