"""Pruebas unitarias para la aplicación Flask."""

from app.core.application import create_app


def test_create_app():
    """
    Prueba que la función create_app crea correctamente una instancia de Flask.
    """
    app = create_app('testing')
    assert app is not None
    assert 'app.core.application' in app.name


def test_app_config():
    """
    Prueba que la aplicación carga correctamente la configuración.
    """
    app = create_app('testing')
    assert 'DEBUG' in app.config
    assert 'SECRET_KEY' in app.config
