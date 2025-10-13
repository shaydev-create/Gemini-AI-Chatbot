"""
Sistema de seguridad avanzado para la aplicación Flask.

Este módulo proporciona:
- Autenticación y autorización
- Gestión de tokens JWT
- Rate limiting
- Protección CSRF
- Sanitización de entrada
- Auditoría de seguridad
- Detección de amenazas
- Encriptación de datos
"""

import re
import secrets
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

import jwt
from flask import Flask, g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

# Intentar importar dependencias opcionales
try:
    import base64

    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    Fernet = None

try:
    from ..error_handler import AuthenticationError, AuthorizationError, error_handler
except ImportError:
    class AuthenticationError(Exception):
        pass
    class AuthorizationError(Exception):
        pass
    error_handler = None

try:
    from ..logging_system import get_logger
except ImportError:
    import logging
    get_logger = logging.getLogger

try:
    from ...config.settings import get_current_config
except ImportError:
    def get_current_config():
        """
        Devuelve una configuración simulada para cuando la app no está completamente inicializada.
        """
        class SecurityConfig:
            """Configuración de seguridad simulada."""
            jwt_secret_key = "your-secret-key"
            jwt_expiration_hours = 24
            rate_limit_per_minute = 60
            max_login_attempts = 5
            lockout_duration_minutes = 15
            password_min_length = 8
            session_timeout_minutes = 30

        class Config:
            """Clase de configuración principal simulada."""
            security = SecurityConfig()

        return Config()


@dataclass
class SecurityEvent:
    """Evento de seguridad."""
    event_type: str
    timestamp: datetime
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    severity: str = "info"  # info, warning, error, critical
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "endpoint": self.endpoint,
            "severity": self.severity,
            "details": self.details
        }


