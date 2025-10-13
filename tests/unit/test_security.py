import time
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

# Asumimos que app.core.security está en el path.
# Si no, necesitaríamos ajustar el sys.path, pero pytest suele manejarlo.
from app.core.security import (
    DataEncryption,
    LoginAttemptTracker,
    RateLimiter,
    SecurityAuditor,
    SecurityEvent,
    SecurityManager,
    TokenManager,
)

# --- Pruebas para TokenManager ---


@pytest.fixture
def token_manager():
    """Fixture para un TokenManager con una clave secreta de prueba."""
    return TokenManager(secret_key="test-secret", expiration_hours=1)


def test_token_manager_generate_and_verify(token_manager):
    """Prueba la generación y verificación de un token válido."""
    token = token_manager.generate_token("user-123")
    assert isinstance(token, str)

    payload = token_manager.verify_token(token)
    assert payload is not None
    assert payload["user_id"] == "user-123"


def test_token_manager_expired_token(token_manager):
    """Prueba que un token expirado no se verifica."""
    # Generar un token con expiración de -1 hora
    token_manager.expiration_hours = -1
    expired_token = token_manager.generate_token("user-123")

    payload = token_manager.verify_token(expired_token)
    assert payload is None


def test_token_manager_invalid_signature(token_manager):
    """Prueba que un token con firma inválida no se verifica."""
    token = token_manager.generate_token("user-123")

    # Intentar verificar con una clave secreta diferente
    wrong_key_manager = TokenManager(secret_key="wrong-secret")
    payload = wrong_key_manager.verify_token(token)
    assert payload is None


def test_token_manager_blacklist(token_manager):
    """Prueba que un token en lista negra no se verifica."""
    token = token_manager.generate_token("user-123")

    # El token es válido al principio
    assert token_manager.verify_token(token) is not None

    # Añadir a la lista negra y verificar de nuevo
    token_manager.blacklist_token(token)
    assert token_manager.verify_token(token) is None


# --- Pruebas para RateLimiter ---


@pytest.fixture
def rate_limiter():
    """Fixture para un RateLimiter con configuración de prueba."""
    return RateLimiter(max_requests=5, window_minutes=1)


def test_rate_limiter_allows_under_limit(rate_limiter):
    """Prueba que se permiten las peticiones por debajo del límite."""
    identifier = "ip-1.1.1.1"
    for i in range(5):
        assert rate_limiter.is_allowed(identifier) is True
        assert rate_limiter.get_remaining_requests(identifier) == 5 - (i + 1)


def test_rate_limiter_blocks_over_limit(rate_limiter):
    """Prueba que se bloquean las peticiones por encima del límite."""
    identifier = "ip-2.2.2.2"
    for _ in range(5):
        rate_limiter.is_allowed(identifier)

    assert rate_limiter.is_allowed(identifier) is False
    assert rate_limiter.get_remaining_requests(identifier) == 0


def test_rate_limiter_resets_after_window(rate_limiter):
    """Prueba que el contador se resetea después de la ventana de tiempo."""
    identifier = "ip-3.3.3.3"
    rate_limiter.window_seconds = 1  # Usar una ventana corta para el test

    for _ in range(5):
        rate_limiter.is_allowed(identifier)

    assert rate_limiter.is_allowed(identifier) is False

    time.sleep(1.1)  # Esperar a que la ventana expire

    assert rate_limiter.is_allowed(identifier) is True
    assert rate_limiter.get_remaining_requests(identifier) == 4


# --- Pruebas para LoginAttemptTracker ---


@pytest.fixture
def login_tracker():
    """Fixture para un LoginAttemptTracker con configuración de prueba."""
    return LoginAttemptTracker(max_attempts=3, lockout_minutes=1)


def test_login_tracker_locks_after_max_attempts(login_tracker):
    """Prueba que la cuenta se bloquea tras varios intentos fallidos."""
    identifier = "user-a"
    assert login_tracker.is_locked(identifier) is False

    login_tracker.record_failed_attempt(identifier)
    login_tracker.record_failed_attempt(identifier)
    assert login_tracker.is_locked(identifier) is False

    login_tracker.record_failed_attempt(identifier)
    assert login_tracker.is_locked(identifier) is True
    assert login_tracker.get_lockout_time_remaining(identifier) > 0


