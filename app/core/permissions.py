"""
Sistema de permisos granulares para la aplicación.
Permite definir permisos específicos más allá de roles simples.
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
import logging

logger = logging.getLogger(__name__)

# Definición de permisos disponibles
PERMISSIONS = {
    # Permisos de administración
    'admin.users.read': 'Leer información de usuarios',
    'admin.users.write': 'Crear/editar usuarios',
    'admin.users.delete': 'Eliminar usuarios',
    'admin.sessions.read': 'Ver sesiones de chat',
    'admin.sessions.delete': 'Eliminar sesiones de chat',
    'admin.system.stats': 'Ver estadísticas del sistema',
    
    # Permisos de usuario
    'user.chat.create': 'Crear sesiones de chat',
    'user.chat.read': 'Leer sesiones propias',
    'user.chat.delete': 'Eliminar sesiones propias',
    'user.profile.read': 'Leer perfil propio',
    'user.profile.write': 'Editar perfil propio',
    
    # Permisos premium
    'premium.chat.history': 'Acceso a historial extendido',
    'premium.chat.export': 'Exportar conversaciones',
    'premium.models.access': 'Acceso a modelos avanzados',
}

# Mapeo de roles a permisos por defecto
ROLE_PERMISSIONS = {
    'superadmin': list(PERMISSIONS.keys()),  # Todos los permisos
    'admin': [
        'admin.users.read', 'admin.users.write', 'admin.users.delete',
        'admin.sessions.read', 'admin.sessions.delete',
        'admin.system.stats',
        'user.chat.create', 'user.chat.read', 'user.chat.delete',
        'user.profile.read', 'user.profile.write',
        'premium.chat.history', 'premium.chat.export', 'premium.models.access'
    ],
    'moderator': [
        'admin.users.read',
        'admin.sessions.read', 'admin.sessions.delete',
        'user.chat.create', 'user.chat.read', 'user.chat.delete',
        'user.profile.read', 'user.profile.write',
    ],
    'premium': [
        'user.chat.create', 'user.chat.read', 'user.chat.delete',
        'user.profile.read', 'user.profile.write',
        'premium.chat.history', 'premium.chat.export', 'premium.models.access'
    ],
    'user': [
        'user.chat.create', 'user.chat.read', 'user.chat.delete',
        'user.profile.read', 'user.profile.write',
    ],
    'guest': [
        'user.chat.create', 'user.chat.read',
    ]
}

def permission_required(required_permission: str):
    """
    Decorador para verificar permisos específicos del usuario.
    
    Args:
        required_permission: El permiso requerido (ej. 'admin.users.read')
    """
    
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                from .decorators import get_current_user_from_jwt
                current_user = get_current_user_from_jwt()
                
                if not current_user:
                    logger.warning("Acceso denegado: usuario no autenticado")
                    return jsonify({
                        "message": "Se requiere autenticación para acceder a este recurso.",
                        "error": "authentication_required"
                    }), 401

                jwt_identity = get_jwt_identity()
                user_role = jwt_identity.get("role", "user")
                
                # Obtener permisos del usuario basados en su rol
                user_permissions = ROLE_PERMISSIONS.get(user_role, [])
                
                # Verificar si el usuario tiene el permiso requerido
                if required_permission not in user_permissions:
                    logger.warning(
                        "Permiso denegado para el usuario %s (rol: %s). Se requiere permiso: %s.",
                        current_user.username,
                        user_role,
                        required_permission,
                    )
                    return jsonify(
                        {
                            "message": "No tienes permiso para realizar esta acción.",
                            "error": "insufficient_permissions",
                            "required_permission": required_permission,
                            "user_role": user_role
                        }
                    ), 403

                return fn(*args, **kwargs)
            except Exception:
                logger.exception("Error en el decorador permission_required.")
                return jsonify(
                    {
                        "message": "Error interno al verificar los permisos.",
                        "error": "internal_server_error",
                    }
                ), 500

        return wrapper

    return decorator

def get_user_permissions(user_role: str) -> list:
    """
    Obtiene la lista de permisos para un rol específico.
    
    Args:
        user_role: El rol del usuario
        
    Returns:
        Lista de permisos para el rol
    """
    return ROLE_PERMISSIONS.get(user_role, [])

def has_permission(user_role: str, permission: str) -> bool:
    """
    Verifica si un rol tiene un permiso específico.
    
    Args:
        user_role: El rol del usuario
        permission: El permiso a verificar
        
    Returns:
        True si tiene el permiso, False en caso contrario
    """
    return permission in get_user_permissions(user_role)