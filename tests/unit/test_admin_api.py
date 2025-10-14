import unittest
from unittest.mock import MagicMock, patch

from app.api.admin import admin_bp
from app.config.extensions import db, jwt
from app.models import User
from flask import Flask
from flask_jwt_extended import create_access_token


class TestAdminRoutes(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        # Configuración mínima necesaria para JWT y la aplicación
        self.app.config["TESTING"] = True
        self.app.config["SECRET_KEY"] = "test-secret-key"
        self.app.config["JWT_SECRET_KEY"] = "test-jwt-secret"
        self.app.config["JWT_TOKEN_LOCATION"] = ["headers"]
        self.app.config["JWT_HEADER_NAME"] = "Authorization"
        self.app.config["JWT_HEADER_TYPE"] = "Bearer"
        self.app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False  # Deshabilitar expiración para tests
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        # Registrar el blueprint
        self.app.register_blueprint(admin_bp, url_prefix="/api/admin")

        # Inicializar extensiones
        db.init_app(self.app)
        jwt.init_app(self.app)

        # Configurar mocks para las dependencias que requieren inicialización
        self.app.metrics = MagicMock()
        self.app.gemini_service = MagicMock()

        # Crear un usuario de prueba en la base de datos
        with self.app.app_context():
            # Crear todas las tablas de la base de datos
            db.create_all()

            # Crear un usuario admin de prueba
            test_user = User(
                username="test-admin",
                email="admin@test.com",
                status="active"
            )
            test_user.set_password("Testpassword123!")
            db.session.add(test_user)
            db.session.commit()

            # Crear un token JWT válido para las pruebas (con rol admin)
            identity = {
                "user_id": test_user.id,
                "username": "test-admin",
                "role": "admin"  # Rol admin para acceder a las rutas de administración
            }
            self.valid_token = create_access_token(identity=identity)

        self.client = self.app.test_client()

    @patch("app.api.admin.get_security_summary")
    def test_get_security_summary_route(self, mock_get_security_summary):
        """
        Prueba que la ruta /api/admin/security-summary funciona correctamente.
        """
        expected_summary = {
            "total_events": 0,
            "events_by_type": {},
            "events_by_severity": {},
            "unique_ips": 0,
            "top_endpoints": {}
        }
        mock_get_security_summary.return_value = expected_summary

        response = self.client.get("/api/admin/security-summary", headers={"Authorization": f"Bearer {self.valid_token}"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), expected_summary)
        mock_get_security_summary.assert_called_once()

    @patch("app.api.admin.metrics_manager")
    def test_get_metrics_route(self, mock_metrics_manager):
        """
        Prueba que la ruta /api/admin/metrics funciona correctamente.
        """
        expected_metrics = {
            "uptime_seconds": 0.0,
            "counters": {},
            "response_time_stats": {},
            "requests_per_minute": 0,
            "request_history_count": 0,
            "timestamp": 0.0
        }
        mock_metrics_manager.get_metrics.return_value = expected_metrics

        response = self.client.get("/api/admin/metrics", headers={"Authorization": f"Bearer {self.valid_token}"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), expected_metrics)
        mock_metrics_manager.get_metrics.assert_called_once()

    def test_get_system_status_route(self):
        """
        Prueba que la ruta /api/admin/status funciona correctamente.
        """
        response = self.client.get("/api/admin/status", headers={"Authorization": f"Bearer {self.valid_token}"})

        self.assertEqual(response.status_code, 200)
        self.assertIn("database", response.get_json())
        self.assertIn("ai_services", response.get_json())

    def tearDown(self):
        """Limpiar la base de datos después de cada test"""
        with self.app.app_context():
            # Eliminar todos los usuarios de prueba
            User.query.delete()
            db.session.commit()


if __name__ == "__main__":
    unittest.main()
