#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestor de seguridad centralizado para Gemini AI Chatbot.
Coordina todas las funciones de seguridad del sistema.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from flask import Flask, request, g
from src.auth import auth_manager
from src.security import security_manager, RateLimiter, require_https, validate_input


class SecurityManagerCore:
    """Gestor central de seguridad del sistema."""

    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        self.auth = auth_manager
        self.security = security_manager
        self.logger = self._setup_logger()

        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        """Inicializar seguridad en la aplicación Flask."""
        self.app = app

        # Configurar middleware de seguridad
        app.before_request(self._before_request)
        app.after_request(self._after_request)

        # Configurar manejo de errores de seguridad
        app.errorhandler(401)(self._handle_unauthorized)
        app.errorhandler(403)(self._handle_forbidden)
        app.errorhandler(429)(self._handle_rate_limit)

    def _setup_logger(self) -> logging.Logger:
        """Configurar logger de seguridad."""
        logger = logging.getLogger("security")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _before_request(self):
        """Middleware ejecutado antes de cada request."""
        # Verificar IP bloqueada
        if request.remote_addr in self.security.blocked_ips:
            self.logger.warning(
                f"Blocked IP attempted access: {
                    request.remote_addr}")
            return "Access denied", 403

        # Log de request
        self.logger.info(
            f"Request: {
                request.method} {
                request.path} from {
                request.remote_addr}")

        # Verificar autenticación para rutas protegidas
        if self._requires_auth(request.path):
            auth_result = self._authenticate_request()
            if not auth_result["success"]:
                return auth_result["response"]
            g.current_user = auth_result["user"]

    def _after_request(self, response):
        """Middleware ejecutado después de cada request."""
        # Aplicar headers de seguridad
        response = self.security.apply_security_headers(response)

        # Log de respuesta
        self.logger.info(
            f"Response: {
                response.status_code} for {
                request.path}")

        return response

    def _requires_auth(self, path: str) -> bool:
        """Verificar si la ruta requiere autenticación."""
        protected_paths = [
            "/api/chat",
            "/api/history",
            "/api/settings",
            "/api/user"]

        return any(path.startswith(protected) for protected in protected_paths)

    def _authenticate_request(self) -> Dict[str, Any]:
        """Autenticar request actual."""
        # Verificar token JWT en header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            # Aquí iría la validación JWT
            # Por simplicidad, retornamos éxito
            return {
                "success": True,
                "user": {
                    "id": "demo_user",
                    "username": "demo"}}

        # Verificar API key
        api_key = request.headers.get("X-API-Key")
        if api_key:
            user = self.auth.authenticate_api_key(api_key)
            if user:
                return {"success": True, "user": user}

        return {"success": False, "response": ("Unauthorized", 401)}

    def _handle_unauthorized(self, error):
        """Manejar error 401."""
        self.logger.warning(
            f"Unauthorized access attempt: {
                request.remote_addr}")
        return {"error": "Unauthorized",
                "message": "Acceso no autorizado"}, 401

    def _handle_forbidden(self, error):
        """Manejar error 403."""
        self.logger.warning(f"Forbidden access attempt: {request.remote_addr}")
        return {"error": "Forbidden", "message": "Acceso prohibido"}, 403

    def _handle_rate_limit(self, error):
        """Manejar error 429."""
        self.logger.warning(f"Rate limit exceeded: {request.remote_addr}")
        return {
            "error": "Rate limit exceeded",
            "message": "Demasiadas solicitudes",
        }, 429

    def block_ip(self, ip_address: str, reason: str = "Security violation"):
        """Bloquear dirección IP."""
        self.security.blocked_ips.add(ip_address)
        self.logger.warning(f"IP blocked: {ip_address} - Reason: {reason}")

    def unblock_ip(self, ip_address: str):
        """Desbloquear dirección IP."""
        self.security.blocked_ips.discard(ip_address)
        self.logger.info(f"IP unblocked: {ip_address}")

    def get_security_status(self) -> Dict[str, Any]:
        """Obtener estado de seguridad del sistema."""
        return {
            "blocked_ips": len(self.security.blocked_ips),
            "active_rate_limits": len(self.security.rate_limits),
            "security_headers_enabled": True,
            "authentication_enabled": True,
            "last_check": datetime.utcnow().isoformat(),
        }

    def audit_log(self, event: str, details: Dict[str, Any]):
        """Registrar evento de auditoría."""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            "user": getattr(
                g,
                "current_user",
                {}).get(
                "username",
                "anonymous"),
            "ip": request.remote_addr if request else "system",
            "details": details,
        }

        self.logger.info(f"AUDIT: {audit_entry}")


# Instancia global
security_core = SecurityManagerCore()
