#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de autenticación para Gemini AI Chatbot.
Manejo de usuarios, sesiones y autenticación JWT.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from flask import Blueprint
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    verify_jwt_in_request,
)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.config.extensions import db
from app.core.permissions import get_user_permissions, has_permission
from app.models import User

logger = logging.getLogger(__name__)


class AuthManager:
    """
    Gestor de autenticación y autorización.
    Interactúa con la base de datos a través del modelo User.
    """

    def __init__(self, max_attempts: int = 5, lockout_duration: int = 300) -> None:
        """
        Inicializa el gestor de autenticación.

        Args:
            max_attempts: Número máximo de intentos de inicio de sesión fallidos.
            lockout_duration: Duración del bloqueo de la cuenta en segundos.
        """
        self.max_attempts = max_attempts
        self.lockout_duration = lockout_duration

    def create_user(self, username: str, password: str, email: str) -> tuple[Optional[User], str]:
        """
        Crea un nuevo usuario en la base de datos.

        Returns:
            Una tupla (User, mensaje_de_éxito) o (None, mensaje_de_error).
        """
        if not self.validate_password_strength(password)[0]:
            return None, "La contraseña no cumple con los requisitos de seguridad."

        try:
            # Verificar si el usuario o el email ya existen
            if User.query.filter((User.username == username) | (User.email == email)).first():
                logger.warning(
                    "Intento de crear un usuario que ya existe: %s o %s",
                    username,
                    email,
                )
                return None, "El nombre de usuario o el email ya están en uso."

            new_user = User(username=username, email=email, status="pending")
            new_user.set_password(password)

            db.session.add(new_user)
            db.session.commit()

            logger.info("✅ Nuevo usuario creado con éxito: %s", username)
            return new_user, "Usuario creado con éxito."
        except IntegrityError:
            db.session.rollback()
            logger.warning(
                "Intento de crear un usuario que ya existe (error de integridad): %s",
                username,
            )
            return None, "El nombre de usuario o el email ya están en uso."
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception("❌ Error de base de datos al crear el usuario: %s", username)
            return None, "Error en la base de datos al crear el usuario."

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Autentica a un usuario con su nombre de usuario y contraseña.
        Maneja el bloqueo de cuentas por intentos fallidos.
        """
        user = User.query.filter_by(username=username).first()

        if not user:
            logger.warning("Intento de inicio de sesión para usuario no existente: %s", username)
            return None

        if user.is_account_locked():
            logger.warning("Intento de inicio de sesión para cuenta bloqueada: %s", username)
            return None

        if user.check_password(password):
            if user.status != "active":
                logger.warning(
                    "Intento de inicio de sesión para usuario inactivo: %s (estado: %s)",
                    username,
                    user.status,
                )
                return None

            # Login exitoso: resetear intentos fallidos y actualizar último login
            user.failed_login_attempts = 0
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            logger.info("Inicio de sesión exitoso para el usuario: %s", username)
            return user
        else:
            # Contraseña incorrecta: incrementar intentos fallidos
            user.failed_login_attempts += 1

            # Bloquear cuenta si se excede el máximo de intentos
            if user.failed_login_attempts >= self.max_attempts:
                user.lock_account(self.lockout_duration)
                logger.warning(
                    "Cuenta bloqueada para el usuario: %s después de %d intentos fallidos",
                    username,
                    self.max_attempts,
                )

            db.session.commit()
            logger.warning(
                "Intento de inicio de sesión fallido para el usuario: %s (intento %d/%d)",
                username,
                user.failed_login_attempts,
                self.max_attempts,
            )
            return None

    def update_user_role(self, user_id: int, new_role: str) -> Optional[User]:
        """
        Actualiza el rol de un usuario.

        Args:
            user_id: ID del usuario a actualizar
            new_role: Nuevo rol del usuario

        Returns:
            El usuario actualizado o None si no se encuentra
        """
        # Validar que el rol sea válido
        valid_roles: list[Any] = [
            "superadmin",
            "admin",
            "moderator",
            "premium",
            "user",
            "guest",
        ]
        if new_role not in valid_roles:
            logger.warning("Intento de asignar rol inválido: %s", new_role)
            return None

        user = User.query.get(user_id)
        if user:
            user.role = new_role
            db.session.commit()
            logger.info("Rol del usuario %s actualizado a: %s", user.username, new_role)
            return user

        return None

    def assign_role_to_user(self, user_id: int, role: str) -> Optional[User]:
        """
        Asigna un rol a un usuario existente.

        Args:
            user_id: ID del usuario al que se le asignará el rol.
            role: El rol a asignar (ej. 'admin', 'user').

        Returns:
            El objeto User actualizado si la asignación fue exitosa, None en caso contrario.
        """
        valid_roles: list[Any] = [
            "superadmin",
            "admin",
            "moderator",
            "premium",
            "user",
            "guest",
        ]
        if role not in valid_roles:
            logger.warning("Intento de asignar un rol inválido: %s a user_id: %d", role, user_id)
            return None

        user = User.query.get(user_id)
        if user:
            user.role = role
            db.session.commit()
            logger.info("Rol '%s' asignado al usuario %s (ID: %d)", role, user.username, user_id)
            return user
        logger.warning("No se encontró el usuario con ID: %d para asignar el rol.", user_id)
        return None

    def remove_role_from_user(self, user_id: int, role: str) -> Optional[User]:
        """
        Elimina un rol específico de un usuario.

        Args:
            user_id: ID del usuario al que se le eliminará el rol.
            role: El rol a eliminar.

        Returns:
            El objeto User actualizado si la eliminación fue exitosa, None en caso contrario.
        """
        user = User.query.get(user_id)
        if user:
            # Solo eliminar el rol si el usuario realmente lo tiene
            if user.role == role:
                user.role = "user"  # O algún rol predeterminado
                db.session.commit()
                logger.info(
                    "Rol '%s' eliminado del usuario %s (ID: %d). Rol actual: %s",
                    role,
                    user.username,
                    user_id,
                    user.role,
                )
                return user
            logger.warning(
                "El usuario %s (ID: %d) no tiene el rol '%s' para eliminar.",
                user.username,
                user_id,
                role,
            )
            return None  # Retornar None si el usuario no tiene el rol para eliminar
        logger.warning("No se encontró el usuario con ID: %d para eliminar el rol.", user_id)
        return None

    def get_user_permissions(self, user_id: int) -> List[str]:
        """
        Obtiene la lista de permisos de un usuario basado en su rol.

        Args:
            user_id: ID del usuario

        Returns:
            Lista de permisos del usuario
        """
        user = User.query.get(user_id)
        if user:
            return get_user_permissions(user.role)
        return []

    def has_permission(self, user_id: int, permission: str) -> bool:
        """
        Verifica si un usuario tiene un permiso específico.

        Args:
            user_id: ID del usuario
            permission: Permiso a verificar

        Returns:
            True si tiene el permiso, False en caso contrario
        """
        user = User.query.get(user_id)
        if user:
            return has_permission(user.role, permission)
        return False

    def get_users_by_role(self, role: str) -> List[User]:
        """
        Obtiene todos los usuarios con un rol específico.

        Args:
            role: Rol a buscar

        Returns:
            Lista de usuarios con el rol especificado
        """
        return User.query.filter_by(role=role).all()

    def authenticate_api_key(self, api_key: str) -> Optional[User]:
        """Autentica a un usuario usando una API key."""
        if not api_key:
            return None

        user = User.query.filter_by(api_key=api_key).first()

        if user and user.status == "active":
            return user

        return None

    def create_tokens(self, user: User) -> Dict[str, Any]:
        """
        Crea tokens JWT (acceso y refresco) para un usuario.
        """
        identity = {
            "user_id": user.id,
            "username": user.username,
            "role": user.role,  # Usar el rol real del usuario
        }

        access_token = create_access_token(identity=identity, expires_delta=timedelta(hours=1))
        refresh_token = create_refresh_token(identity=identity, expires_delta=timedelta(days=30))

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": 3600,  # 1 hora en segundos
        }

    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, str]:
        """
        Valida la fortaleza de una contraseña.
        Criterios: Mínimo 8 caracteres, mayúscula, minúscula, dígito y especial.
        """
        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres."
        if not any(c.isupper() for c in password):
            return False, "La contraseña debe contener al menos una letra mayúscula."
        if not any(c.islower() for c in password):
            return False, "La contraseña debe contener al menos una letra minúscula."
        if not any(c.isdigit() for c in password):
            return False, "La contraseña debe contener al menos un dígito."
        if not any(c in "!@#$%^&*()-_=+[]{}|;:'\",.<>/?`~" for c in password):
            return False, "La contraseña debe contener al menos un carácter especial."

        return True, "La contraseña es segura."


# Instancia global
auth_manager = AuthManager()
auth = Blueprint("auth", __name__)


def get_current_user_from_jwt() -> Optional[User]:
    """
    Obtiene el usuario actual a partir de la identidad del token JWT.
    Busca en la base de datos para devolver el objeto User completo y actualizado.
    Retorna None si no hay JWT o si no es válido.
    """
    try:
        # Verificar si hay un JWT en la request antes de intentar obtener la identidad
        verify_jwt_in_request(optional=True)

        jwt_identity = get_jwt_identity()
        if not jwt_identity or "user_id" not in jwt_identity:
            return None

        user = User.query.get(jwt_identity["user_id"])

        if user and user.status == "active":
            return user

        return None
    except Exception:
        # Si no hay JWT o hay cualquier error, simplemente retornar None
        # No logear el error ya que es esperado para usuarios anónimos
        return None
