import unittest
from unittest.mock import MagicMock, patch

from app.api.admin import admin_bp
from flask import Flask


class TestAdminRoutes(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.register_blueprint(admin_bp, url_prefix="/api/admin")
        self.client = self.app.test_client()

    @patch("app.api.admin.get_security_summary")
    def test_get_security_summary_route(self, mock_get_security_summary):
        """
        Prueba que la ruta /api/admin/security-summary funciona correctamente.
        """
        expected_summary = {"status": "secure"}
        mock_get_security_summary.return_value = expected_summary

        response = self.client.get("/api/admin/security-summary")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), expected_summary)
        mock_get_security_summary.assert_called_once()

    def test_get_metrics_route(self):
        """
        Prueba que la ruta /api/admin/metrics funciona correctamente.
        """
        expected_metrics = {"requests": 100}
        mock_metrics_manager = MagicMock()
        mock_metrics_manager.get_metrics.return_value = expected_metrics

        with self.app.app_context():
            # Adjuntar el mock al objeto de la aplicación actual
            self.app.metrics = mock_metrics_manager

            # Realizar la solicitud dentro del contexto de la aplicación
            response = self.client.get("/api/admin/metrics")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), expected_metrics)
        mock_metrics_manager.get_metrics.assert_called_once()

    def test_get_system_status_route(self):
        """
        Prueba que la ruta /api/admin/system-status funciona correctamente.
        """
        response = self.client.get("/api/admin/system-status")

        self.assertEqual(response.status_code, 200)
        self.assertIn("db", response.get_json())
        self.assertIn("cache", response.get_json())


if __name__ == "__main__":
    unittest.main()
