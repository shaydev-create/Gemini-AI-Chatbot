"""
Blueprint de administración para Gemini AI Chatbot.
Solo accesible para usuarios autenticados con rol de administrador.
"""

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required

from app.config.database import check_db_connection, db
from app.core.decorators import role_required
from app.core.metrics import metrics_manager
from app.models import User

admin_bp = Blueprint("admin_api", __name__)


@admin_bp.route("/status", methods=["GET"])
@jwt_required()
@role_required("admin")
def system_status():
    """
    Endpoint para verificar el estado del sistema (base de datos, servicios de IA, etc.).
    """
    # Verificar estado de la base de datos
    db_url = current_app.config.get("SQLALCHEMY_DATABASE_URI")
    db_ok, db_msg = check_db_connection(db_url)

    # Verificar estado de los servicios de IA
    ai_service_ok = hasattr(current_app, 'gemini_service') and current_app.gemini_service is not None

    status = {
        "database": {"status": "ok" if db_ok else "error", "message": db_msg},
        "ai_services": {"status": "ok" if ai_service_ok else "error", "message": "Servicios de IA operativos." if ai_service_ok else "Servicios de IA no inicializados."}
    }

    http_status = 200 if db_ok and ai_service_ok else 503  # Service Unavailable
    return jsonify(status), http_status


@admin_bp.route("/metrics", methods=["GET"])
@jwt_required()
@role_required("admin")
def get_metrics():
    """
    Endpoint para obtener las métricas de rendimiento de la aplicación.
    """
    return jsonify(metrics_manager.get_metrics()), 200


@admin_bp.route("/users", methods=["GET"])
@jwt_required()
@role_required("admin")
def list_users():
    """
    Obtiene una lista paginada de todos los usuarios.
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    users_pagination = User.query.paginate(page=page, per_page=per_page, error_out=False)
    users_list = [user.to_dict() for user in users_pagination.items]

    return jsonify({
        "users": users_list,
        "total": users_pagination.total,
        "pages": users_pagination.pages,
        "current_page": users_pagination.page
    }), 200


@admin_bp.route("/users/<int:user_id>", methods=["GET"])
@jwt_required()
@role_required("admin")
def get_user(user_id: int):
    """
    Obtiene los detalles de un usuario específico.
    """
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200


@admin_bp.route("/users/<int:user_id>", methods=["PUT"])
@jwt_required()
@role_required("admin")
def update_user(user_id: int):
    """
    Actualiza la información de un usuario (ej. rol, estado).
    """
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    if not data:
        return jsonify({"message": "Se requiere un cuerpo de solicitud JSON."}), 400

    # Actualizar campos permitidos
    user.status = data.get('status', user.status)
    # Aquí se podría añadir la lógica para cambiar el rol, con cuidado.
    # user.role = data.get('role', user.role)

    db.session.commit()
    return jsonify({"message": "Usuario actualizado con éxito.", "user": user.to_dict()}), 200

