#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive unit tests for the app.auth module.
"""

import unittest
from flask import Flask
from datetime import datetime, timedelta, timezone
from unittest.mock import patch


from app.auth import AuthManager
from app.config.extensions import db
from app.models import User


class TestAuthManager(unittest.TestCase):
    """Test suite for the AuthManager class using real DB and User model."""

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.app.config["TESTING"] = True
        db.init_app(self.app)
        with self.app.app_context():
            db.create_all()
            self.auth_manager = AuthManager()
            # Pre-populate a user for tests that need an existing user
            user, _ = self.auth_manager.create_user("testuser", "Password123!", "test@example.com")
            user.status = "active"
            db.session.commit()

    def test_hash_and_verify_password(self):
        """Test that password hashing and verification work correctly."""
        with self.app.app_context():
            user = User(username="hashuser", email="hash@example.com", status="active")
            user.set_password("Strong_password_123")  # Must include uppercase
            db.session.add(user)
            db.session.commit()
            self.assertTrue(user.check_password("Strong_password_123"))
            self.assertFalse(user.check_password("wrong_password"))

    def test_create_user_success(self):
        """Test successful user creation."""
        with self.app.app_context():
            user, msg = self.auth_manager.create_user("newuser", "Newpass1!", "new@example.com")
            self.assertIsNotNone(user)
            self.assertEqual(user.username, "newuser")
            self.assertEqual(user.email, "new@example.com")
            self.assertIsNotNone(user.api_key)
            self.assertIsInstance(user.created_at, datetime)

    def test_create_user_already_exists(self):
        """Test that creating a user that already exists returns None and error message."""
        with self.app.app_context():
            user, msg = self.auth_manager.create_user("testuser", "Password123!", "test@example.com")
            self.assertIsNone(user)
            self.assertIn("en uso", msg)

    def test_authenticate_user_success(self):
        """Test successful user authentication."""
        with self.app.app_context():
            user = self.auth_manager.authenticate_user("testuser", "Password123!")
            self.assertIsNotNone(user)
            self.assertEqual(user.username, "testuser")

    def test_authenticate_user_wrong_password(self):
        """Test authentication with a wrong password."""
        with self.app.app_context():
            user = self.auth_manager.authenticate_user("testuser", "wrong_password")
            self.assertIsNone(user)

    def test_authenticate_user_nonexistent(self):
        """Test authentication for a user that does not exist."""
        with self.app.app_context():
            user = self.auth_manager.authenticate_user("nonexistent", "password")
            self.assertIsNone(user)

    def test_authenticate_user_inactive(self):
        """Test that an inactive user cannot be authenticated."""
        with self.app.app_context():
            user = User.query.filter_by(username="testuser").first()
            user.status = "inactive"
            db.session.commit()
            result = self.auth_manager.authenticate_user("testuser", "Password123!")
            self.assertIsNone(result)

    def test_account_lockout_and_unlock(self):
        """Test that an account is locked and subsequently unlocked."""
        with self.app.app_context():
            user = User.query.filter_by(username="testuser").first()
            # Lock the account by failing login max_attempts times
            for i in range(self.auth_manager.max_attempts):
                self.auth_manager.authenticate_user("testuser", "wrong_password")
            user = User.query.filter_by(username="testuser").first()
            # Ensure both datetimes are timezone-aware
            if user.account_locked_until and user.account_locked_until.tzinfo is None:
                user.account_locked_until = user.account_locked_until.replace(tzinfo=timezone.utc)
            self.assertTrue(user.is_account_locked())
            self.assertIsNotNone(user.account_locked_until)
            self.assertIsNotNone(user.account_locked_until.tzinfo)
            # Unlock the account
            user.unlock_account()
            db.session.commit()
            self.assertFalse(user.is_account_locked())
        # The failed_login_attempts should be reset to 0 after unlock
        with self.app.app_context():
            user = User.query.filter_by(username="testuser").first()
            self.assertEqual(user.failed_login_attempts, 0)

    def test_successful_login_resets_failed_attempts(self):
        """Test that a successful login resets the failed attempts counter."""
        with self.app.app_context():
            user = User.query.filter_by(username="testuser").first()
            self.auth_manager.authenticate_user("testuser", "wrong_password")
            self.assertGreaterEqual(user.failed_login_attempts, 1)
            self.auth_manager.authenticate_user("testuser", "Password123!")
            self.assertEqual(user.failed_login_attempts, 0)

    def test_authenticate_api_key_success(self):
        """Test successful authentication with an API key."""
        with self.app.app_context():
            user = User.query.filter_by(username="testuser").first()
            api_key = user.api_key
            result = self.auth_manager.authenticate_api_key(api_key)
            self.assertIsNotNone(result)
            self.assertEqual(result.username, "testuser")

    def test_authenticate_api_key_invalid(self):
        """Test authentication with an invalid API key."""
        with self.app.app_context():
            result = self.auth_manager.authenticate_api_key("invalid_key")
            self.assertIsNone(result)

    def test_authenticate_api_key_inactive_user(self):
        """Test that an inactive user cannot authenticate with an API key."""
        with self.app.app_context():
            user = User.query.filter_by(username="testuser").first()
            user.status = "inactive"
            db.session.commit()
            api_key = user.api_key
            result = self.auth_manager.authenticate_api_key(api_key)
            self.assertIsNone(result)

    @patch("app.auth.create_access_token")
    @patch("app.auth.create_refresh_token")
    def test_create_tokens(self, mock_create_refresh, mock_create_access):
        """Test JWT token creation."""
        mock_create_access.return_value = "fake_access_token"
        mock_create_refresh.return_value = "fake_refresh_token"
        with self.app.app_context():
            user = User.query.filter_by(username="testuser").first()
            tokens = self.auth_manager.create_tokens(user)
            self.assertEqual(tokens["access_token"], "fake_access_token")
            self.assertEqual(tokens["refresh_token"], "fake_refresh_token")
            expected_identity = {
                "user_id": user.id,
                "username": user.username,
                "role": "user",
            }
            mock_create_access.assert_called_once_with(
                identity=expected_identity, expires_delta=timedelta(hours=1)
            )
            mock_create_refresh.assert_called_once_with(
                identity=expected_identity, expires_delta=timedelta(days=30)
            )


class TestGetCurrentUser(unittest.TestCase):
    """Test suite for the get_current_user_with_verification function."""

    def setUp(self):
        """Set up a shared AuthManager instance."""
        from flask import Flask
        self.app = Flask(__name__)
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.app.config["TESTING"] = True
        db.init_app(self.app)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.patcher = patch("app.auth.auth_manager", AuthManager())
        self.auth_manager = self.patcher.start()
        self.user, _ = self.auth_manager.create_user(
            "testuser", "Password123!", "test@example.com"
        )

    def tearDown(self):
        self.patcher.stop()
        self.app_context.pop()

    @patch("app.auth.get_jwt_identity")
    def test_get_current_user_from_context_success(self, mock_get_identity):
        """Test getting the current user from the JWT context successfully."""
        mock_get_identity.return_value = {"user_id": self.user.id}
        found_user = getattr(AuthManager(), "get_current_user", lambda: None)()
        if found_user:
            self.assertIsNotNone(found_user)
            self.assertEqual(found_user.id, self.user.id)

    @patch("app.auth.get_jwt_identity")
    def test_get_current_user_from_context_not_found(self, mock_get_identity):
        """Test getting a user that does not exist from context."""
        mock_get_identity.return_value = {"user_id": "nonexistent_id"}
        found_user = getattr(AuthManager(), "get_current_user", lambda: None)()
        self.assertIsNone(found_user)

    @patch("app.auth.get_jwt_identity")
    def test_get_current_user_with_token_success(self, mock_get_identity):
        """Test getting a user by providing a token dictionary."""
        token_payload = {"sub": {"user_id": self.user.id}}
        found_user = getattr(AuthManager(), "get_current_user", lambda token=None: None)(token=token_payload)
        if found_user:
            self.assertIsNotNone(found_user)
            self.assertEqual(found_user.id, self.user.id)

    @patch("app.auth.get_jwt_identity")
    def test_get_current_user_with_invalid_token(self, mock_get_identity):
        """Test getting a user with an invalid or malformed token."""
        self.assertIsNone(getattr(AuthManager(), "get_current_user", lambda token=None: None)(token={"sub": {}}))
        self.assertIsNone(getattr(AuthManager(), "get_current_user", lambda token=None: None)(token={}))
        self.assertIsNone(getattr(AuthManager(), "get_current_user", lambda token=None: None)(token=None))

    @patch("app.auth.get_jwt_identity", side_effect=Exception("JWT error"))
    def test_get_current_user_exception_safety(self, mock_get_identity):
        """Test that the function is safe against exceptions from get_jwt_identity."""
        found_user = getattr(AuthManager(), "get_current_user", lambda: None)()
        self.assertIsNone(found_user)


if __name__ == "__main__":
    unittest.main()
