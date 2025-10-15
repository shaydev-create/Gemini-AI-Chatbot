"""
Blueprint de administración para Gemini AI Chatbot.
Solo accesible para usuarios autenticados con rol de administrador.
"""

from typing import Any

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required

from app.auth import auth_manager
from app.config.database import check_db_connection, db
from app.core.decorators import role_required
from app.core.metrics import metrics_manager
from app.core.permissions import PERMISSIONS, ROLE_PERMISSIONS
from app.core.security import get_security_summary
from app.models import User

admin_bp = Blueprint("admin_api", __name__)


@admin_bp.route("/security-summary", methods=["GET"])
@jwt_required()
@role_required("admin")
def security_summary() -> None:
    """
    Endpoint para obtener un resumen de seguridad del sistema.
    """
    return jsonify(get_security_summary()), 200


@admin_bp.route("/status", methods=["GET"])
@jwt_required()
@role_required("admin")
def system_status() -> None:
    """
    Endpoint para verificar el estado del sistema (base de datos, servicios de IA, etc.).
    """
    # Verificar estado de la base de datos
    db_url = current_app.config.get("SQLALCHEMY_DATABASE_URI")
    db_ok, db_msg = check_db_connection(db_url)

    # Verificar estado de los servicios de IA
    ai_service_ok = hasattr(current_app, "gemini_service") and current_app.gemini_service is not None

    status = {
        "database": {"status": "ok" if db_ok else "error", "message": db_msg},
        "ai_services": {
            "status": "ok" if ai_service_ok else "error",
            "message": ("Servicios de IA operativos." if ai_service_ok else "Servicios de IA no inicializados."),
        },
    }

    http_status = 200 if db_ok and ai_service_ok else 503  # Service Unavailable
    return jsonify(status), http_status


@admin_bp.route("/metrics", methods=["GET"])
@jwt_required()
@role_required("admin")
def get_metrics() -> None:
    """
    Endpoint para obtener las métricas de rendimiento de la aplicación.
    """
    return jsonify(metrics_manager.get_metrics()), 200


@admin_bp.route("/users", methods=["GET"])
@jwt_required()
@role_required("admin")
def list_users() -> None:
    """
    Obtiene una lista paginada de todos los usuarios.
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    users_pagination = User.query.paginate(page=page, per_page=per_page, error_out=False)
    users_list: list[Any] = [user.to_dict() for user in users_pagination.items]

    return (
        jsonify(
            {
                "users": users_list,
                "total": users_pagination.total,
                "pages": users_pagination.pages,
                "current_page": users_pagination.page,
            }
        ),
        200,
    )


@admin_bp.route("/users/<int:user_id>", methods=["GET"])
@jwt_required()
@role_required("admin")
def get_user(user_id: int) -> None:
    """
    Obtiene los detalles de un usuario específico.
    """
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200


@admin_bp.route("/users/<int:user_id>", methods=["PUT"])
@jwt_required()
@role_required("admin")
def update_user(user_id: int) -> None:
    """
    Actualiza la información de un usuario (ej. rol, estado).
    """
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    if not data:
        return jsonify({"message": "Se requiere un cuerpo de solicitud JSON."}), 400

    # Actualizar campos permitidos
    user.status = data.get("status", user.status)

    # Actualizar rol si se proporciona y es válido
    if "role" in data:
        new_role = data["role"]
        valid_roles: list[Any] = [
            "superadmin",
            "admin",
            "moderator",
            "premium",
            "user",
            "guest",
        ]
        if new_role in valid_roles:
            user.role = new_role
        else:
            return (
                jsonify(
                    {
                        "message": f"Rol inválido: {new_role}. Roles válidos: {', '.join(valid_roles)}",
                        "error": "invalid_role",
                    }
                ),
                400,
            )

    db.session.commit()
    return (
        jsonify({"message": "Usuario actualizado con éxito.", "user": user.to_dict()}),
        200,
    )


@admin_bp.route("/users/<int:user_id>/role", methods=["PUT"])
@jwt_required()
@role_required("admin")
def update_user_role(user_id: int) -> None:
    """
    Actualiza el rol de un usuario.
    Requiere rol de administrador.
    """
    try:
        data = request.get_json()
        if not data or "role" not in data:
            return (
                jsonify(
                    {
                        "message": 'Se requiere el campo "role"',
                        "error": "missing_role_field",
                    }
                ),
                400,
            )

        new_role = data["role"]
        updated_user = auth_manager.update_user_role(user_id, new_role)

        if not updated_user:
            return (
                jsonify(
                    {
                        "message": "Usuario no encontrado o rol inválido",
                        "error": "user_not_found_or_invalid_role",
                    }
                ),
                404,
            )

        return (
            jsonify(
                {
                    "message": "Rol actualizado correctamente",
                    "user": updated_user.to_dict(),
                    "new_permissions": auth_manager.get_user_permissions(updated_user.id),
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"message": "Error al actualizar rol", "error": str(e)}), 500


@admin_bp.route("/users/role/<role>", methods=["GET"])
@jwt_required()
@role_required("admin")
def get_users_by_role(role: str) -> None:
    """
    Obtiene todos los usuarios con un rol específico.
    Requiere rol de administrador.
    """
    try:
        users = auth_manager.get_users_by_role(role)
        return (
            jsonify(
                {
                    "users": [user.to_dict() for user in users],
                    "count": len(users),
                    "role": role,
                }
            ),
            200,
        )
    except Exception as e:
        return (
            jsonify({"message": "Error al obtener usuarios por rol", "error": str(e)}),
            500,
        )


@admin_bp.route("/permissions/<int:user_id>", methods=["GET"])
@jwt_required()
@role_required("admin")
def get_user_permissions(user_id: int) -> None:
    """
    Obtiene los permisos de un usuario específico.
    Requiere rol de administrador.
    """
    try:
        permissions = auth_manager.get_user_permissions(user_id)
        user = User.query.get(user_id)

        if not user:
            return (
                jsonify({"message": "Usuario no encontrado", "error": "user_not_found"}),
                404,
            )

        return (
            jsonify(
                {
                    "user_id": user_id,
                    "username": user.username,
                    "role": user.role,
                    "permissions": permissions,
                    "permissions_count": len(permissions),
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"message": "Error al obtener permisos", "error": str(e)}), 500


@admin_bp.route("/permissions", methods=["GET"])
@jwt_required()
@role_required("admin")
def get_all_permissions() -> None:
    """
    Obtiene todos los permisos disponibles en el sistema.
    Requiere rol de administrador.
    """
    return (
        jsonify({"permissions": PERMISSIONS, "role_permissions": ROLE_PERMISSIONS}),
        200,
    )


@admin_bp.route("/stats/users", methods=["GET"])
@jwt_required()
@role_required("admin")
def get_users_stats() -> None:
    """
    Obtiene estadísticas de usuarios por rol.
    Requiere rol de administrador.
    """
    try:
        # Contar usuarios por rol
        roles_stats: dict[str, Any] = {}
        valid_roles: list[Any] = [
            "superadmin",
            "admin",
            "moderator",
            "premium",
            "user",
            "guest",
        ]

        for role in valid_roles:
            count = User.query.filter_by(role=role).count()
            roles_stats[role] = count

        total_users = User.query.count()

        return (
            jsonify(
                {
                    "users_total": total_users,
                    "users_by_role": roles_stats,
                    "active_sessions": 0,  # TODO: Implementar contador de sesiones activas
                }
            ),
            200,
        )

    except Exception as e:
        return (
            jsonify({"message": "Error al obtener estadísticas", "error": str(e)}),
            500,
        )
