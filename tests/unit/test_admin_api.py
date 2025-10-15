import unittest
from unittest.mock import MagicMock, patch

from flask import Flask
from flask_jwt_extended import create_access_token

from app.api.admin import admin_bp
from app.config.extensions import db, jwt
from app.models import User


class TestAdminRoutes(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["SECRET_KEY"] = "test-secret-key"
        self.app.config["JWT_SECRET_KEY"] = "test-jwt-secret"
        self.app.config["JWT_TOKEN_LOCATION"] = ["headers"]
        self.app.config["JWT_HEADER_NAME"] = "Authorization"
        self.app.config["JWT_HEADER_TYPE"] = "Bearer"
        self.app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        # Registrar el blueprint
        self.app.register_blueprint(admin_bp, url_prefix="/api/admin")

        # Inicializar extensiones
        db.init_app(self.app)
        jwt.init_app(self.app)

        # Mocks de dependencias
        self.app.metrics = MagicMock()
        self.app.gemini_service = MagicMock()

        with self.app.app_context():
            db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    @patch("app.core.decorators.role_required")
    @patch("app.api.admin.get_security_summary")
    def test_get_security_summary_route(self, mock_get_security_summary, mock_role_required):
        # Mock role_required to bypass authentication
        mock_role_required.return_value = lambda f: f

        expected_summary = {
            "total_events": 0,
            "events_by_type": {},
            "events_by_severity": {},
            "unique_ips": 0,
            "top_endpoints": {},
        }
        mock_get_security_summary.return_value = expected_summary

        response = self.client.get("/api/admin/security-summary")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), expected_summary)
        mock_get_security_summary.assert_called_once()

    @patch("app.core.decorators.role_required")
    @patch("app.api.admin.metrics_manager")
    def test_get_metrics_route(self, mock_metrics_manager, mock_role_required):
        # Mock role_required to bypass authentication
        mock_role_required.return_value = lambda f: f

        expected_metrics = {
            "uptime_seconds": 0.0,
            "counters": {},
            "response_time_stats": {},
            "requests_per_minute": 0,
            "request_history_count": 0,
            "timestamp": 0.0,
        }
        mock_metrics_manager.get_metrics.return_value = expected_metrics

        response = self.client.get("/api/admin/metrics")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), expected_metrics)
        mock_metrics_manager.get_metrics.assert_called_once()

    @patch("app.core.decorators.role_required")
    @patch("app.api.admin.check_db_connection")
    def test_get_system_status_route(self, mock_check_db_connection, mock_role_required):
        # Mock role_required to bypass authentication
        mock_role_required.return_value = lambda f: f

        mock_check_db_connection.return_value = (True, "Database connection OK")

        response = self.client.get("/api/admin/status")

        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertIn("database", response_data)
        self.assertIn("ai_services", response_data)
        mock_check_db_connection.assert_called_once()


if __name__ == "__main__":
    unittest.main()
