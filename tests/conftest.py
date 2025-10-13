import pytest
from app.core.application import create_app


@pytest.fixture(scope="module")
def app():
    """Crea y configura una nueva instancia de la aplicacion para cada modulo de prueba."""
    app_instance, socketio = create_app("testing")
    yield app_instance


@pytest.fixture(scope="module")
def client(app):
    """Fixture que proporciona un cliente de prueba para la aplicacion Flask."""
    return app.test_client()
