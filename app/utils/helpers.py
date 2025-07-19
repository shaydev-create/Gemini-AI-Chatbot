"""
Utilidades generales para la aplicación.
"""

import os
import hashlib
import secrets
from typing import Optional

def generate_secret_key(length: int = 32) -> str:
    """
    Generar una clave secreta segura.
    
    Args:
        length: Longitud de la clave en bytes
        
    Returns:
        Clave secreta en hexadecimal
    """
    return secrets.token_hex(length)

def hash_string(text: str, algorithm: str = 'sha256') -> str:
    """
    Generar hash de un string.
    
    Args:
        text: Texto a hashear
        algorithm: Algoritmo de hash
        
    Returns:
        Hash en hexadecimal
    """
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(text.encode('utf-8'))
    return hash_obj.hexdigest()

def ensure_directory_exists(path: str) -> None:
    """
    Asegurar que un directorio existe.
    
    Args:
        path: Ruta del directorio
    """
    os.makedirs(path, exist_ok=True)

def get_file_size(file_path: str) -> Optional[int]:
    """
    Obtener el tamaño de un archivo.
    
    Args:
        file_path: Ruta del archivo
        
    Returns:
        Tamaño en bytes o None si no existe
    """
    try:
        return os.path.getsize(file_path)
    except OSError:
        return None

def sanitize_filename(filename: str) -> str:
    """
    Sanitizar nombre de archivo.
    
    Args:
        filename: Nombre original
        
    Returns:
        Nombre sanitizado
    """
    # Caracteres no permitidos
    invalid_chars = '<>:"/\\|?*'
    
    # Reemplazar caracteres inválidos
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limitar longitud
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename

def format_bytes(bytes_value: int) -> str:
    """
    Formatear bytes en formato legible.
    
    Args:
        bytes_value: Valor en bytes
        
    Returns:
        String formateado (ej: "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"

def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncar texto si es muy largo.
    
    Args:
        text: Texto original
        max_length: Longitud máxima
        suffix: Sufijo para texto truncado
        
    Returns:
        Texto truncado si es necesario
    """
    if len(text) <= max_length:
        return text
    
    # Truncar y eliminar espacios al final antes de agregar el sufijo
    truncated = text[:max_length - len(suffix)].rstrip()
    return truncated + suffix