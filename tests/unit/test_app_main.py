import runpy
import unittest
from unittest.mock import MagicMock, patch


class TestAppMain(unittest.TestCase):
    @patch("app.core.application.create_app")
    def test_main_script_execution(self, mock_create_app):
        """
        Prueba que el script principal `app_original.py` se ejecuta correctamente
        cuando es llamado como __main__.
        """
        # Configurar el mock para la app y socketio
        mock_app = MagicMock()
        mock_socketio = MagicMock()
        mock_create_app.return_value = (mock_app, mock_socketio)

        # Ejecutar app_original.py como si fuera el script principal
        runpy.run_path("app_original.py", run_name="__main__")

        # Verificar que create_app fue llamado para instanciar la app
        mock_create_app.assert_called_once()

        # Verificar que socketio.run fue llamado con los argumentos correctos
        mock_socketio.run.assert_called_once_with(
            mock_app,
            host="127.0.0.1",
            port=5000,
            debug=True,
            allow_unsafe_werkzeug=True,
        )


if __name__ == "__main__":
    unittest.main()
