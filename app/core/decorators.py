"""
Decoradores para la aplicación.
"""

import logging
from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity

from app.auth import get_current_user_from_jwt

logger = logging.getLogger(__name__)


def role_required(required_role: str):
    """
    Decorador para restringir el acceso a una ruta a usuarios con un rol específico.
    Soporta múltiples roles separados por coma y jerarquía de permisos.

    Args:
        required_role: El rol o roles requeridos (ej. 'admin' o 'admin,moderator').
    """
    # Definir jerarquía de roles (de mayor a menor privilegio)
    ROLE_HIERARCHY = {
        'superadmin': 100,
        'admin': 90,
        'moderator': 80,
        'premium': 70,
        'user': 50,
        'guest': 10
    }

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                current_user = get_current_user_from_jwt()

                if not current_user:
                    logger.warning("Acceso denegado: usuario no autenticado")
                    return jsonify({
                        "message": "Se requiere autenticación para acceder a este recurso.",
                        "error": "authentication_required"
                    }), 401

                jwt_identity = get_jwt_identity()
                user_role = jwt_identity.get("role", "user")

                # Verificar si el usuario tiene el rol requerido o uno superior
                required_roles = [r.strip() for r in required_role.split(',')]
                user_has_access = False

                # Verificar acceso por rol específico
                if user_role in required_roles:
                    user_has_access = True
                # Verificar acceso por jerarquía (si el usuario tiene un rol superior)
                elif (user_role in ROLE_HIERARCHY and
                      any(req_role in ROLE_HIERARCHY and
                          ROLE_HIERARCHY[user_role] >= ROLE_HIERARCHY[req_role]
                          for req_role in required_roles)):
                    user_has_access = True

                if not user_has_access:
                    logger.warning(
                        "Acceso denegado para el usuario %s (rol: %s). Se requiere rol: %s.",
                        current_user.username,
                        user_role,
                        required_role,
                    )
                    return jsonify(
                        {
                            "message": "No tienes permiso para realizar esta acción.",
                            "error": "insufficient_permissions",
                            "required_role": required_role,
                            "user_role": user_role
                        }
                    ), 403

                return fn(*args, **kwargs)
            except Exception:
                logger.exception("Error en el decorador role_required.")
                return jsonify(
                    {
                        "message": "Error interno al verificar los permisos.",
                        "error": "internal_server_error",
                    }
                ), 500

        return wrapper

    return decorator


def log_request(fn):
    """
    Decorador para registrar información sobre las solicitudes entrantes.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_identity = get_jwt_identity()
        logger.info(
            "Solicitud a '%s' recibida de %s.",
            fn.__name__,
            user_identity.get("username", "anónimo") if user_identity else "anónimo",
        )
        return fn(*args, **kwargs)

    return wrapper
