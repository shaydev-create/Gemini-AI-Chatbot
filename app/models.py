#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modelos de base de datos para Gemini AI Chatbot.
Define las estructuras de datos principales de la aplicación utilizando SQLAlchemy.
"""

import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import bcrypt
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Mapped

from app.config.extensions import db

logger=logging.getLogger(__name__)


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Valida la fortaleza de una contraseña.
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


class User(db.Model):
    """
    Modelo de usuario para autenticación, perfiles y gestión de acceso.
    """

    __tablename__: str = "users"

    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email: str = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash: str = db.Column(db.String(128), nullable=False)
    first_name: Optional[str] = db.Column(db.String(64))
    last_name: Optional[str] = db.Column(db.String(64))
    created_at: datetime = db.Column(db.DateTime, default=db.func.now())
    last_login: Optional[datetime] = db.Column(db.DateTime)
    status: str = db.Column(db.String(20), default="pending", nullable=False)
    role: str = db.Column(db.String(20), default="user", nullable=False, index=True)
    email_verified: bool = db.Column(db.Boolean, default=False, nullable=False)
    api_key: str = db.Column(db.String(64), unique=True, index=True, nullable=False)
    failed_login_attempts: int = db.Column(db.Integer, default=0, nullable=False)
    account_locked_until: Optional[datetime] = db.Column(db.DateTime, nullable=True)

    chat_sessions: Mapped[list["ChatSession"]] = db.relationship(
        "ChatSession", backref="user", lazy="select"
    )

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        if not self.api_key:
            self.api_key = self.generate_new_api_key()

    def __repr__(self) -> Any:
        return f"<User id={self.id} username='{self.username}' email='{self.email}' status='{self.status}'>"

    def set_password(self, password: str) -> None:
        """
        Hashea y establece la contraseña del usuario, validando su fortaleza.
        """
        is_strong, message = validate_password_strength(password)
        if not is_strong:
            raise ValueError(message)

        password_bytes=password.encode("utf-8")
        salt=bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password_bytes, salt).decode("utf-8")

    def check_password(self, password: str) -> bool:
        """Verifica si la contraseña proporcionada coincide con el hash almacenado."""
        if not self.password_hash:
            return False
        password_bytes=password.encode("utf-8")
        hash_bytes=self.password_hash.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hash_bytes)

    @staticmethod
    def generate_new_api_key() -> Any:
        """Genera una nueva API key segura."""
        return secrets.token_urlsafe(32)

    def regenerate_api_key(self) -> None:
        """Asigna una nueva API key al usuario."""
        self.api_key = self.generate_new_api_key()

    def increment_failed_login(self) -> None:
        """Incrementa el contador de intentos de inicio de sesión fallidos."""
        self.failed_login_attempts = (self.failed_login_attempts or 0) + 1

    def reset_failed_login(self) -> None:
        """Resetea el contador de intentos de inicio de sesión fallidos."""
        self.failed_login_attempts = 0

    def lock_account(self, minutes: int = 15) -> None:
        """Bloquea la cuenta por un número determinado de minutos."""
        self.account_locked_until = datetime.now(timezone.utc) + timedelta(
            minutes=minutes
        )

    def unlock_account(self) -> None:
        """Desbloquea la cuenta y resetea los intentos fallidos."""
        self.account_locked_until = None
        self.reset_failed_login()

    def is_account_locked(self) -> bool:
        """
        Verifica si la cuenta está actualmente bloqueada.
        Si el tiempo de bloqueo ha pasado, desbloquea la cuenta automáticamente.
        """
        if not self.account_locked_until:
            return False

        if datetime.now(timezone.utc) < self.account_locked_until:
            return True

        # El tiempo de bloqueo ha expirado, desbloquear la cuenta.
        self.unlock_account()
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception(
                "Error al auto-desbloquear la cuenta del usuario %s", self.username
            )
        return False

    def to_dict(self) -> dict[str, Any]:
        """Devuelve una representación del usuario en un diccionario."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "status": self.status,
            "role": self.role,
        }

    def check_password(self, password: str) -> bool:
        """Verifica si la contraseña proporcionada coincide con el hash almacenado."""
        if not self.password_hash:
            return False
        password_bytes=password.encode("utf-8")
        hash_bytes=self.password_hash.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hash_bytes)

    @staticmethod
    def generate_new_api_key() -> Any:
        """Genera una nueva API key segura."""
        return secrets.token_urlsafe(32)

    def regenerate_api_key(self) -> None:
        """Asigna una nueva API key al usuario."""
        self.api_key = self.generate_new_api_key()

    def increment_failed_login(self) -> None:
        """Incrementa el contador de intentos de inicio de sesión fallidos."""
        self.failed_login_attempts = (self.failed_login_attempts or 0) + 1

    def reset_failed_login(self) -> None:
        """Resetea el contador de intentos de inicio de sesión fallidos."""
        self.failed_login_attempts = 0

    def lock_account(self, minutes: int = 15) -> None:
        """Bloquea la cuenta por un número determinado de minutos."""
        self.account_locked_until = datetime.now(timezone.utc) + timedelta(
            minutes=minutes
        )

    def unlock_account(self) -> None:
        """Desbloquea la cuenta y resetea los intentos fallidos."""
        self.account_locked_until = None
        self.reset_failed_login()

    def is_account_locked(self) -> bool:
        """
        Verifica si la cuenta está actualmente bloqueada.
        Si el tiempo de bloqueo ha pasado, desbloquea la cuenta automáticamente.
        """
        if not self.account_locked_until:
            return False

        if datetime.now(timezone.utc) < self.account_locked_until:
            return True

        # El tiempo de bloqueo ha expirado, desbloquear la cuenta.
        self.unlock_account()
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception(
                "Error al auto-desbloquear la cuenta del usuario %s", self.username
            )
        return False

    def to_dict(self) -> dict[str, Any]:
        """Devuelve una representación del usuario en un diccionario."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "status": self.status,
            "role": self.role,
        }


class ChatSession(db.Model):
    """
    Modelo para una sesión de chat, que agrupa una serie de mensajes.
    """

    __tablename__: str = "chat_sessions"

    id: int = db.Column(db.Integer, primary_key=True)
    session_id: str = db.Column(db.String(64), unique=True, nullable=False, index=True)
    user_id: int = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    title: str = db.Column(db.String(255), nullable=False)
    created_at: datetime = db.Column(db.DateTime, default=db.func.now())
    updated_at: datetime = db.Column(
        db.DateTime,
        default=db.func.now(),
        onupdate=db.func.now(),
    )
    status: str = db.Column(db.String(20), default="active", nullable=False)
    model: str = db.Column(db.String(50), default="gemini-flash-latest", nullable=False)

    messages: Mapped[list["ChatMessage"]] = db.relationship(
        "ChatMessage", backref="session", lazy="select", cascade="all, delete-orphan"
    )

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        if not self.session_id:
            self.session_id = secrets.token_urlsafe(16)
        if not self.title:
            self.title = f"Conversación del {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}"

    def __repr__(self) -> Any:
        return f"<ChatSession id={self.id} session_id='{self.session_id}' user_id={self.user_id} status='{self.status}'>"

    def to_dict(self) -> dict[str, Any]:
        """Devuelve una representación de la sesión en un diccionario."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "title": self.title,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "status": self.status,
            "model": self.model,
        }


class ChatMessage(db.Model):
    """
    Modelo para un único mensaje dentro de una sesión de chat.
    """

    __tablename__: str = "chat_messages"

    id: int = db.Column(db.Integer, primary_key=True)
    session_id: int = db.Column(
        db.Integer, db.ForeignKey("chat_sessions.id"), nullable=False, index=True
    )
    role: str = db.Column(db.String(20), nullable=False)  # 'user' o 'assistant'
    content: str = db.Column(db.Text, nullable=False)
    created_at: datetime = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )
    tokens: Optional[int] = db.Column(db.Integer)

    def __repr__(self) -> Any:
        return f"<ChatMessage id={self.id} session_id={self.session_id} role='{self.role}'>"

    def to_dict(self) -> dict[str, Any]:
        """Devuelve una representación del mensaje en un diccionario."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "tokens": self.tokens,
        }