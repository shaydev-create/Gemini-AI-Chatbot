"""
Tests unitarios para utilidades.
"""

from app.utils.helpers import (
    format_bytes,
    generate_secret_key,
    hash_string,
    sanitize_filename,
    truncate_text,
)
from app.utils.validators import (
    sanitize_input,
    validate_api_key,
    validate_email,
    validate_file_upload,
    validate_message_content,
)


class TestHelpers:
    """Tests para funciones auxiliares."""

    def test_generate_secret_key(self):
        """Test generación de clave secreta."""
        key1 = generate_secret_key()
        key2 = generate_secret_key()

        assert len(key1) == 64  # 32 bytes * 2 (hex)
        assert len(key2) == 64
        assert key1 != key2  # Deben ser diferentes
        assert all(c in "0123456789abcdef" for c in key1)

    def test_hash_string(self):
        """Test hash de strings."""
        text = "test string"
        hash1 = hash_string(text)
        hash2 = hash_string(text)

        assert hash1 == hash2  # Mismo input, mismo hash
        assert len(hash1) == 64  # SHA256 = 64 chars hex

        # Diferente input, diferente hash
        hash3 = hash_string("different string")
        assert hash1 != hash3

    def test_sanitize_filename(self):
        """Test sanitización de nombres de archivo."""
        assert sanitize_filename("normal.txt") == "normal.txt"
        assert sanitize_filename("file<>name.txt") == "file__name.txt"
        assert sanitize_filename("file:with|bad*chars.txt") == "file_with_bad_chars.txt"

        # Test longitud máxima
        long_name = "a" * 300 + ".txt"
        sanitized = sanitize_filename(long_name)
        assert len(sanitized) <= 255
        assert sanitized.endswith(".txt")

    def test_format_bytes(self):
        """Test formateo de bytes."""
        assert format_bytes(512) == "512.0 B"
        assert format_bytes(1024) == "1.0 KB"
        assert format_bytes(1536) == "1.5 KB"
        assert format_bytes(1048576) == "1.0 MB"
        assert format_bytes(1073741824) == "1.0 GB"

    def test_truncate_text(self):
        """Test truncado de texto."""
        text = "Este es un texto muy largo para probar"

        assert truncate_text(text, 20) == "Este es un texto..."
        assert truncate_text(text, 100) == text  # No se trunca
        assert truncate_text(text, 20, "***") == "Este es un texto***"


class TestValidators:
    """Tests para validadores."""

    def test_validate_email(self):
        """Test validación de emails."""
        assert validate_email("test@example.com") is True
        assert validate_email("user.name+tag@domain.co.uk") is True
        assert validate_email("invalid.email") is False
        assert validate_email("@domain.com") is False
        assert validate_email("user@") is False
        assert validate_email("") is False

    def test_validate_message_content(self):
        """Test validación de contenido de mensajes."""
        # Mensaje válido
        valid, error = validate_message_content("Hola, ¿cómo estás?")
        assert valid is True
        assert error is None

        # Mensaje vacío
        valid, error = validate_message_content("")
        assert valid is False
        assert "vacío" in error

        # Mensaje muy corto
        valid, error = validate_message_content("a")
        assert valid is False
        assert "corto" in error

        # Mensaje muy largo
        long_message = "a" * 5000
        valid, error = validate_message_content(long_message)
        assert valid is False
        assert "excede" in error or "longitud" in error

        # Contenido peligroso
        dangerous = "<script>alert('xss')</script>"
        valid, error = validate_message_content(dangerous)
        assert valid is False
        assert "no permitido" in error

    def test_validate_api_key(self):
        """Test validación de API keys."""
        assert validate_api_key("valid_api_key_123456789") is True
        assert validate_api_key("short") is False
        assert validate_api_key("") is False
        assert validate_api_key(None) is False
        assert validate_api_key("invalid@key#with$symbols") is False

    def test_sanitize_input(self):
        """Test sanitización de entrada."""
        assert sanitize_input("  texto normal  ") == "texto normal"
        assert sanitize_input("texto\x00con\x1fcontrol") == "textoconcontrol"
        assert sanitize_input("texto   con    espacios") == "texto con espacios"
        assert sanitize_input("") == ""
        assert sanitize_input(None) == ""

    def test_validate_file_upload(self):
        """Test validación de archivos subidos."""
        allowed = ["jpg", "png", "gif"]

        # Archivo válido
        valid, error = validate_file_upload("image.jpg", allowed)
        assert valid is True
        assert error is None

        # Sin nombre
        valid, error = validate_file_upload("", allowed)
        assert valid is False
        assert "vacío" in error or "requerido" in error

        # Sin extensión
        valid, error = validate_file_upload("archivo", allowed)
        assert valid is False
        assert "extensión" in error

        # Extensión no permitida
        valid, error = validate_file_upload("document.pdf", allowed)
        assert valid is False
        assert "no permitida" in error

        # Caracteres peligrosos
        valid, error = validate_file_upload("file<script>.jpg", allowed)
        assert valid is False
        assert "no válidos" in error or "no permitidos" in error
