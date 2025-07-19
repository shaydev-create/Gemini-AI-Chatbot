"""
Sistema de caché para la aplicación.
"""

import time
import threading
from typing import Any, Optional

class CacheManager:
    """Gestor de caché simple en memoria."""
    
    def __init__(self, default_ttl: int = 300):
        """
        Inicializar el gestor de caché.
        
        Args:
            default_ttl: Tiempo de vida por defecto en segundos
        """
        self.cache = {}
        self.default_ttl = default_ttl
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Obtener valor del caché.
        
        Args:
            key: Clave del caché
            
        Returns:
            Valor almacenado o None si no existe o expiró
        """
        with self.lock:
            if key in self.cache:
                value, expiry = self.cache[key]
                if time.time() < expiry:
                    return value
                else:
                    del self.cache[key]
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Almacenar valor en el caché.
        
        Args:
            key: Clave del caché
            value: Valor a almacenar
            ttl: Tiempo de vida en segundos
        """
        ttl = ttl or self.default_ttl
        expiry = time.time() + ttl
        
        with self.lock:
            self.cache[key] = (value, expiry)
    
    def delete(self, key: str) -> bool:
        """
        Eliminar valor del caché.
        
        Args:
            key: Clave del caché
            
        Returns:
            True si se eliminó, False si no existía
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Limpiar todo el caché."""
        with self.lock:
            self.cache.clear()
    
    def cleanup_expired(self) -> int:
        """
        Limpiar entradas expiradas.
        
        Returns:
            Número de entradas eliminadas
        """
        current_time = time.time()
        expired_keys = []
        
        with self.lock:
            for key, (value, expiry) in self.cache.items():
                if current_time >= expiry:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]
        
        return len(expired_keys)
    
    def get_stats(self) -> dict:
        """
        Obtener estadísticas del caché.
        
        Returns:
            Dict con estadísticas
        """
        with self.lock:
            total_entries = len(self.cache)
            current_time = time.time()
            expired_count = sum(1 for _, expiry in self.cache.values() 
                              if current_time >= expiry)
            
            return {
                'total_entries': total_entries,
                'active_entries': total_entries - expired_count,
                'expired_entries': expired_count
            }

# Instancia global del gestor de caché
cache_manager = CacheManager()