class TokenManager:
    """Gestor de tokens JWT."""

    def __init__(self, secret_key: str, expiration_hours: int = 24):
        self.secret_key = secret_key
        self.expiration_hours = expiration_hours
        self.algorithm = "HS256"
        self.blacklisted_tokens = set()
        self.logger = get_logger(__name__)

    def generate_token(self, user_id: str, additional_claims: Optional[Dict[str, Any]] = None) -> str:
        """Generar token JWT."""
        now = datetime.now(timezone.utc)
        payload = {
            "user_id": user_id,
            "iat": now,
            "exp": now + timedelta(hours=self.expiration_hours),
            "jti": secrets.token_urlsafe(16)  # JWT ID único
        }

        if additional_claims:
            payload.update(additional_claims)

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

        self.logger.info(f"Token generated for user {user_id}")
        return token

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verificar y decodificar token JWT."""
        try:
            # Verificar si el token está en la lista negra
            if token in self.blacklisted_tokens:
                self.logger.warning("Attempted use of blacklisted token")
                return None

            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            return payload

        except jwt.ExpiredSignatureError:
            self.logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            self.logger.warning(f"Invalid token: {e}")
            return None

    def blacklist_token(self, token: str):
        """Agregar token a lista negra."""
        self.blacklisted_tokens.add(token)
        self.logger.info("Token blacklisted")

    def refresh_token(self, token: str) -> Optional[str]:
        """Refrescar token si está cerca de expirar."""
        payload = self.verify_token(token)
        if not payload:
            return None

        # Verificar si el token expira en menos de 1 hora
        exp_time = datetime.fromtimestamp(payload['exp'], tz=timezone.utc)
        if exp_time - datetime.now(timezone.utc) < timedelta(hours=1):
            # Invalidar token actual
            self.blacklist_token(token)

            # Generar nuevo token
            return self.generate_token(
                payload['user_id'],
                {k: v for k, v in payload.items() if k not in ['iat', 'exp', 'jti']}
            )

        return token


class RateLimiter:
    """Limitador de tasa de requests."""

    def __init__(self, max_requests: int = 60, window_minutes: int = 1):
        self.max_requests = max_requests
        self.window_seconds = window_minutes * 60
        self.requests = defaultdict(deque)
        self.lock = threading.Lock()
        self.logger = get_logger(__name__)

    def is_allowed(self, identifier: str) -> bool:
        """Verificar si el request está permitido."""
        with self.lock:
            now = time.time()

            # Limpiar requests antiguos
            while (self.requests[identifier] and
                   now - self.requests[identifier][0] > self.window_seconds):
                self.requests[identifier].popleft()

            # Verificar límite
            if len(self.requests[identifier]) >= self.max_requests:
                self.logger.warning(f"Rate limit exceeded for {identifier}")
                return False

            # Agregar request actual
            self.requests[identifier].append(now)
            return True

    def get_remaining_requests(self, identifier: str) -> int:
        """Obtener requests restantes."""
        with self.lock:
            now = time.time()

            # Limpiar requests antiguos
            while (self.requests[identifier] and
                   now - self.requests[identifier][0] > self.window_seconds):
                self.requests[identifier].popleft()

            return max(0, self.max_requests - len(self.requests[identifier]))

    def reset_limit(self, identifier: str):
        """Resetear límite para un identificador."""
        with self.lock:
            if identifier in self.requests:
                del self.requests[identifier]


class LoginAttemptTracker:
    """Rastreador de intentos de login."""

    def __init__(self, max_attempts: int = 5, lockout_minutes: int = 15):
        self.max_attempts = max_attempts
        self.lockout_seconds = lockout_minutes * 60
        self.attempts = defaultdict(list)
        self.lockouts = {}
        self.lock = threading.Lock()
        self.logger = get_logger(__name__)

    def record_failed_attempt(self, identifier: str):
        """Registrar intento fallido."""
        with self.lock:
            now = time.time()

            # Limpiar intentos antiguos
            cutoff = now - self.lockout_seconds
            self.attempts[identifier] = [
                attempt for attempt in self.attempts[identifier]
                if attempt > cutoff
            ]

            # Agregar intento actual
            self.attempts[identifier].append(now)

            # Verificar si se debe bloquear
            if len(self.attempts[identifier]) >= self.max_attempts:
                self.lockouts[identifier] = now + self.lockout_seconds
                self.logger.warning(f"Account locked due to failed attempts: {identifier}")

    def record_successful_attempt(self, identifier: str):
        """Registrar intento exitoso."""
        with self.lock:
            # Limpiar intentos fallidos
            if identifier in self.attempts:
                del self.attempts[identifier]

            # Remover bloqueo si existe
            if identifier in self.lockouts:
                del self.lockouts[identifier]

    def is_locked(self, identifier: str) -> bool:
        """Verificar si la cuenta está bloqueada."""
        with self.lock:
            if identifier not in self.lockouts:
                return False

            # Verificar si el bloqueo ha expirado
            if time.time() > self.lockouts[identifier]:
                del self.lockouts[identifier]
                return False

            return True

    def get_lockout_time_remaining(self, identifier: str) -> int:
        """Obtener tiempo restante de bloqueo en segundos."""
        with self.lock:
            if identifier not in self.lockouts:
                return 0

            remaining = self.lockouts[identifier] - time.time()
            return max(0, int(remaining))


class DataEncryption:
    """Encriptación de datos."""

    def __init__(self, password: Optional[str] = None):
        if not CRYPTOGRAPHY_AVAILABLE:
            raise ImportError("cryptography library is required for encryption")

        if password:
            self.key = self._derive_key(password.encode())
        else:
            self.key = Fernet.generate_key()

        self.cipher = Fernet(self.key)

    def _derive_key(self, password: bytes) -> bytes:
        """Derivar clave de encriptación desde password."""
        salt = b'salt_1234567890'  # En producción, usar salt aleatorio
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key

    def encrypt(self, data: str) -> str:
        """Encriptar datos."""
        encrypted_data = self.cipher.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Desencriptar datos."""
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt data: {e}")


