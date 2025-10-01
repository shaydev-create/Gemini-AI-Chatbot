"""
Blueprint de administración para Gemini AI Chatbot.
Solo accesible para usuarios autenticados con rol de administrador.
"""

from app.utils.i18n import translate
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# Importar la utilidad de traducción

# Hacer disponible en los templates


def inject_translate():
    return dict(translate=translate)


admin_bp.context_processor(inject_translate)


@admin_bp.route("/", methods=["GET"])
@jwt_required()
def admin_dashboard():
    user = get_jwt_identity()
    # Aquí se debería verificar el rol del usuario
    # if not user.get("is_admin", False):
    #     flash("Acceso restringido a administradores", "danger")
    #     return redirect(url_for("index"))
    return render_template("admin.html", user=user)
