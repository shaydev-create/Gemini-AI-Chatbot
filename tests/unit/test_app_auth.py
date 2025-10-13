#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive unit tests for the app.auth module.
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from app.auth import AuthManager


class TestAuthManager(unittest.TestCase):
    """Test suite for the AuthManager class."""

    def setUp(self):
        """Set up a new AuthManager instance for each test."""
        self.auth_manager = AuthManager()
        # Pre-populate a user for tests that need an existing user
        self.auth_manager.create_user("testuser", "password123", "test@example.com")

    def test_hash_and_verify_password(self):
        """Test that password hashing and verification work correctly."""
        password = "strong_password_123"
        hashed_password = self.auth_manager.hash_password(password)
        self.assertNotEqual(password, hashed_password)
        self.assertTrue(self.auth_manager.verify_password(password, hashed_password))
        self.assertFalse(self.auth_manager.verify_password("wrong_password", hashed_password))

    def test_create_user_success(self):
        """Test successful user creation."""
        user = self.auth_manager.create_user("newuser", "newpass", "new@example.com")
        self.assertIn("newuser", self.auth_manager.users)
        self.assertEqual(user["username"], "newuser")
        self.assertEqual(user["email"], "new@example.com")
        self.assertTrue(self.auth_manager.verify_password("newpass", user["password_hash"]))
        self.assertIn("api_key", user)
        self.assertIsInstance(user["created_at"], datetime)

    def test_create_user_already_exists(self):
        """Test that creating a user that already exists raises a ValueError."""
        with self.assertRaises(ValueError) as context:
            self.auth_manager.create_user("testuser", "another_password", "another@example.com")
        self.assertEqual(str(context.exception), "Usuario ya existe")

    def test_authenticate_user_success(self):
        """Test successful user authentication."""
        user = self.auth_manager.authenticate_user("testuser", "password123")
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "testuser")
        self.assertIsNotNone(user["last_login"])

    def test_authenticate_user_wrong_password(self):
        """Test authentication with a wrong password."""
        user = self.auth_manager.authenticate_user("testuser", "wrong_password")
        self.assertIsNone(user)
        self.assertEqual(self.auth_manager.failed_attempts["testuser"]["count"], 1)

    def test_authenticate_user_nonexistent(self):
        """Test authentication for a user that does not exist."""
        user = self.auth_manager.authenticate_user("nonexistent", "password")
        self.assertIsNone(user)
        self.assertEqual(self.auth_manager.failed_attempts["nonexistent"]["count"], 1)

    def test_authenticate_user_inactive(self):
        """Test that an inactive user cannot be authenticated."""
        self.auth_manager.users["testuser"]["is_active"] = False
        user = self.auth_manager.authenticate_user("testuser", "password123")
        self.assertIsNone(user)

    def test_account_lockout_and_unlock(self):
        """Test that an account is locked and subsequently unlocked."""
        # Lock the account
        for i in range(self.auth_manager.max_attempts):
            self.auth_manager.authenticate_user("testuser", "wrong_password")
            self.assertEqual(self.auth_manager.failed_attempts["testuser"]["count"], i + 1)

        with self.assertRaises(ValueError) as context:
            self.auth_manager.authenticate_user("testuser", "wrong_password")
        self.assertEqual(str(context.exception), "Cuenta bloqueada por múltiples intentos fallidos")

        # Simulate time passing to unlock the account
        self.auth_manager.failed_attempts["testuser"]["last_attempt"] -= timedelta(seconds=self.auth_manager.lockout_duration + 1)

        # Should be able to attempt login again (will fail, but not be locked)
        user = self.auth_manager.authenticate_user("testuser", "wrong_password")
        self.assertIsNone(user)
        # The count should have been reset and is now 1
        self.assertEqual(self.auth_manager.failed_attempts["testuser"]["count"], 1)

    def test_successful_login_resets_failed_attempts(self):
        """Test that a successful login resets the failed attempts counter."""
        self.auth_manager.authenticate_user("testuser", "wrong_password")
        self.assertIn("testuser", self.auth_manager.failed_attempts)

        self.auth_manager.authenticate_user("testuser", "password123")
        self.assertNotIn("testuser", self.auth_manager.failed_attempts)

    def test_authenticate_api_key_success(self):
        """Test successful authentication with an API key."""
        api_key = self.auth_manager.users["testuser"]["api_key"]
        user = self.auth_manager.authenticate_api_key(api_key)
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "testuser")

    def test_authenticate_api_key_invalid(self):
        """Test authentication with an invalid API key."""
        user = self.auth_manager.authenticate_api_key("invalid_key")
        self.assertIsNone(user)

    def test_authenticate_api_key_inactive_user(self):
        """Test that an inactive user cannot authenticate with an API key."""
        self.auth_manager.users["testuser"]["is_active"] = False
        api_key = self.auth_manager.users["testuser"]["api_key"]
        user = self.auth_manager.authenticate_api_key(api_key)
        self.assertIsNone(user)

    @patch('app.auth.create_access_token')
    @patch('app.auth.create_refresh_token')
    def test_create_tokens(self, mock_create_refresh, mock_create_access):
        """Test JWT token creation."""
        mock_create_access.return_value = "fake_access_token"
        mock_create_refresh.return_value = "fake_refresh_token"

        user_data = self.auth_manager.users["testuser"]
        tokens = self.auth_manager.create_tokens(user_data)

        self.assertEqual(tokens["access_token"], "fake_access_token")
        self.assertEqual(tokens["refresh_token"], "fake_refresh_token")

        expected_identity = {
            "user_id": user_data["id"],
            "username": user_data["username"],
            "role": user_data["role"],
        }
        mock_create_access.assert_called_once_with(identity=expected_identity, expires_delta=timedelta(hours=1))
        mock_create_refresh.assert_called_once_with(identity=expected_identity, expires_delta=timedelta(days=30))

