import unittest
from unittest.mock import MagicMock

from app.security import RateLimiter, SecurityManager, require_https, validate_input
from app.security import security_manager as global_security_manager
from flask import Flask, jsonify, request


class TestSecurityManager(unittest.TestCase):
    def setUp(self):
        self.manager = SecurityManager()

    def test_sanitize_input(self):
        self.assertEqual(
            self.manager.sanitize_input("<script>alert('xss')</script>"), "alert('xss')"
        )
        self.assertEqual(
            self.manager.sanitize_input("<b>Hello</b> World"), "<b>Hello</b> World"
        )
        self.assertEqual(
            self.manager.sanitize_input(" an evil input "), "an evil input"
        )
        self.assertEqual(self.manager.sanitize_input("a" * 10001), "a" * 10000)
        self.assertEqual(self.manager.sanitize_input(123), "")

    def test_validate_email(self):
        self.assertTrue(self.manager.validate_email("test@example.com"))
        self.assertFalse(self.manager.validate_email("invalid-email"))
        self.assertFalse(self.manager.validate_email("test@.com"))

    def test_validate_password(self):
        strong = self.manager.validate_password("Str0ngP@ss!")
        self.assertTrue(strong["valid"])
        self.assertEqual(strong["strength"], "strong")

        # This password meets all criteria but is less than 12 chars, so score is 3 -> strong
        medium = self.manager.validate_password("MedPass1!")
        self.assertTrue(medium["valid"])
        self.assertEqual(medium["strength"], "strong")

        weak = self.manager.validate_password("weak")
        self.assertFalse(weak["valid"])
        self.assertEqual(weak["strength"], "weak")
        self.assertIn("Mínimo 8 caracteres", weak["errors"])
        self.assertIn("Debe contener mayúsculas", weak["errors"])
        self.assertIn("Debe contener números", weak["errors"])

    def test_check_rate_limit(self):
        identifier = "127.0.0.1"
        for _ in range(5):
            self.assertTrue(
                self.manager.check_rate_limit(identifier, limit=5, window=60)
            )
        self.assertFalse(self.manager.check_rate_limit(identifier, limit=5, window=60))

    def test_detect_suspicious_activity(self):
        self.assertTrue(
            self.manager.detect_suspicious_activity({"comment": "SELECT * FROM users"})
        )
        self.assertTrue(
            self.manager.detect_suspicious_activity(
                {"post": "<script>alert(1)</script>"}
            )
        )
        self.assertFalse(
            self.manager.detect_suspicious_activity(
                {"comment": "This is a safe comment."}
            )
        )

    def test_csrf_token_generation_and_validation(self):
        token1 = self.manager.generate_csrf_token()
        token2 = self.manager.generate_csrf_token()
        self.assertNotEqual(token1, token2)
        self.assertTrue(self.manager.validate_csrf_token(token1, token1))
        self.assertFalse(self.manager.validate_csrf_token(token1, token2))

    def test_hash_data(self):
        hashed = self.manager.hash_data("my_secret_data")
        self.assertEqual(len(hashed), 64)
        self.assertNotEqual(hashed, "my_secret_data")

    def test_apply_security_headers(self):
        mock_response = MagicMock()
        mock_response.headers = {}
        self.manager.apply_security_headers(mock_response)
        self.assertIn("X-Content-Type-Options", mock_response.headers)
        self.assertEqual(mock_response.headers["X-Frame-Options"], "DENY")


class TestDecorators(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

        # Reset the global security manager's state for each test
        global_security_manager.rate_limits = {}

        @self.app.route("/limited")
        @RateLimiter(limit=2, window=60)
        def limited_route():
            return jsonify(success=True)

        @self.app.route("/secure", methods=["POST"])
        @require_https
        def secure_route():
            return jsonify(success=True)

        @self.app.route("/validated", methods=["POST"])
        @validate_input(schema={"comment": {"sanitize": True, "max_length": 20}})
        def validated_route():
            return jsonify(data=request.validated_data)

    def test_rate_limiter_decorator(self):
        with self.app.test_request_context("/limited"):
            response1 = self.client.get("/limited")
            self.assertEqual(response1.status_code, 200)
            response2 = self.client.get("/limited")
            self.assertEqual(response2.status_code, 200)
            response3 = self.client.get("/limited")
            self.assertEqual(response3.status_code, 429)

    def test_require_https_decorator(self):
        with self.app.test_request_context(
            "/secure", method="POST", base_url="http://localhost"
        ):
            response = self.client.post("/secure")
            self.assertEqual(response.status_code, 400)
            self.assertIn("HTTPS required", response.get_data(as_text=True))

        with self.app.test_request_context(
            "/secure", method="POST", base_url="https://localhost"
        ):
            # In a test environment, request.is_secure might still be false.
            # We can simulate the X-Forwarded-Proto header.
            response = self.client.post(
                "/secure", headers={"X-Forwarded-Proto": "https"}
            )
            self.assertEqual(response.status_code, 200)

    def test_validate_input_decorator_sanitization(self):
        # Test sanitization of non-suspicious HTML
        with self.app.test_request_context(
            "/validated", method="POST", json={"comment": "<b>innocent</b>"}
        ):
            view_func = self.app.view_functions["validated_route"]
            response = view_func()
            # On success, the decorator passes through, and the view returns a Response object
            self.assertEqual(response.status_code, 200)
            json_data = response.get_json()
            self.assertEqual(json_data["data"]["comment"], "<b>innocent</b>")

    def test_validate_input_decorator_suspicious_activity(self):
        with self.app.test_request_context(
            "/validated", method="POST", json={"comment": "SELECT * FROM users"}
        ):
            view_func = self.app.view_functions["validated_route"]
            # On suspicious activity, the decorator returns a tuple (response, status_code)
            response, status_code = view_func()
            self.assertEqual(status_code, 400)
            self.assertIn(
                "Suspicious activity detected", response.get_data(as_text=True)
            )


if __name__ == "__main__":
    unittest.main()
