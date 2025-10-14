"""
Tests para el sistema de permisos y roles.
"""

import pytest
from app.core.permissions import get_user_permissions, has_permission, PERMISSIONS, ROLE_PERMISSIONS


def test_get_user_permissions():
    """Test que verifica que se obtienen los permisos correctos para cada rol."""
    
    # Test para rol de superadmin
    superadmin_perms = get_user_permissions('superadmin')
    assert len(superadmin_perms) == len(PERMISSIONS)
    assert all(perm in superadmin_perms for perm in PERMISSIONS.keys())
    
    # Test para rol de admin
    admin_perms = get_user_permissions('admin')
    assert len(admin_perms) > 0
    assert 'admin.users.read' in admin_perms
    assert 'admin.users.write' in admin_perms
    
    # Test para rol de user
    user_perms = get_user_permissions('user')
    assert 'user.chat.create' in user_perms
    assert 'user.profile.read' in user_perms
    assert 'admin.users.read' not in user_perms  # User no debería tener permisos de admin
    
    # Test para rol inexistente
    unknown_perms = get_user_permissions('unknown')
    assert len(unknown_perms) == 0


def test_has_permission():
    """Test que verifica la función has_permission."""
    
    # Test permisos válidos
    assert has_permission('admin', 'admin.users.read') is True
    assert has_permission('admin', 'admin.users.write') is True
    assert has_permission('user', 'user.chat.create') is True
    assert has_permission('user', 'user.profile.read') is True
    
    # Test permisos inválidos
    assert has_permission('user', 'admin.users.read') is False
    assert has_permission('user', 'admin.users.write') is False
    assert has_permission('guest', 'premium.chat.export') is False
    
    # Test permisos inexistentes
    assert has_permission('admin', 'nonexistent.permission') is False
    assert has_permission('user', 'invalid.permission') is False


def test_role_permissions_structure():
    """Test que verifica la estructura de ROLE_PERMISSIONS."""
    
    # Verificar que todos los roles definidos tienen permisos
    expected_roles = ['superadmin', 'admin', 'moderator', 'premium', 'user', 'guest']
    for role in expected_roles:
        assert role in ROLE_PERMISSIONS
        assert isinstance(ROLE_PERMISSIONS[role], list)
        assert len(ROLE_PERMISSIONS[role]) > 0
    
    # Verificar que los permisos asignados existen en PERMISSIONS
    for role, permissions in ROLE_PERMISSIONS.items():
        for permission in permissions:
            assert permission in PERMISSIONS, f"Permiso '{permission}' no existe en PERMISSIONS para rol '{role}'"


def test_permissions_hierarchy():
    """Test que verifica la jerarquía de permisos entre roles."""
    
    # Superadmin debería tener todos los permisos
    superadmin_perms = set(get_user_permissions('superadmin'))
    all_perms = set(PERMISSIONS.keys())
    assert superadmin_perms == all_perms
    
    # Admin debería tener más permisos que user
    admin_perms = set(get_user_permissions('admin'))
    user_perms = set(get_user_permissions('user'))
    assert admin_perms.issuperset(user_perms)
    assert len(admin_perms) > len(user_perms)
    
    # Premium debería tener más permisos que user regular
    premium_perms = set(get_user_permissions('premium'))
    assert premium_perms.issuperset(user_perms)
    assert len(premium_perms) > len(user_perms)
    assert 'premium.chat.export' in premium_perms
    assert 'premium.chat.export' not in user_perms