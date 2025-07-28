# Pruebas del Proyecto Gemini AI Chatbot

Este directorio contiene las pruebas automatizadas para el proyecto Gemini AI Chatbot.

## Estructura de Pruebas

Las pruebas están organizadas en tres categorías principales:

- **Pruebas Unitarias** (`unit/`): Pruebas de componentes individuales y funciones aisladas.
- **Pruebas de Integración** (`integration/`): Pruebas que verifican la interacción entre diferentes componentes.
- **Pruebas End-to-End** (`e2e/`): Pruebas que simulan el comportamiento del usuario final.

## Ejecución de Pruebas

Para ejecutar todas las pruebas, utiliza el siguiente comando desde la raíz del proyecto:

```bash
pytest
```

Para ejecutar un tipo específico de pruebas:

```bash
# Pruebas unitarias
pytest tests/unit/

# Pruebas de integración
pytest tests/integration/

# Pruebas end-to-end
pytest tests/e2e/
```

Para generar un informe de cobertura:

```bash
pytest --cov=src --cov=core --cov=app --cov-report=html
```

El informe de cobertura se generará en el directorio `htmlcov/`.

## Añadir Nuevas Pruebas

Al añadir nuevas pruebas, sigue estas convenciones:

1. Los archivos de prueba deben comenzar con `test_`.
2. Las funciones de prueba deben comenzar con `test_`.
3. Utiliza fixtures de pytest cuando sea apropiado para configurar el entorno de prueba.
4. Documenta el propósito de cada prueba con docstrings.

## Marcadores de Pytest

Se han definido varios marcadores personalizados en `pytest.ini` para categorizar las pruebas:

- `@pytest.mark.unit`: Pruebas unitarias
- `@pytest.mark.integration`: Pruebas de integración
- `@pytest.mark.e2e`: Pruebas end-to-end
- `@pytest.mark.slow`: Pruebas que tardan más tiempo en ejecutarse

Para ejecutar pruebas con un marcador específico:

```bash
pytest -m unit
```