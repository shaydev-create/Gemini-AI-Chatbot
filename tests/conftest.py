"""Configuración y fixtures para pruebas."""

import pytest
from app.core.application import create_app
from config.settings import Config


@pytest.fixture
def app():
    """
    Fixture que proporciona una instancia de la aplicación Flask para pruebas.
    """
    app = create_app()
    app.config.update({
        'TESTING': True,
        'DEBUG': True,
    })

    # Configurar la aplicación para pruebas
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """
    Fixture que proporciona un cliente de prueba para la aplicación Flask.
    """
    return app.test_client()
