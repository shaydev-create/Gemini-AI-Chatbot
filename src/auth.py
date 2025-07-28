#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de autenticación para Gemini AI Chatbot.
Manejo de usuarios, sesiones y autenticación JWT.
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
import bcrypt

class AuthManager:
    """Gestor de autenticación y autorización."""
    
    def __init__(self):
        self.users = {}  # En producción usar base de datos
        self.sessions = {}
        self.failed_attempts = {}
        self.max_attempts = 5
        self.lockout_duration = 300  # 5 minutos
    
    def hash_password(self, password: str) -> str:
        """Hashear contraseña con bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verificar contraseña hasheada."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def generate_api_key(self) -> str:
        """Generar API key segura."""
        return secrets.token_urlsafe(32)
    
    def create_user(self, username: str, password: str, email: str) -> Dict[str, Any]:
        """Crear nuevo usuario."""
        if username in self.users:
            raise ValueError("Usuario ya existe")
        
        user_id = secrets.token_urlsafe(16)
        hashed_password = self.hash_password(password)
        api_key = self.generate_api_key()
        
        user = {
            'id': user_id,
            'username': username,
            'email': email,
            'password_hash': hashed_password,
            'api_key': api_key,
            'created_at': datetime.utcnow(),
            'last_login': None,
            'is_active': True,
            'role': 'user'
        }
        
        self.users[username] = user
        return user
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Autenticar usuario con username y password."""
        # Verificar intentos fallidos
        if self._is_locked_out(username):
            raise ValueError("Cuenta bloqueada por múltiples intentos fallidos")
        
        user = self.users.get(username)
        if not user or not user['is_active']:
            self._record_failed_attempt(username)
            return None
        
        if self.verify_password(password, user['password_hash']):
            # Login exitoso
            user['last_login'] = datetime.utcnow()
            self._clear_failed_attempts(username)
            return user
        else:
            self._record_failed_attempt(username)
            return None
    
    def authenticate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Autenticar usando API key."""
        for user in self.users.values():
            if user.get('api_key') == api_key and user['is_active']:
                return user
        return None
    
    def create_tokens(self, user: Dict[str, Any]) -> Dict[str, str]:
        """Crear tokens JWT para el usuario."""
        identity = {
            'user_id': user['id'],
            'username': user['username'],
            'role': user['role']
        }
        
        access_token = create_access_token(
            identity=identity,
            expires_delta=timedelta(hours=1)
        )
        
        refresh_token = create_refresh_token(
            identity=identity,
            expires_delta=timedelta(days=30)
        )
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': 3600
        }
    
    def _is_locked_out(self, username: str) -> bool:
        """Verificar si la cuenta está bloqueada."""
        if username not in self.failed_attempts:
            return False
        
        attempts = self.failed_attempts[username]
        if attempts['count'] >= self.max_attempts:
            time_since_last = (datetime.utcnow() - attempts['last_attempt']).seconds
            return time_since_last < self.lockout_duration
        
        return False
    
    def _record_failed_attempt(self, username: str):
        """Registrar intento fallido."""
        if username not in self.failed_attempts:
            self.failed_attempts[username] = {'count': 0, 'last_attempt': None}
        
        self.failed_attempts[username]['count'] += 1
        self.failed_attempts[username]['last_attempt'] = datetime.utcnow()
    
    def _clear_failed_attempts(self, username: str):
        """Limpiar intentos fallidos."""
        if username in self.failed_attempts:
            del self.failed_attempts[username]

# Instancia global
auth_manager = AuthManager()


def get_current_user_with_verification(token=None):
    """Obtiene el usuario actual con verificación de token.
    
    Args:
        token: Token JWT opcional. Si no se proporciona, se obtiene del contexto.
        
    Returns:
        Usuario autenticado o None si no hay autenticación válida.
    """
    try:
        if token:
            # Lógica para verificar token proporcionado manualmente
            user_id = token.get('sub', {}).get('user_id')
            if not user_id:
                return None
        else:
            # Obtener identidad del token JWT en el contexto actual
            user_id = get_jwt_identity().get('user_id')
            if not user_id:
                return None
                
        # En un entorno real, buscaríamos el usuario en la base de datos
        # Aquí simulamos la búsqueda en el diccionario de usuarios
        for user in auth_manager.users.values():
            if user['id'] == user_id and user['is_active']:
                return user
        return None
    except Exception:
        return None


def validate_password_strength(password):
    """Valida la fortaleza de una contraseña.
    
    Args:
        password: La contraseña a validar.
        
    Returns:
        Tupla (bool, str) con el resultado de la validación y un mensaje.
    """
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
        
    if not any(c.isupper() for c in password):
        return False, "La contraseña debe contener al menos una letra mayúscula"
        
    if not any(c.islower() for c in password):
        return False, "La contraseña debe contener al menos una letra minúscula"
        
    if not any(c.isdigit() for c in password):
        return False, "La contraseña debe contener al menos un número"
        
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?/~`" for c in password):
        return False, "La contraseña debe contener al menos un carácter especial"
        
    return True, "Contraseña válida"