class TestGetCurrentUser(unittest.TestCase):
    """Test suite for the get_current_user_with_verification function."""

    def setUp(self):
        """Set up a shared AuthManager instance."""
        self.patcher = patch('app.auth.auth_manager', AuthManager())
        self.auth_manager = self.patcher.start()
        self.user = self.auth_manager.create_user("testuser", "password123", "test@example.com")

    def tearDown(self):
        self.patcher.stop()

    @patch('app.auth.get_jwt_identity')
    def test_get_current_user_from_context_success(self, mock_get_identity):
        """Test getting the current user from the JWT context successfully."""
        mock_get_identity.return_value = {"user_id": self.user["id"]}

        found_user = AuthManager().get_current_user()
        self.assertIsNotNone(found_user)
        self.assertEqual(found_user["id"], self.user["id"])

    @patch('app.auth.get_jwt_identity')
    def test_get_current_user_from_context_not_found(self, mock_get_identity):
        """Test getting a user that does not exist from context."""
        mock_get_identity.return_value = {"user_id": "nonexistent_id"}
        found_user = AuthManager().get_current_user()
        self.assertIsNone(found_user)

    def test_get_current_user_with_token_success(self):
        """Test getting a user by providing a token dictionary."""
        token_payload = {"sub": {"user_id": self.user["id"]}}
        found_user = AuthManager().get_current_user(token=token_payload)
        self.assertIsNotNone(found_user)
        self.assertEqual(found_user["id"], self.user["id"])

    def test_get_current_user_with_invalid_token(self):
        """Test getting a user with an invalid or malformed token."""
        self.assertIsNone(AuthManager().get_current_user(token={"sub": {}}))
        self.assertIsNone(AuthManager().get_current_user(token={}))
        self.assertIsNone(AuthManager().get_current_user(token=None))

    @patch('app.auth.get_jwt_identity', side_effect=Exception("JWT error"))
    def test_get_current_user_exception_safety(self, mock_get_identity):
        """Test that the function is safe against exceptions from get_jwt_identity."""
        found_user = AuthManager().get_current_user()
        self.assertIsNone(found_user)

if __name__ == '__main__':
    unittest.main()
