import pytest
from app.api.auth import auth_bp
from app.config.database import db
from app.models import User
from flask import Flask


@pytest.fixture
def app():
    """Crea una instancia de una aplicación Flask para pruebas de autenticación."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "test-secret"

    db.init_app(app)
    app.register_blueprint(auth_bp)

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    """Un cliente de prueba para la aplicación Flask."""
    return app.test_client()


@pytest.fixture
def new_user_data():
    """Datos para un nuevo usuario."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User",
    }


def test_register_success(client, new_user_data):
    """Prueba el registro exitoso de un nuevo usuario."""
    response = client.post("/auth/register", json=new_user_data)
    assert response.status_code == 201
    assert response.json["success"] is True
    assert response.json["message"] == "Usuario registrado"

    # Verificar que el usuario está en la base de datos
    user = User.query.filter_by(email=new_user_data["email"]).first()
    assert user is not None
    assert user.username == new_user_data["username"]


def test_register_missing_data(client):
    """Prueba el registro con datos faltantes."""
    response = client.post("/auth/register", json={})
    assert response.status_code == 400
    assert response.json["success"] is False
    assert response.json["message"] == "Datos requeridos"


def test_register_existing_email(client, new_user_data):
    """Prueba el registro con un email que ya existe."""
    client.post("/auth/register", json=new_user_data)  # Registrar primero
    response = client.post("/auth/register", json=new_user_data)  # Intentar de nuevo
    assert response.status_code == 409
    assert response.json["success"] is False
    assert response.json["message"] == "Email ya registrado"


def test_login_success(client, new_user_data):
    """Prueba un inicio de sesión exitoso."""
    # Primero, registrar el usuario
    client.post("/auth/register", json=new_user_data)

    login_data = {
        "email": new_user_data["email"],
        "password": new_user_data["password"],
    }
    response = client.post("/auth/login", json=login_data)

    assert response.status_code == 200
    assert response.json["success"] is True
    assert response.json["message"] == "Login exitoso"
    assert "access_token" in response.json


def test_login_invalid_credentials(client, new_user_data):
    """Prueba un inicio de sesión con contraseña incorrecta."""
    client.post("/auth/register", json=new_user_data)

    login_data = {"email": new_user_data["email"], "password": "wrongpassword"}
    response = client.post("/auth/login", json=login_data)

    assert response.status_code == 401
    assert response.json["success"] is False
    assert response.json["message"] == "Credenciales inválidas"


def test_login_nonexistent_user(client):
    """Prueba un inicio de sesión con un usuario que no existe."""
    login_data = {"email": "nonexistent@example.com", "password": "password"}
    response = client.post("/auth/login", json=login_data)

    assert response.status_code == 401
    assert response.json["success"] is False
    assert response.json["message"] == "Credenciales inválidas"


def test_login_missing_data(client):
    """Prueba un inicio de sesión con datos faltantes."""
    response = client.post("/auth/login", json={})
    assert response.status_code == 400
    assert response.json["success"] is False
    assert response.json["message"] == "Datos requeridos"
