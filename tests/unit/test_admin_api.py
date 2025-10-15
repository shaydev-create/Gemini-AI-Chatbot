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

        # Crear usuario admin y token
        with self.app.app_context():
            db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    @patch("app.api.admin.get_security_summary")
    def test_get_security_summary_route(self, mock_get_security_summary):
        expected_summary = {
            "total_events": 0,
            "events_by_type": {},
            "events_by_severity": {},
            "unique_ips": 0,
            "top_endpoints": {},
        }
        mock_get_security_summary.return_value = expected_summary

        with self.app.app_context():
            db.drop_all()
            db.create_all()
            # Create a test user with admin role
            test_user = User(
                username="admin_user",
                email="admin@test.com",
                role="admin",
                status="active",
            )
            test_user.set_password("Password123!")
            db.session.add(test_user)
            db.session.commit()

            # Create JWT token with proper identity format
            identity = {
                "user_id": test_user.id,
                "username": test_user.username,
                "role": test_user.role,
            }
            token = create_access_token(identity=identity)

            response = self.client.get(
                "/api/admin/security-summary",
                headers={"Authorization": f"Bearer {token}"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), expected_summary)
        mock_get_security_summary.assert_called_once()

    @patch("app.api.admin.metrics_manager")
    def test_get_metrics_route(self, mock_metrics_manager):
        expected_metrics = {
            "uptime_seconds": 0.0,
            "counters": {},
            "response_time_stats": {},
            "requests_per_minute": 0,
            "request_history_count": 0,
            "timestamp": 0.0,
        }
        mock_metrics_manager.get_metrics.return_value = expected_metrics

        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.create_all()
            # Create a test user with admin role
            test_user = User(
                username="admin_user",
                email="admin@test.com",
                role="admin",
                status="active",
            )
            test_user.set_password("Password123!")
            db.session.add(test_user)
            db.session.commit()

            # Create JWT token with proper identity format
            identity = {
                "user_id": test_user.id,
                "username": test_user.username,
                "role": test_user.role,
            }
            token = create_access_token(identity=identity)

            response = self.client.get(
                "/api/admin/metrics", headers={"Authorization": f"Bearer {token}"}
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), expected_metrics)
        mock_metrics_manager.get_metrics.assert_called_once()

    def test_get_system_status_route(self):
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            # Create a test user with admin role
            test_user = User(
                username="admin_user",
                email="admin@test.com",
                role="admin",
                status="active",
            )
            test_user.set_password("Password123!")
            db.session.add(test_user)
            db.session.commit()

            # Create JWT token with proper identity format
            identity = {
                "user_id": test_user.id,
                "username": test_user.username,
                "role": test_user.role,
            }
            token = create_access_token(identity=identity)

            response = self.client.get(
                "/api/admin/status",
                headers={"Authorization": f"Bearer {token}"},
            )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("database", data)
        self.assertIn("ai_services", data)
        self.assertIn("status", data["database"])
        self.assertIn("status", data["ai_services"])


if __name__ == "__main__":
    unittest.main()
