import runpy
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestAppMain(unittest.TestCase):
    @patch("app.core.application.create_app")
    def test_main_script_execution(self, mock_create_app):
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

        # Verificar que importa subprocess para ejecutar launch_app.py
        assert "subprocess" in content, "El archivo debe usar subprocess para ejecutar launcher"


if __name__ == "__main__":
    unittest.main()
