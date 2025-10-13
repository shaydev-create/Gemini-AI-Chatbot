import runpy
import unittest
from unittest.mock import MagicMock, patch


class TestAppMain(unittest.TestCase):
    @patch("app.core.application.create_app")
    def test_main_script_execution(self, mock_create_app):
        """
        Prueba que el script principal `app/main.py` se ejecuta correctamente
        cuando es llamado como __main__.
        """
        # Configurar el mock para la app y su método run.
        # create_app devolverá este mock.
        mock_app = MagicMock()
        mock_create_app.return_value = mock_app

        # Ejecutar el script app/main.py simulando `python app/main.py`.
        # run_name='__main__' asegura que el bloque if __name__ == '__main__' se ejecute.
        runpy.run_module("app.main", run_name="__main__")

        # Verificar que create_app fue llamado para instanciar la app.
        mock_create_app.assert_called_once()

        # Verificar que app.run() fue llamado con los argumentos correctos.
        # El objeto app creado dentro de app/main.py es en realidad nuestro mock_app.
        mock_app.run.assert_called_once_with(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    unittest.main()
