"""
Validadores para la aplicación.
"""

import re
from typing import List, Optional


def validate_email(email: str) -> bool:
    """
    Validar formato de email.

    Args:
        email: Email a validar

    Returns:
        True si es válido
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_message_content(message: str) -> tuple[bool, Optional[str]]:
    """
    Validar contenido de mensaje.

    Args:
        message: Mensaje a validar

    Returns:
        Tupla (es_válido, mensaje_error)
    """
    if not message or not message.strip():
        return False, "El mensaje no puede estar vacío"

    if len(message) > 4000:
        return False, "El mensaje es demasiado largo (máximo 4000 caracteres)"

    if len(message.strip()) < 2:
        return False, "El mensaje es demasiado corto (mínimo 2 caracteres)"

    # Verificar caracteres peligrosos
    dangerous_patterns = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, message, re.IGNORECASE):
            return False, "El mensaje contiene contenido no permitido"

    return True, None


def validate_api_key(api_key: str) -> bool:
    """
    Validar formato de API key.

    Args:
        api_key: API key a validar

    Returns:
        True si el formato es válido
    """
    if not api_key:
        return False

    # Verificar longitud mínima
    if len(api_key) < 10:
        return False

    # Verificar que solo contenga caracteres alfanuméricos y guiones bajos
    pattern = r"^[a-zA-Z0-9_]+$"
    return bool(re.match(pattern, api_key))


def sanitize_input(text: Optional[str]) -> str:
    """
    Sanitizar entrada de usuario.

    Args:
        text: Texto a sanitizar

    Returns:
        Texto sanitizado
    """
    if not text:
        return ""

    # Remover caracteres de control
    text = re.sub(r"[\x00-\x1f\x7f]", "", text)

    # Normalizar espacios en blanco
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def validate_file_upload(
    filename: str, allowed_extensions: List[str]
) -> tuple[bool, Optional[str]]:
    """
    Validar archivo subido.

    Args:
        filename: Nombre del archivo
        allowed_extensions: Extensiones permitidas

    Returns:
        Tupla (es_válido, mensaje_error)
    """
    if not filename:
        return False, "Nombre de archivo requerido"

    # Verificar extensión
    if "." not in filename:
        return False, "Archivo sin extensión"

    extension = filename.rsplit(".", 1)[1].lower()
    if extension not in [ext.lower() for ext in allowed_extensions]:
        return (
            False,
            f"Extensión no permitida. Permitidas: {
                ', '.join(allowed_extensions)}",
        )

    # Verificar caracteres peligrosos en el nombre
    dangerous_chars = ["<", ">", ":", '"', "|", "?", "*", "\\", "/"]
    for char in dangerous_chars:
        if char in filename:
            return False, "Nombre de archivo contiene caracteres no permitidos"

    return True, None
