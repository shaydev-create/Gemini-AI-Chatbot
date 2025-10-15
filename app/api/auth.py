
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.auth import auth_manager, get_current_user_from_jwt

auth_bp=Blueprint("auth_api", __name__)


@auth_bp.route("/register", methods=["POST"])
def register() -> None:
    """
    Registra un nuevo usuario.
    """
    data=request.get_json()
    if (
        not data
        or not data.get("username")
        or not data.get("password")
        or not data.get("email")
    ):
        return jsonify(
            {"message": "Se requieren nombre de usuario, contraseña y email."}
        ), 400

    user, message = auth_manager.create_user(
        username=data["username"], password=data["password"], email=data["email"]
    )

    if not user:
        return jsonify({"message": message}), 409  # Conflict or Bad Request

    return jsonify(
        {"message": "Usuario registrado con éxito. Por favor, verifique su email."}
    ), 201


@auth_bp.route("/login", methods=["POST"])
def login() -> None:
    """
    Autentica a un usuario y devuelve tokens JWT.
    """
    data=request.get_json()
    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"message": "Se requieren nombre de usuario y contraseña."}), 400

    user=auth_manager.authenticate_user(
        username=data["username"], password=data["password"]
    )

    if not user:
        return jsonify(
            {"message": "Credenciales inválidas o cuenta inactiva/bloqueada."}
        ), 401

    tokens=auth_manager.create_tokens(user)
    return jsonify(tokens), 200


@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile() -> None:
    """
    Obtiene el perfil del usuario autenticado.
    """
    current_user=get_current_user_from_jwt()
    if not current_user:
        return jsonify({"message": "Usuario no encontrado o inactivo."}), 404

    return jsonify(current_user.to_dict()), 200


@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile() -> None:
    """
    Actualiza el perfil del usuario autenticado.
    """
    data=request.get_json()
    current_user=get_current_user_from_jwt()

    if not current_user:
        return jsonify({"message": "Usuario no encontrado."}), 404

    # Actualizar campos permitidos
    current_user.first_name = data.get("first_name", current_user.first_name)
    current_user.last_name = data.get("last_name", current_user.last_name)

    # Guardar cambios en la base de datos
    from app.config.database import db

    db.session.commit()

    return jsonify(
        {"message": "Perfil actualizado con éxito.", "user": current_user.to_dict()}
    ), 200