class SecurityAuditor:
    """Auditor de seguridad."""

    def __init__(self):
        self.events: List[SecurityEvent] = []
        self.lock = threading.Lock()
        self.logger = get_logger(__name__)
        self.threat_patterns = {
            "sql_injection": [r"union\s+select", r"drop\s+table", r"insert\s+into", r"' or '1'='1'", r"--"],
            "xss": [r"<script", r"javascript:", r"onerror="],
            "path_traversal": [r"\.\./", r"\\\.\.\\"]
        }

    def log_event(self, event: SecurityEvent):
        """Registrar evento de seguridad."""
        with self.lock:
            self.events.append(event)

            # Mantener solo los últimos 1000 eventos
            if len(self.events) > 1000:
                self.events = self.events[-1000:]

        # Log del evento
        log_level = {
            "info": "info",
            "warning": "warning",
            "error": "error",
            "critical": "critical"
        }.get(event.severity, "info")

        getattr(self.logger, log_level)(
            f"Security event: {event.event_type}",
            extra={"security_event": event.to_dict()}
        )

    def analyze_request(self, request_data: str) -> List[str]:
        """Analizar request en busca de amenazas."""
        threats = []
        request_lower = request_data.lower()

        for threat_type, patterns in self.threat_patterns.items():
            for pattern in patterns:
                if re.search(pattern, request_lower, re.IGNORECASE):
                    threats.append(threat_type)
                    break

        return threats

    def get_security_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Obtener resumen de seguridad."""
        with self.lock:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
            recent_events = [
                event for event in self.events
                if event.timestamp > cutoff
            ]

            summary = {
                "total_events": len(recent_events),
                "events_by_type": defaultdict(int),
                "events_by_severity": defaultdict(int),
                "unique_ips": set(),
                "top_endpoints": defaultdict(int)
            }

            for event in recent_events:
                summary["events_by_type"][event.event_type] += 1
                summary["events_by_severity"][event.severity] += 1

                if event.ip_address:
                    summary["unique_ips"].add(event.ip_address)

                if event.endpoint:
                    summary["top_endpoints"][event.endpoint] += 1

            # Convertir sets a listas para serialización
            summary["unique_ips"] = len(summary["unique_ips"])
            summary["events_by_type"] = dict(summary["events_by_type"])
            summary["events_by_severity"] = dict(summary["events_by_severity"])
            summary["top_endpoints"] = dict(summary["top_endpoints"])

            return summary


class SecurityManager:
    """Gestor principal de seguridad."""

    def __init__(self, config=None):
        self.config = config or get_current_config().security
        self.token_manager = TokenManager(
            self.config.jwt_secret_key,
            self.config.jwt_expiration_hours
        )
        self.rate_limiter = RateLimiter(
            self.config.rate_limit_per_minute
        )
        self.login_tracker = LoginAttemptTracker(
            self.config.max_login_attempts,
            self.config.lockout_duration_minutes
        )
        self.auditor = SecurityAuditor()
        self.logger = get_logger(__name__)

        # Encriptación opcional
        self.encryption = None
        if CRYPTOGRAPHY_AVAILABLE:
            try:
                self.encryption = DataEncryption()
            except Exception as e:
                self.logger.warning(f"Could not initialize encryption: {e}")

    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """Autenticar usuario."""
        identifier = f"login_{username}"

        # Verificar si la cuenta está bloqueada
        if self.login_tracker.is_locked(identifier):
            remaining = self.login_tracker.get_lockout_time_remaining(identifier)
            self.auditor.log_event(SecurityEvent(
                event_type="login_attempt_blocked",
                timestamp=datetime.now(timezone.utc),
                user_id=username,
                severity="warning",
                details={"lockout_remaining_seconds": remaining}
            ))
            raise AuthenticationError(f"Account locked. Try again in {remaining} seconds.")

        # Aquí iría la verificación real del usuario/password
        # Por ahora, simulamos la verificación
        user_valid = self._verify_user_credentials(username, password)

        if user_valid:
            self.login_tracker.record_successful_attempt(identifier)
            token = self.token_manager.generate_token(username)

            self.auditor.log_event(SecurityEvent(
                event_type="login_success",
                timestamp=datetime.now(timezone.utc),
                user_id=username,
                severity="info"
            ))

            return token
        else:
            self.login_tracker.record_failed_attempt(identifier)

            self.auditor.log_event(SecurityEvent(
                event_type="login_failed",
                timestamp=datetime.now(timezone.utc),
                user_id=username,
                severity="warning"
            ))

            raise AuthenticationError("Invalid credentials")

    def _verify_user_credentials(self, username: str, password: str) -> bool:
        """Verificar credenciales de usuario (implementar según tu sistema)."""
        # Implementar verificación real aquí
        # Por ejemplo, consultar base de datos
        return True  # Placeholder

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verificar token de autenticación."""
        payload = self.token_manager.verify_token(token)

        if payload:
            self.auditor.log_event(SecurityEvent(
                event_type="token_verified",
                timestamp=datetime.now(timezone.utc),
                user_id=payload.get('user_id'),
                severity="info"
            ))
        else:
            self.auditor.log_event(SecurityEvent(
                event_type="token_verification_failed",
                timestamp=datetime.now(timezone.utc),
                severity="warning"
            ))

        return payload

    def check_rate_limit(self, identifier: str) -> bool:
        """Verificar límite de tasa."""
        allowed = self.rate_limiter.is_allowed(identifier)

        if not allowed:
            self.auditor.log_event(SecurityEvent(
                event_type="rate_limit_exceeded",
                timestamp=datetime.now(timezone.utc),
                severity="warning",
                details={"identifier": identifier}
            ))

        return allowed

    def analyze_request_security(self, request_data: str) -> List[str]:
        """Analizar seguridad del request."""
        threats = self.auditor.analyze_request(request_data)

        if threats:
            self.auditor.log_event(SecurityEvent(
                event_type="security_threat_detected",
                timestamp=datetime.now(timezone.utc),
                severity="error",
                details={"threats": threats, "request_data": request_data[:100]}
            ))

        return threats


