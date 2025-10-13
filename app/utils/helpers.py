"""
Utilidades generales para la aplicación.
"""

import hashlib
import logging
import os
import secrets
import uuid
from pathlib import Path
from typing import Optional, Union

logger = logging.getLogger(__name__)


def generate_secret_key(length: int = 32) -> str:
    """
    Genera una clave secreta segura en formato hexadecimal.

    Args:
        length: La longitud en bytes del token a generar.

    Returns:
        Una clave secreta hexadecimal.
    """
    return secrets.token_hex(length)


def generate_request_id() -> str:
    """Genera un ID único para una solicitud (request)."""
    return str(uuid.uuid4())


def hash_string(text: str, algorithm: str = "sha256") -> str:
    """
    Genera el hash de una cadena de texto utilizando el algoritmo especificado.

    Args:
        text: Texto a hashear
        algorithm: Algoritmo de hash

    Returns:
        Hash en hexadecimal
    """
    try:
        hash_obj = hashlib.new(algorithm)
        hash_obj.update(text.encode("utf-8"))
        return hash_obj.hexdigest()
    except ValueError:
        logger.exception(
            "Algoritmo de hash no válido: %s. Usando sha256 como fallback.", algorithm
        )
        hash_obj = hashlib.sha256()
        hash_obj.update(text.encode("utf-8"))
        return hash_obj.hexdigest()


def ensure_directory_exists(path: Union[str, Path]):
    """
    Asegura que un directorio exista, creándolo si es necesario.
    Utiliza pathlib para un manejo de rutas más robusto.

    Args:
        path: Ruta del directorio
    """
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
    except OSError:
        logger.exception("No se pudo crear el directorio en la ruta: %s", path)


def get_file_size(file_path: Union[str, Path]) -> Optional[int]:
    """
    Obtiene el tamaño de un archivo en bytes.

    Args:
        file_path: Ruta del archivo

    Returns:
        Tamaño en bytes o None si no existe
    """
    try:
        return Path(file_path).stat().st_size
    except (OSError, FileNotFoundError):
        logger.debug(
            "No se pudo obtener el tamaño del archivo (puede que no exista): %s",
            file_path,
        )
        return None


def sanitize_filename(filename: str) -> str:
    """
    Limpia y sanitiza un nombre de archivo para hacerlo seguro para el sistema de archivos.

    Args:
        filename: Nombre original

    Returns:
        Nombre sanitizado
    """
    # Caracteres no permitidos en la mayoría de los sistemas de archivos
    invalid_chars = r'<>:"/\\|?*'
    sanitized = "".join(c if c.isalnum() or c in "._-" else "_" for c in filename)

    # Limitar la longitud total del nombre del archivo
    if len(sanitized) > 255:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[: 255 - len(ext)] + ext

    return sanitized


def format_bytes(size_in_bytes: int) -> str:
    """
    Formatea un tamaño en bytes a un formato legible por humanos (KB, MB, GB, etc.).

    Args:
        size_in_bytes: Valor en bytes

    Returns:
        String formateado (ej: "1.5 MB")
    """
    if size_in_bytes is None or size_in_bytes < 0:
        return "0 B"

    power = 1024
    n = 0
    power_labels = {0: "B", 1: "KB", 2: "MB", 3: "GB", 4: "TB"}

    while size_in_bytes >= power and n < len(power_labels) - 1:
        size_in_bytes /= power
        n += 1

    return f"{size_in_bytes:.1f} {power_labels[n]}"


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Trunca un texto a una longitud máxima si es necesario, añadiendo un sufijo.

    Args:
        text: Texto original
        max_length: Longitud máxima
        suffix: Sufijo para texto truncado

    Returns:
        Texto truncado si es necesario
    """
    if not isinstance(text, str) or len(text) <= max_length:
        return text

    # Truncar y eliminar espacios en blanco al final antes de añadir el sufijo
    truncated = text[: max_length - len(suffix)].rstrip()
    return truncated + suffix
