from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from flask import Flask, make_response

from app.core.security import (
    DataEncryption,
    RateLimiter,
    SecurityAuditor,
    SecurityEvent,
    TokenManager,
    generate_csrf_token,
    get_security_summary,
    hash_password,
    rate_limit,
    security_headers,
    setup_security,
    verify_password,
)

# --- Pruebas para TokenManager ---


def test_token_refresh_logic():
    """Prueba la lógica de refresco de un token JWT."""
    manager = TokenManager(secret_key="super-secret", expiration_hours=1)

    # 1. Generar un token original
    user_id = "user-123"
    original_token = manager.generate_token(user_id)

    # 2. Simular que el tiempo ha pasado y el token está a punto de expirar
    # Modificamos la fecha de expiración para que esté en el pasado cercano
    payload = manager.verify_token(original_token)
    payload["exp"] = (datetime.now(timezone.utc) - timedelta(minutes=30)).timestamp()

    with patch("app.core.security.jwt.decode", return_value=payload):
        with patch.object(manager, "blacklist_token") as mock_blacklist:
            # 3. Intentar refrescar el token
            refreshed_token = manager.refresh_token(original_token)

            # 4. Verificar que se generó un nuevo token y se invalidó el anterior
            assert refreshed_token is not None
            assert refreshed_token != original_token
            mock_blacklist.assert_called_once_with(original_token)

            # 5. Verificar que el nuevo token es válido
            new_payload = manager.verify_token(refreshed_token)
            assert new_payload is not None
            assert new_payload["user_id"] == user_id


def test_token_no_refresh_needed():
    """Prueba que el token no se refresca si no está cerca de expirar."""
    manager = TokenManager(secret_key="super-secret", expiration_hours=24)
    token = manager.generate_token("user-123")

    with patch.object(manager, "blacklist_token") as mock_blacklist:
        refreshed_token = manager.refresh_token(token)
        assert refreshed_token == token
        mock_blacklist.assert_not_called()


# --- Pruebas para RateLimiter ---


def test_rate_limiter_reset():
    """Prueba que el límite de tasa se puede resetear para un identificador."""
    limiter = RateLimiter(max_requests=2, window_minutes=1)
    identifier = "test-reset"

    assert limiter.is_allowed(identifier) is True
    assert limiter.is_allowed(identifier) is True
    assert limiter.is_allowed(identifier) is False  # Límite alcanzado

    limiter.reset_limit(identifier)

    assert limiter.is_allowed(identifier) is True  # Puede hacer requests de nuevo


# --- Pruebas para DataEncryption ---


def test_decryption_failure():
    """Prueba que la desencriptación falla con datos inválidos."""
    if not DataEncryption:
        pytest.skip("cryptography is not installed")

    encryptor = DataEncryption("my-password")
    invalid_data = "this-is-not-valid-encrypted-data"

    with pytest.raises(ValueError, match="Failed to decrypt data"):
        encryptor.decrypt(invalid_data)


# --- Pruebas para SecurityAuditor ---


def test_auditor_event_pruning():
    """Prueba que el auditor de seguridad purga los eventos antiguos."""
    auditor = SecurityAuditor()

    # Forzar el límite de eventos a un número bajo para la prueba
    with patch.object(auditor, "events", []):
        for i in range(1010):
            auditor.log_event(SecurityEvent(event_type=f"event_{i}", timestamp=datetime.now(timezone.utc)))

        assert len(auditor.events) == 1000
        assert auditor.events[0].event_type == "event_10"
        assert auditor.events[-1].event_type == "event_1009"


# --- Pruebas para Decoradores y Funciones de Utilidad ---


@pytest.fixture
def app_for_decorators():
    """Crea una instancia de Flask para probar decoradores."""
    app = Flask(__name__)
    app.config["TESTING"] = True

    @app.route("/limited")
    @rate_limit(identifier_func=lambda: "test-decorator")
    def limited_route():
        return "Success", 200

    @app.route("/secure-headers")
    @security_headers
    def secure_headers_route():
        return make_response("Content with headers")

    setup_security(app)
    return app


def test_rate_limit_decorator(app_for_decorators):
    """Prueba el decorador @rate_limit."""
    client = app_for_decorators.test_client()

    # Simular que el límite se excede
    with patch("app.core.security.security_manager.check_rate_limit", return_value=False):
        response = client.get("/limited")
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json["error"]


def test_security_headers_decorator(app_for_decorators):
    """Prueba el decorador @security_headers."""
    client = app_for_decorators.test_client()
    response = client.get("/secure-headers")

    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-XSS-Protection"] == "1; mode=block"
    assert "Strict-Transport-Security" in response.headers
    assert "Content-Security-Policy" in response.headers


def test_setup_security_middleware(app_for_decorators):
    """Prueba que el middleware de seguridad bloquea requests maliciosos."""
    client = app_for_decorators.test_client()

    # Simular una amenaza detectada
    with patch(
        "app.core.security.security_manager.analyze_request_security",
        return_value=["sql_injection"],
    ):
        response = client.post("/secure-headers", data="<script>alert('xss')</script>")
        assert response.status_code == 400
        assert "Request blocked" in response.json["error"]


def test_password_hashing_and_verification():
    """Prueba el hashing y la verificación de contraseñas."""
    password = "MyStrongPassword123!"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_generate_csrf_token():
    """Prueba la generación de tokens CSRF."""
    token1 = generate_csrf_token()
    token2 = generate_csrf_token()

    assert isinstance(token1, str)
    assert len(token1) > 30
    assert token1 != token2


def test_get_security_summary_wrapper():
    """Prueba la función de conveniencia get_security_summary."""
    with patch("app.core.security.security_manager.auditor.get_security_summary") as mock_summary:
        mock_summary.return_value = {"total_events": 5}
        summary = get_security_summary()

        assert summary["total_events"] == 5
        mock_summary.assert_called_once()
