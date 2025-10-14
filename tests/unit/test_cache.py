import time

import pytest

from app.core.cache import CacheManager


@pytest.fixture
def cache():
    """Fixture para crear una instancia limpia de CacheManager para cada prueba."""
    return CacheManager(default_ttl=60)


def test_cache_set_and_get(cache):
    """Prueba que se puede guardar y recuperar un valor del caché."""
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"


def test_cache_get_nonexistent_key(cache):
    """Prueba que obtener una clave inexistente devuelve None."""
    assert cache.get("nonexistent") is None


def test_cache_item_expires(cache):
    """Prueba que un elemento del caché expira después de su TTL."""
    cache.set("key_ttl", "value_ttl", ttl=0.1)
    assert cache.get("key_ttl") == "value_ttl"
    time.sleep(0.2)
    assert cache.get("key_ttl") is None


def test_cache_delete(cache):
    """Prueba que se puede eliminar un elemento del caché."""
    cache.set("key_to_delete", "value_to_delete")
    assert cache.get("key_to_delete") is not None

    deleted = cache.delete("key_to_delete")
    assert deleted is True
    assert cache.get("key_to_delete") is None


def test_cache_delete_nonexistent_key(cache):
    """Prueba que eliminar una clave inexistente devuelve False."""
    assert cache.delete("nonexistent") is False


def test_cache_clear(cache):
    """Prueba que se puede limpiar todo el caché."""
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    assert cache.get("key1") is not None

    cache.clear()
    assert cache.get("key1") is None
    assert cache.get("key2") is None
    stats = cache.get_stats()
    assert stats["total_entries"] == 0


def test_cache_cleanup_expired(cache):
    """Prueba que la limpieza de elementos expirados funciona correctamente."""
    cache.set("key_active", "value_active", ttl=10)
    cache.set("key_expired", "value_expired", ttl=0.1)

    time.sleep(0.2)

    cleaned_count = cache.cleanup_expired()
    assert cleaned_count == 1
    assert cache.get("key_active") == "value_active"
    assert cache.get("key_expired") is None


def test_cache_get_stats(cache):
    """Prueba que las estadísticas del caché son correctas."""
    cache.set("key1", "value1", ttl=10)
    cache.set("key2", "value2", ttl=0.1)

    stats_before_expiry = cache.get_stats()
    assert stats_before_expiry["total_entries"] == 2
    assert stats_before_expiry["active_entries"] == 2
    assert stats_before_expiry["expired_entries"] == 0

    time.sleep(0.2)

    stats_after_expiry = cache.get_stats()
    assert stats_after_expiry["total_entries"] == 2
    assert stats_after_expiry["active_entries"] == 1
    assert stats_after_expiry["expired_entries"] == 1


def test_cache_overwrite_key(cache):
    """Prueba que se puede sobreescribir una clave existente."""
    cache.set("key1", "original_value")
    assert cache.get("key1") == "original_value"

    cache.set("key1", "new_value")
    assert cache.get("key1") == "new_value"
