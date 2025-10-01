"""Pruebas para verificar la versión de la aplicación."""

import app


def test_version():
    """
    Prueba que la aplicación tiene una versión definida.
    """
    assert hasattr(app, '__version__')
    assert isinstance(app.__version__, str)
    assert app.__version__ != ''
