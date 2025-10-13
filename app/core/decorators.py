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

    Args:
        required_role: El rol requerido para acceder a la ruta (ej. 'admin').
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                current_user = get_current_user_from_jwt()

                # Asumiendo que el modelo User tiene un campo 'role'
                # y que get_jwt_identity() devuelve un diccionario con 'role'.
                jwt_identity = get_jwt_identity()
                user_role = jwt_identity.get("role")

                if not current_user or user_role != required_role:
                    logger.warning(
                        "Acceso denegado para el usuario %s (rol: %s). Se requiere rol: %s.",
                        jwt_identity.get("username", "desconocido"),
                        user_role,
                        required_role,
                    )
                    return jsonify(
                        {
                            "message": "No tienes permiso para realizar esta acción.",
                            "error": "insufficient_permissions",
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
