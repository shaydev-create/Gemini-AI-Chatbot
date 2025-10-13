import pytest
from app.core.application import get_flask_app



@pytest.fixture(scope="module")
def app():
    """Crea y configura una nueva instancia de la aplicacion Flask para cada modulo de prueba."""
    app_instance = get_flask_app("testing")
    yield app_instance


@pytest.fixture(scope="module")
def client(app):
    """Fixture que proporciona un cliente de prueba para la aplicacion Flask."""
    return app.test_client()
