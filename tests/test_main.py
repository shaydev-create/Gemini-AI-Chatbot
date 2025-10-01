#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TESTS UNITARIOS - GEMINI AI CHATBOT

Suite completa de tests para validar todas las funcionalidades del sistema.
"""

from src.auth import get_current_user_with_verification, validate_password_strength
from src.models import db, User, ChatSession
from app.core.application import create_app
import pytest
import os
import sys
from datetime import datetime, timezone
from flask import Flask
from flask_testing import TestCase

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class BaseTestCase(TestCase):
    """Clase base para todos los tests."""

    def create_app(self):
        """Crear aplicación para testing."""
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['JWT_SECRET_KEY'] = 'test-secret-key'
        return app

    def setUp(self):
        """Configurar antes de cada test."""
        db.create_all()

        # Crear usuario de prueba
        self.test_user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        self.test_user.set_password('testpassword123')
        self.test_user.email_verified = True
        self.test_user.status = 'active'

        db.session.add(self.test_user)
        db.session.commit()

    def tearDown(self):
        """Limpiar después de cada test."""
        db.session.remove()
        db.drop_all()


class TestUserModel(BaseTestCase):
    """Tests para el modelo User."""

    def test_user_creation(self):
        """Test creación de usuario."""
        user = User(
            username='newuser',
            email='new@example.com'
        )
        user.set_password('password123')

        db.session.add(user)
        db.session.commit()

        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, 'newuser')
        self.assertTrue(user.check_password('password123'))

    def test_password_hashing(self):
        """Test hashing de contraseñas."""
        user = User(username='test', email='test@test.com')
        user.set_password('secret')

        self.assertNotEqual(user.password_hash, 'secret')
        self.assertTrue(user.check_password('secret'))
        self.assertFalse(user.check_password('wrong'))

    def test_account_locking(self):
        """Test bloqueo de cuenta."""
        user = self.test_user

        # Incrementar intentos fallidos
        for _ in range(5):
            user.increment_failed_login()

        # Bloquear cuenta
        user.lock_account(15)

        self.assertTrue(user.is_account_locked())

        # Desbloquear
        user.unlock_account()
        self.assertFalse(user.is_account_locked())


class TestAuthentication(BaseTestCase):
    """Tests para autenticación."""

    def test_login_success(self):
        """Test login exitoso."""
        response = self.client.post('/auth/login', json={
            'email': 'test@example.com',
            'password': 'testpassword123'
        })

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('access_token', data)

    def test_login_invalid_credentials(self):
        """Test login con credenciales inválidas."""
        response = self.client.post('/auth/login', json={
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })

        self.assertEqual(response.status_code, 401)

    def test_register_user(self):
        """Test registro de usuario."""
        response = self.client.post('/auth/register', json={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123',
            'first_name': 'New',
            'last_name': 'User'
        })

        self.assertEqual(response.status_code, 201)

        # Verificar que el usuario fue creado
        user = User.query.filter_by(email='newuser@example.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'newuser')


class TestPasswordValidation(BaseTestCase):
    """Tests para validación de contraseñas."""

    def test_strong_password(self):
        """Test contraseña fuerte."""
        result = validate_password_strength('MyStr0ngP@ssw0rd!')
        self.assertTrue(result['valid'])
        self.assertGreaterEqual(result['score'], 80)

    def test_weak_password(self):
        """Test contraseña débil."""
        result = validate_password_strength('123')
        self.assertFalse(result['valid'])
        self.assertLess(result['score'], 50)


class TestChatAPI(BaseTestCase):
    """Tests para API de chat."""

    def test_chat_without_auth(self):
        """Test chat sin autenticación."""
        response = self.client.post('/api/chat', json={
            'message': 'Hello'
        })

        self.assertEqual(response.status_code, 401)

    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get('/api/health')

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'healthy')


class TestFileUpload(BaseTestCase):
    """Tests para carga de archivos."""

    def test_upload_without_auth(self):
        """Test upload sin autenticación."""
        response = self.client.post('/api/upload')

        self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    pytest.main([__file__])
