#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de seguridad para Gemini AI Chatbot.
Implementa validación, sanitización, rate limiting y protecciones de seguridad.
"""

import hashlib
import re
import secrets
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Any, Dict, List

import bleach
from flask import g, jsonify, request


class SecurityManager:
    """Gestor principal de seguridad."""

    def __init__(self):
        self.rate_limits = {}
        self.blocked_ips = set()
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }

    def sanitize_input(self, text: str, max_length: int = 10000) -> str:
        """Sanitizar entrada de usuario."""
        if not isinstance(text, str):
            return ""

        # Limitar longitud
        text = text[:max_length]

        # Limpiar con bleach (escapa caracteres peligrosos y permite tags seguros)
        allowed_tags = ["b", "i", "u", "em", "strong", "p", "br"]
        text = bleach.clean(text, tags=allowed_tags, strip=True)

        return text.strip()

    def validate_email(self, email: str) -> bool:
        """Validar formato de email."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def _check_password_requirements(self, password: str) -> List[str]:
        """Verificar requisitos básicos de la contraseña."""
        errors = []

        requirements = [
            (len(password) >= 8, "Mínimo 8 caracteres"),
            (bool(re.search(r"[A-Z]", password)), "Debe contener mayúsculas"),
            (bool(re.search(r"[a-z]", password)), "Debe contener minúsculas"),
            (bool(re.search(r"\d", password)), "Debe contener números"),
            (
                bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password)),
                "Debe contener símbolos especiales",
            ),
        ]

        for condition, error_message in requirements:
            if not condition:
                errors.append(error_message)

        return errors

    def _calculate_password_strength(self, password: str) -> str:
        """Calcular la fortaleza de la contraseña."""
        score = 0

        if len(password) >= 12:
            score += 1
        if re.search(r"[A-Z]", password) and re.search(r"[a-z]", password):
            score += 1
        if re.search(r"\d", password):
            score += 1
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 1

        if score >= 3:
            return "strong"
        elif score >= 2:
            return "medium"
        else:
            return "weak"

    def validate_password(self, password: str) -> Dict[str, Any]:
        """Validar fortaleza de contraseña."""
        errors = self._check_password_requirements(password)

        if errors:
            return {"valid": False, "errors": errors, "strength": "weak"}
        else:
            return {
                "valid": True,
                "errors": [],
                "strength": self._calculate_password_strength(password),
            }

    def check_rate_limit(
        self, identifier: str, limit: int = 100, window: int = 3600
    ) -> bool:
        """Verificar límite de tasa."""
        now = datetime.now(timezone.utc)

        if identifier not in self.rate_limits:
            self.rate_limits[identifier] = []

        # Limpiar requests antiguos
        cutoff = now - timedelta(seconds=window)
        self.rate_limits[identifier] = [
            timestamp
            for timestamp in self.rate_limits[identifier]
            if timestamp > cutoff
        ]

        # Verificar límite
        if len(self.rate_limits[identifier]) >= limit:
            return False

        # Registrar request actual
        self.rate_limits[identifier].append(now)
        return True

    def detect_suspicious_activity(self, request_data: Dict[str, Any]) -> bool:
        """Detectar actividad sospechosa."""
        # Verificar patrones de inyección SQL
        sql_patterns = [
            r"(\bUNION\b|\bSELECT\b|\bINSERT\b|\bDELETE\b|\bDROP\b)",
            r"(\bOR\b\s+\d+\s*=\s*\d+)",
            r"(\bAND\b\s+\d+\s*=\s*\d+)",
            r"(--|\#|\/\*|\*\/)",
        ]

        # Verificar patrones XSS
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>.*?</iframe>",
        ]

        text_to_check = str(request_data).lower()

        for pattern in sql_patterns + xss_patterns:
            if re.search(pattern, text_to_check, re.IGNORECASE):
                return True

        return False

    def generate_csrf_token(self) -> str:
        """Generar token CSRF."""
        return secrets.token_urlsafe(32)

    def validate_csrf_token(self, token: str, session_token: str) -> bool:
        """Validar token CSRF."""
        return secrets.compare_digest(token, session_token)

    def hash_data(self, data: str) -> str:
        """Hash seguro de datos."""
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def apply_security_headers(self, response):
        """Aplicar headers de seguridad a la respuesta."""
        for header, value in self.security_headers.items():
            response.headers[header] = value
        return response


class RateLimiter:
    """Decorador para rate limiting."""

    def __init__(self, limit: int = 100, window: int = 3600):
        self.limit = limit
        self.window = window
        self.security_manager = SecurityManager()

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Obtener identificador (IP o usuario)
            identifier = request.remote_addr
            if hasattr(g, "current_user") and g.current_user:
                identifier = g.current_user.get("id", identifier)

            if not self.security_manager.check_rate_limit(
                identifier, self.limit, self.window
            ):
                return (
                    jsonify(
                        {
                            "error": "Rate limit exceeded",
                            "message": "Demasiadas solicitudes. Intenta más tarde.",
                        }
                    ),
                    429,
                )

            return func(*args, **kwargs)

        return wrapper


def require_https(func):
    """Decorador para requerir HTTPS."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if (
            not request.is_secure
            and not request.headers.get("X-Forwarded-Proto") == "https"
        ):
            return (
                jsonify(
                    {
                        "error": "HTTPS required",
                        "message": "Esta operación requiere conexión segura",
                    }
                ),
                400,
            )
        return func(*args, **kwargs)

    return wrapper


def validate_input(schema: Dict[str, Any]):
    """Decorador para validar entrada."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            security_manager = SecurityManager()

            # Obtener datos de la request
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form.to_dict()

            # Detectar actividad sospechosa
            if security_manager.detect_suspicious_activity(data):
                return (
                    jsonify(
                        {
                            "error": "Suspicious activity detected",
                            "message": "Solicitud bloqueada por seguridad",
                        }
                    ),
                    400,
                )

            # Sanitizar y validar datos
            validated_data = {}
            for field, rules in schema.items():
                value = data.get(field)
                if value is None:
                    validated_data[field] = None
                    continue

                # Sanitizar si se especifica
                if rules.get("sanitize"):
                    value = security_manager.sanitize_input(str(value))

                # Validar longitud
                max_length = rules.get("max_length")
                if max_length and len(value) > max_length:
                    return (
                        jsonify(
                            {
                                "error": "Validation error",
                                "message": f"Field '{field}' exceeds max length of {max_length}",
                            }
                        ),
                        400,
                    )
                validated_data[field] = value

            request.validated_data = validated_data
            return func(*args, **kwargs)

        return wrapper

    return decorator


# Instancia global
security_manager = SecurityManager()
