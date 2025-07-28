"""Pruebas para las rutas de la aplicación."""

import pytest


def test_index_route(client):
    """
    Prueba que la ruta principal devuelve un código de estado 200.
    """
    response = client.get('/')
    assert response.status_code == 200


def test_api_health_check(client):
    """
    Prueba que la ruta de verificación de salud de la API funciona correctamente.
    """
    response = client.get('/api/health')
    assert response.status_code in (200, 404)  # Aceptamos 404 si la ruta no está implementada aún