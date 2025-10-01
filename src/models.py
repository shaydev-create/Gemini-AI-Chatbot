#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modelos de base de datos para Gemini AI Chatbot.
Define las estructuras de datos principales de la aplicación.
"""

import datetime
import secrets
import bcrypt
from config.database import db
from datetime import datetime, timedelta


class User(db.Model):
    """Modelo de usuario para autenticación y gestión de perfiles."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    # pending, active, suspended, deleted
    status = db.Column(db.String(20), default="pending")
    email_verified = db.Column(db.Boolean, default=False)
    api_key = db.Column(db.String(64), unique=True, index=True)
    failed_login_attempts = db.Column(db.Integer, default=0)
    account_locked_until = db.Column(db.DateTime, nullable=True)

    # Relaciones
    chat_sessions = db.relationship("ChatSession", backref="user", lazy="dynamic")

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.api_key is None:
            self.api_key = secrets.token_urlsafe(32)

    def set_password(self, password):
        """Establece el hash de la contraseña."""
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password_bytes, salt).decode("utf-8")

    def check_password(self, password):
        """Verifica si la contraseña es correcta."""
        password_bytes = password.encode("utf-8")
        hash_bytes = self.password_hash.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hash_bytes)

    def generate_new_api_key(self):
        """Genera una nueva API key."""
        self.api_key = secrets.token_urlsafe(32)
        return self.api_key

    def increment_failed_login(self):
        """Incrementa el contador de intentos fallidos de login."""
        self.failed_login_attempts += 1
        return self.failed_login_attempts

    def reset_failed_login(self):
        """Resetea el contador de intentos fallidos de login."""
        self.failed_login_attempts = 0

    def lock_account(self, minutes=15):
        """Bloquea la cuenta por un número de minutos."""
        self.account_locked_until = datetime.utcnow() + timedelta(minutes=minutes)

    def unlock_account(self):
        """Desbloquea la cuenta."""
        self.account_locked_until = None
        self.reset_failed_login()

    def is_account_locked(self):
        """Verifica si la cuenta está bloqueada."""
        if not self.account_locked_until:
            return False
        return datetime.utcnow() < self.account_locked_until


class ChatSession(db.Model):
    """Modelo para sesiones de chat."""

    __tablename__ = "chat_sessions"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    # active, archived, deleted
    status = db.Column(db.String(20), default="active")
    model = db.Column(db.String(50), default="gemini-pro")

    # Relaciones
    messages = db.relationship(
        "ChatMessage", backref="session", lazy="dynamic", cascade="all, delete-orphan"
    )

    def __init__(self, **kwargs):
        super(ChatSession, self).__init__(**kwargs)
        if self.session_id is None:
            self.session_id = secrets.token_urlsafe(16)
        if self.title is None:
            self.title = f"Conversación {
                datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"


class ChatMessage(db.Model):
    """Modelo para mensajes de chat."""

    __tablename__ = "chat_messages"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(
        db.Integer, db.ForeignKey("chat_sessions.id"), nullable=False
    )
    role = db.Column(db.String(20), nullable=False)  # user, assistant, system
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tokens = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<ChatMessage {self.id} - {self.role}>"
