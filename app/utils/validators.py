"""
Validadores para la aplicación.
"""

import logging
import re
from typing import List, Optional, Tuple

# Configuración del logger
logger = logging.getLogger(__name__)

# Expresiones regulares precompiladas para un mejor rendimiento
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
API_KEY_PATTERN = re.compile(r"^[a-zA-Z0-9_]{10,}$")
DANGEROUS_SCRIPT_PATTERNS = re.compile(r"<script[^>]*>.*?</script>|javascript:|on\w+\s*=", re.IGNORECASE)
CONTROL_CHARS_PATTERN = re.compile(r"[\x00-\x1f\x7f]")
WHITESPACE_PATTERN = re.compile(r"\s+")
DANGEROUS_FILENAME_CHARS = re.compile(r'[<>:"|?*\\/]')


def validate_email(email: str) -> bool:
    """
    Valida si una cadena de texto tiene un formato de email válido.

    Args:
        email: La dirección de email a validar.

    Returns:
        True si el formato del email es válido, False en caso contrario.
    """
    if not isinstance(email, str) or not EMAIL_PATTERN.match(email):
        logger.warning(f"Intento de validación de email fallido para: '{email}'")
        return False
    return True


def validate_message_content(message: str) -> Tuple[bool, Optional[str]]:
    """
    Valida el contenido de un mensaje para asegurar que cumple con las políticas de seguridad y uso.

    Args:
        message: El mensaje a validar.

    Returns:
        Una tupla (es_valido, mensaje_error). Si es válido, mensaje_error es None.
    """
    if not message or not message.strip():
        return False, "El mensaje no puede estar vacío."

    if len(message) > 4096:
        return (
            False,
            "El mensaje excede la longitud máxima permitida (4096 caracteres).",
        )

    if len(message.strip()) < 2:
        return False, "El mensaje es demasiado corto (mínimo 2 caracteres)."

    if DANGEROUS_SCRIPT_PATTERNS.search(message):
        logger.warning(f"Detectado contenido potencialmente peligroso en el mensaje: '{message[:100]}...'")
        return (
            False,
            "El mensaje contiene contenido no permitido que podría ser inseguro.",
        )

    return True, None


def validate_api_key(api_key: str) -> bool:
    """
    Valida el formato de una clave de API.

    Args:
        api_key: La clave de API a validar.

    Returns:
        True si el formato es válido, False en caso contrario.
    """
    if not isinstance(api_key, str) or not API_KEY_PATTERN.match(api_key):
        logger.warning("Intento de uso de una API key con formato inválido.")
        return False
    return True


def sanitize_input(text: Optional[str]) -> str:
    """
    Limpia y sanitiza una cadena de texto de entrada para remover caracteres no deseados.

    Args:
        text: El texto a sanitizar.

    Returns:
        El texto sanitizado y normalizado.
    """
    if not text:
        return ""

    # Remover caracteres de control que no son visibles
    sanitized_text = CONTROL_CHARS_PATTERN.sub("", text)

    # Normalizar espacios en blanco (reemplaza múltiples espacios/saltos de línea por uno solo)
    sanitized_text = WHITESPACE_PATTERN.sub(" ", sanitized_text)

    if text != sanitized_text:
        logger.debug(f"Texto sanitizado de '{text[:100]}' a '{sanitized_text[:100]}'")

    return sanitized_text.strip()


def validate_file_upload(filename: str, allowed_extensions: List[str]) -> Tuple[bool, Optional[str]]:
    """
    Valida el nombre de un archivo subido, su extensión y caracteres.

    Args:
        filename: El nombre original del archivo.
        allowed_extensions: Una lista de extensiones de archivo permitidas (sin punto).

    Returns:
        Una tupla (es_valido, mensaje_error). Si es válido, mensaje_error es None.
    """
    if not filename:
        return False, "El nombre del archivo no puede estar vacío."

    if "." not in filename:
        return False, "El archivo no tiene una extensión."

    extension = filename.rsplit(".", 1)[1].lower()
    if extension not in [ext.lower() for ext in allowed_extensions]:
        allowed_str: str = ", ".join(allowed_extensions)
        logger.warning(f"Intento de subir archivo con extensión no permitida: '{extension}'. Permitidas: {allowed_str}")
        return (
            False,
            f"Extensión de archivo no permitida. Solo se aceptan: {allowed_str}",
        )

    if DANGEROUS_FILENAME_CHARS.search(filename):
        logger.warning(f"Nombre de archivo '{filename}' contiene caracteres no permitidos.")
        return False, "El nombre del archivo contiene caracteres no válidos."

    return True, None
