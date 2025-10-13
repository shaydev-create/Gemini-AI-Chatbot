import unittest

from app.core.application import create_app


class TestMainApp(unittest.TestCase):

    def setUp(self):
        """Configura el entorno para cada prueba."""
        app = create_app('testing')
        self.client = app.test_client()

    def test_app_creation(self):
        """Prueba que la aplicacion Flask se crea correctamente."""
        self.assertIsNotNone(self.client)

    def test_root_route(self):
        """Prueba que la ruta raiz devuelve una respuesta exitosa."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'GEMINI AI', response.data)

if __name__ == '__main__':
    unittest.main()
