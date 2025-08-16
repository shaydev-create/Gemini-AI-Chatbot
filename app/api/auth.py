from flask import Blueprint, request, jsonify
from src.models import User
from config.database import db

# Blueprint para autenticación
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Datos requeridos"}), 400
    user = User.query.filter_by(email=data.get("email")).first()
    if user and user.check_password(data.get("password")):
        # Mock access_token
        access_token = user.api_key or "mocktoken123"
        return jsonify({"success": True, "message": "Login exitoso", "access_token": access_token}), 200
    return jsonify({"success": False, "message": "Credenciales inválidas"}), 401

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Datos requeridos"}), 400
    if User.query.filter_by(email=data.get("email")).first():
        return jsonify({"success": False, "message": "Email ya registrado"}), 409
    user = User(
        username=data.get("username"),
        email=data.get("email"),
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        status="active",
        email_verified=True
    )
    user.set_password(data.get("password"))
    db.session.add(user)
    db.session.commit()
    return jsonify({"success": True, "message": "Usuario registrado"}), 201