def test_login_tracker_resets_on_success(login_tracker):
    """Prueba que un login exitoso resetea el contador de fallos."""
    identifier = "user-b"
    login_tracker.record_failed_attempt(identifier)
    login_tracker.record_failed_attempt(identifier)

    login_tracker.record_successful_attempt(identifier)

    login_tracker.record_failed_attempt(identifier)
    assert login_tracker.is_locked(identifier) is False


def test_login_tracker_unlocks_after_time(login_tracker):
    """Prueba que el bloqueo expira después del tiempo de lockout."""
    identifier = "user-c"
    login_tracker.lockout_seconds = 1  # Ventana corta para el test

    for _ in range(3):
        login_tracker.record_failed_attempt(identifier)

    assert login_tracker.is_locked(identifier) is True

    time.sleep(1.1)

    assert login_tracker.is_locked(identifier) is False


# --- Pruebas para SecurityAuditor ---


@pytest.fixture
def auditor():
    """Fixture para un SecurityAuditor."""
    return SecurityAuditor()


def test_auditor_logs_event(auditor):
    """Prueba que los eventos de seguridad se registran correctamente."""
    event = SecurityEvent(
        event_type="test_event",
        timestamp=datetime.now(timezone.utc),
        user_id="test_user",
    )
    auditor.log_event(event)

    summary = auditor.get_security_summary()
    assert summary["total_events"] == 1
    assert summary["events_by_type"]["test_event"] == 1


@pytest.mark.parametrize(
    "request_data, expected_threats",
    [
        ("SELECT * FROM users WHERE name = 'admin' --", ["sql_injection"]),
        ("SELECT * FROM users WHERE name = '' OR '1'='1'", ["sql_injection"]),
        ("<script>window.location='http://evil.com'</script>", ["xss"]),
        ("some normal data", []),
    ],
)
def test_auditor_analyzes_request(auditor, request_data, expected_threats):
    """Prueba la detección de amenazas en los datos de una petición."""
    threats = auditor.analyze_request(request_data)
    assert threats == expected_threats


# --- Pruebas para DataEncryption (si cryptography está disponible) ---
@pytest.mark.skipif(
    not DataEncryption(password="test").key,
    reason="cryptography library not available or failed to init",
)
def test_data_encryption_encrypt_decrypt():
    """Prueba el ciclo completo de encriptación y desencriptación."""
    encrypter = DataEncryption(password="super-secret")
    original_data = "Esta es información muy sensible."

    encrypted = encrypter.encrypt(original_data)
    assert encrypted != original_data

    decrypted = encrypter.decrypt(encrypted)
    assert decrypted == original_data


# --- Pruebas para SecurityManager (integración de componentes) ---


@pytest.fixture
def security_manager():
    """Fixture para un SecurityManager completo con mocks."""
    # Mock de la configuración para no depender de archivos externos
    mock_config = MagicMock()
    mock_config.jwt_secret_key = "manager-secret"
    mock_config.jwt_expiration_hours = 1
    mock_config.rate_limit_per_minute = 10
    mock_config.max_login_attempts = 3
    mock_config.lockout_duration_minutes = 1

    with patch("app.core.security.get_current_config") as mock_get_config:
        mock_get_config.return_value.security = mock_config
        manager = SecurityManager(config=mock_config)
        # Mock de la verificación de credenciales para aislar el test
        manager._verify_user_credentials = MagicMock(return_value=True)
        yield manager


def test_security_manager_successful_authentication(security_manager):
    """Prueba un flujo de autenticación exitoso."""
    token = security_manager.authenticate_user("testuser", "password")
    assert token is not None

    payload = security_manager.verify_token(token)
    assert payload["user_id"] == "testuser"


def test_security_manager_failed_authentication(security_manager):
    """Prueba un flujo de autenticación fallido."""
    # Configurar el mock para que la verificación de credenciales falle
    security_manager._verify_user_credentials.return_value = False

    with pytest.raises(Exception, match="Invalid credentials"):
        security_manager.authenticate_user("testuser", "wrong_password")


def test_security_manager_account_lockout(security_manager):
    """Prueba que el SecurityManager bloquea una cuenta."""
    security_manager._verify_user_credentials.return_value = False

    # Intentos fallidos
    with pytest.raises(Exception):
        security_manager.authenticate_user("locked_user", "p1")
    with pytest.raises(Exception):
        security_manager.authenticate_user("locked_user", "p2")
    with pytest.raises(Exception):
        security_manager.authenticate_user("locked_user", "p3")

    # Siguiente intento debería fallar por bloqueo
    with pytest.raises(Exception, match="Account locked"):
        security_manager.authenticate_user("locked_user", "p4")