# Instancia global del gestor de seguridad
security_manager = SecurityManager()


# Decoradores de seguridad
def require_auth(func: Callable) -> Callable:
    """Decorador para requerir autenticación."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            if error_handler:
                context = error_handler.handle_error(
                    AuthenticationError("Missing or invalid authorization header")
                )
                response_data, status_code = error_handler.create_error_response(context)
                return jsonify(response_data), status_code
            else:
                return jsonify({"error": "Authentication required"}), 401

        token = auth_header.split(' ')[1]
        payload = security_manager.verify_token(token)

        if not payload:
            if error_handler:
                context = error_handler.handle_error(
                    AuthenticationError("Invalid or expired token")
                )
                response_data, status_code = error_handler.create_error_response(context)
                return jsonify(response_data), status_code
            else:
                return jsonify({"error": "Invalid token"}), 401

        # Agregar información del usuario al contexto
        g.current_user = payload
        g.user_id = payload.get('user_id')

        return func(*args, **kwargs)

    return wrapper


def require_role(required_role: str):
    """Decorador para requerir rol específico."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not hasattr(g, 'current_user') or not g.current_user:
                if error_handler:
                    context = error_handler.handle_error(
                        AuthenticationError("Authentication required")
                    )
                    response_data, status_code = error_handler.create_error_response(context)
                    return jsonify(response_data), status_code
                else:
                    return jsonify({"error": "Authentication required"}), 401

            user_roles = g.current_user.get('roles', [])

            if required_role not in user_roles:
                if error_handler:
                    context = error_handler.handle_error(
                        AuthorizationError(f"Role '{required_role}' required")
                    )
                    response_data, status_code = error_handler.create_error_response(context)
                    return jsonify(response_data), status_code
                else:
                    return jsonify({"error": "Insufficient permissions"}), 403

            return func(*args, **kwargs)

        return wrapper
    return decorator


def rate_limit(identifier_func: Optional[Callable] = None):
    """Decorador para rate limiting."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Determinar identificador
            if identifier_func:
                identifier = identifier_func()
            else:
                identifier = request.remote_addr or "unknown"

            if not security_manager.check_rate_limit(identifier):
                return jsonify({
                    "error": "Rate limit exceeded",
                    "retry_after": 60
                }), 429

            return func(*args, **kwargs)

        return wrapper
    return decorator


def security_headers(func: Callable) -> Callable:
    """Decorador para agregar headers de seguridad."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)

        # Agregar headers de seguridad
        if hasattr(response, 'headers'):
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            response.headers['Content-Security-Policy'] = "default-src 'self'"

        return response

    return wrapper


def setup_security(app: Flask):
    """Configurar seguridad para la aplicación Flask."""

    @app.before_request
    def security_middleware():
        """Middleware de seguridad."""
        # Analizar amenazas en el request
        request_data = str(request.get_data())
        threats = security_manager.analyze_request_security(request_data)

        if threats:
            security_manager.auditor.log_event(SecurityEvent(
                event_type="request_blocked",
                timestamp=datetime.now(timezone.utc),
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                endpoint=request.endpoint,
                severity="error",
                details={"threats": threats}
            ))

            return jsonify({
                "error": "Request blocked due to security concerns"
            }), 400

    # Configurar headers de seguridad globales
    @app.after_request
    def add_security_headers(response):
        """Agregar headers de seguridad a todas las respuestas."""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    return app


# Funciones de conveniencia
def hash_password(password: str) -> str:
    """Hash de password."""
    return generate_password_hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verificar password."""
    return check_password_hash(password_hash, password)


def generate_csrf_token() -> str:
    """Generar token CSRF."""
    return secrets.token_urlsafe(32)


def get_security_summary() -> Dict[str, Any]:
    """Obtener resumen de seguridad."""
    return security_manager.auditor.get_security_summary()


# Configurar logging básico si se ejecuta directamente
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = get_logger(__name__)
    logger.info("Sistema de seguridad inicializado")
