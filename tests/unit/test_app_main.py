import unittest
from pathlib import Path
from unittest.mock import patch


class TestAppMain(unittest.TestCase):
    @patch("app.core.application.get_flask_app")
    def test_main_script_execution(self, mock_get_flask_app):
        """
        Prueba que el script principal `run.py` existe y tiene la estructura correcta.
        """
        # Verificar que el archivo run.py existe
        run_file = Path("run.py")
        assert run_file.exists(), "El archivo run.py debe existir"

        # Verificar que el archivo contiene las funciones necesarias
        content = run_file.read_text(encoding="utf-8")
        assert "def main()" in content, "El archivo debe contener una función main()"
        assert 'if __name__ == "__main__"' in content, "El archivo debe ser ejecutable"

        # Verificar que usa get_flask_app para importación directa
        assert "from app.core.application import get_flask_app" in content, "El archivo debe importar get_flask_app"
        assert "app.run(" in content, "El archivo debe ejecutar el servidor Flask directamente"


if __name__ == "__main__":
    unittest.main()
