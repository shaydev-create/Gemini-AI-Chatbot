"""
Sistema de caché para la aplicación.
"""

import logging
import sys
import threading
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Gestor de caché simple, en memoria y seguro para hilos (thread-safe).
    """

    def __init__(self, default_ttl: int = 300):
        """
        Inicializa el gestor de caché.

        Args:
            default_ttl: Tiempo de vida (TTL) por defecto para las entradas de caché, en segundos.
        """
        self._cache: Dict[str, tuple[Any, float]] = {}
        self.default_ttl = default_ttl
        self._lock = threading.Lock()
        logger.info("CacheManager inicializado con un TTL por defecto de %d segundos.", default_ttl)

    def get(self, key: str) -> Optional[Any]:
        """
        Obtiene un valor de la caché. Devuelve None si la clave no existe o ha expirado.
        """
        with self._lock:
            item = self._cache.get(key)
            if item:
                value, expiry = item
                if time.time() < expiry:
                    logger.debug("Cache HIT para la clave: %s", key)
                    return value
                else:
                    logger.debug("Cache EXPIRED para la clave: %s", key)
                    del self._cache[key]
            else:
                logger.debug("Cache MISS para la clave: %s", key)
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Almacena un valor en la caché con un TTL específico o el por defecto.
        """
        ttl_to_use = ttl or self.default_ttl
        expiry = time.time() + ttl_to_use

        with self._lock:
            self._cache[key] = (value, expiry)
        logger.debug("Cache SET para la clave: %s con un TTL de %d segundos.", key, ttl_to_use)

    def delete(self, key: str) -> bool:
        """
        Elimina una clave de la caché.
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug("Cache DELETE para la clave: %s", key)
                return True
            return False

    def clear(self):
        """
        Limpia toda la caché.
        """
        with self._lock:
            self._cache.clear()
        logger.info("Caché limpiada completamente.")

    def cleanup_expired(self) -> int:
        """
        Elimina todas las entradas expiradas de la caché.
        """
        with self._lock:
            current_time = time.time()
            expired_keys = [key for key, (_, expiry) in self._cache.items() if current_time >= expiry]

            for key in expired_keys:
                del self._cache[key]

        if expired_keys:
            logger.info("Limpieza de caché: %d entradas expiradas eliminadas.", len(expired_keys))
        return len(expired_keys)

    def get_stats(self) -> Dict[str, int]:
        """
        Obtiene estadísticas sobre el estado actual de la caché.
        """
        with self._lock:
            total_entries = len(self._cache)
            active_entries = total_entries - self.cleanup_expired()

            return {
                "total_entries": total_entries,
                "active_entries": active_entries,
                "expired_entries": total_entries - active_entries,
                "estimated_size_bytes": self.size_in_bytes(),
            }

    def size_in_bytes(self) -> int:
        """
        Estima el tamaño total de la caché en bytes.
        Es una aproximación y puede no ser exacta.
        """
        with self._lock:
            # sys.getsizeof no es recursivo, por lo que esto es una estimación.
            # Suma el tamaño del diccionario y una estimación del tamaño de sus contenidos.
            size = sys.getsizeof(self._cache)
            for key, (value, _) in self._cache.items():
                size += sys.getsizeof(key)
                size += sys.getsizeof(value)
        return size


# Instancia global del gestor de caché para ser usada en la aplicación.
cache_manager = CacheManager()
