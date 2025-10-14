"""
Tests para las funcionalidades de roles y permisos en AuthManager.
"""

from app.auth import AuthManager
from app.models import User


def test_update_user_role(auth_manager: AuthManager, test_user: User):
    """Test para actualizar el rol de un usuario."""

    # Verificar rol inicial
    assert test_user.role == "user"

    # Actualizar a admin
    updated_user = auth_manager.update_user_role(test_user.id, "admin")
    assert updated_user is not None
    assert updated_user.role == "admin"
    assert updated_user.id == test_user.id

    # Verificar en la base de datos
    user_from_db = User.query.get(test_user.id)
    assert user_from_db.role == "admin"


def test_update_user_role_invalid_role(auth_manager: AuthManager, test_user: User):
    """Test para intentar actualizar a un rol inválido."""

    # Intentar actualizar a rol inválido
    result = auth_manager.update_user_role(test_user.id, "invalid_role")
    assert result is None

    # Verificar que el rol no cambió
    user_from_db = User.query.get(test_user.id)
    assert user_from_db.role == "user"


def test_update_user_role_nonexistent_user(auth_manager: AuthManager):
    """Test para intentar actualizar rol de usuario inexistente."""

    result = auth_manager.update_user_role(999999, "admin")
    assert result is None


def test_get_user_permissions(auth_manager: AuthManager, test_user: User):
    """Test para obtener permisos de usuario."""

    # Permisos de usuario regular
    permissions = auth_manager.get_user_permissions(test_user.id)
    assert isinstance(permissions, list)
    assert "user.chat.create" in permissions
    assert "user.profile.read" in permissions
    assert "admin.users.read" not in permissions

    # Cambiar a admin y verificar permisos
    auth_manager.update_user_role(test_user.id, "admin")
    admin_permissions = auth_manager.get_user_permissions(test_user.id)
    assert "admin.users.read" in admin_permissions
    assert "admin.users.write" in admin_permissions


def test_has_permission(auth_manager: AuthManager, test_user: User):
    """Test para verificar permisos específicos."""

    # Usuario regular debería tener permisos básicos
    assert auth_manager.has_permission(test_user.id, "user.chat.create") is True
    assert auth_manager.has_permission(test_user.id, "user.profile.read") is True

    # Usuario regular NO debería tener permisos de admin
    assert auth_manager.has_permission(test_user.id, "admin.users.read") is False
    assert auth_manager.has_permission(test_user.id, "admin.users.write") is False

    # Cambiar a admin y verificar
    auth_manager.update_user_role(test_user.id, "admin")
    assert auth_manager.has_permission(test_user.id, "admin.users.read") is True
    assert auth_manager.has_permission(test_user.id, "admin.users.write") is True


def test_has_permission_nonexistent_user(auth_manager: AuthManager):
    """Test para verificar permisos de usuario inexistente."""

    assert auth_manager.has_permission(999999, "user.chat.create") is False
    assert auth_manager.has_permission(999999, "admin.users.read") is False


def test_has_permission_invalid_permission(auth_manager: AuthManager, test_user: User):
    """Test para verificar permisos inválidos."""

    assert auth_manager.has_permission(test_user.id, "nonexistent.permission") is False
    assert auth_manager.has_permission(test_user.id, "invalid.permission") is False


def test_get_users_by_role(auth_manager: AuthManager, test_user: User):
    """Test para obtener usuarios por rol."""

    # Obtener usuarios con rol 'user'
    users = auth_manager.get_users_by_role("user")
    assert isinstance(users, list)
    assert len(users) >= 1
    assert any(user.id == test_user.id for user in users)

    # Obtener usuarios con rol 'admin' (debería estar vacío inicialmente)
    admin_users = auth_manager.get_users_by_role("admin")
    assert isinstance(admin_users, list)

    # Cambiar rol y verificar
    auth_manager.update_user_role(test_user.id, "admin")
    admin_users_after = auth_manager.get_users_by_role("admin")
    assert len(admin_users_after) >= 1
    assert any(user.id == test_user.id for user in admin_users_after)


def test_get_users_by_role_invalid_role(auth_manager: AuthManager):
    """Test para obtener usuarios con rol inválido."""

    users = auth_manager.get_users_by_role("invalid_role")
    assert isinstance(users, list)
    assert len(users) == 0
