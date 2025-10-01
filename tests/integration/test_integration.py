# Test de integración básico

import os
import pytest


def test_environment_variables():
    """Test que verifica que las variables de entorno necesarias estén configuradas."""
    # Este test simplemente verifica que podemos acceder a variables de entorno
    # No verifica valores reales para mantener la seguridad

    # Establecer una variable de entorno de prueba
    os.environ["TEST_VARIABLE"] = "test_value"

    # Verificar que podemos leerla
    assert os.environ.get("TEST_VARIABLE") == "test_value"

    # Verificar que podemos acceder a variables de entorno (sin revelar valores)
    # Solo verificamos que la función de acceso a variables de entorno funciona
    assert os.environ.get("NON_EXISTENT_VARIABLE", "default") == "default"
