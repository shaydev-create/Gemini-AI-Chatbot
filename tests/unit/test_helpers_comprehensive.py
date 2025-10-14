"""
Tests comprehensivos para app/utils/helpers.py
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from app.utils.helpers import (
    ensure_directory_exists,
    format_bytes,
    generate_request_id,
    generate_secret_key,
    get_file_size,
    hash_string,
    sanitize_filename,
    truncate_text,
)


class TestHelpersComprehensive:
    """Tests comprehensivos para todas las funciones de helpers."""

    def test_generate_secret_key_lengths(self):
        """Test generación de claves secretas con diferentes longitudes."""
        # Test longitud por defecto
        key_default = generate_secret_key()
        assert len(key_default) == 64  # 32 bytes * 2 (hex)
        
        # Test longitud personalizada
        key_16 = generate_secret_key(16)
        assert len(key_16) == 32  # 16 bytes * 2
        
        key_64 = generate_secret_key(64)
        assert len(key_64) == 128  # 64 bytes * 2

    def test_generate_secret_key_uniqueness(self):
        """Test que las claves generadas son únicas."""
        keys = [generate_secret_key() for _ in range(10)]
        assert len(set(keys)) == 10  # Todas deben ser únicas

    def test_generate_request_id_uniqueness(self):
        """Test que los request IDs son únicos."""
        ids = [generate_request_id() for _ in range(10)]
        assert len(set(ids)) == 10  # Todos deben ser únicos

    def test_hash_string_different_algorithms(self):
        """Test hash con diferentes algoritmos."""
        text = "test string"
        
        # SHA256 (default)
        sha256_hash = hash_string(text, "sha256")
        assert len(sha256_hash) == 64
        
        # MD5
        md5_hash = hash_string(text, "md5")
        assert len(md5_hash) == 32
        
        # SHA1
        sha1_hash = hash_string(text, "sha1")
        assert len(sha1_hash) == 40

    def test_hash_string_invalid_algorithm_fallback(self):
        """Test que hash_string usa sha256 como fallback para algoritmos inválidos."""
        text = "test string"
        
        # Algoritmo inválido debería usar sha256 como fallback
        with patch('app.utils.helpers.logger') as mock_logger:
            hash_result = hash_string(text, "invalid_algorithm")
            
            # Debería devolver un hash válido
            assert len(hash_result) == 64
            assert all(c in "0123456789abcdef" for c in hash_result)
            
            # Debería registrar el error
            mock_logger.exception.assert_called_once()

    def test_ensure_directory_exists(self):
        """Test creación de directorios."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir) / "new_subdir" / "nested"
            
            # Directorio no debería existir inicialmente
            assert not test_dir.exists()
            
            # Crear directorio
            ensure_directory_exists(test_dir)
            assert test_dir.exists()
            assert test_dir.is_dir()
            
            # Intentar crear de nuevo (no debería fallar)
            ensure_directory_exists(test_dir)

    def test_ensure_directory_exists_error_handling(self):
        """Test manejo de errores en creación de directorios."""
        # Mock para simular error de permisos
        with patch('pathlib.Path.mkdir', side_effect=OSError("Permission denied")):
            with patch('app.utils.helpers.logger') as mock_logger:
                # Debería manejar el error gracefulmente
                ensure_directory_exists("/invalid/path")
                mock_logger.exception.assert_called_once()

    def test_get_file_size_existing_file(self):
        """Test obtener tamaño de archivo existente."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"test content")
            temp_file.flush()
            
            size = get_file_size(temp_file.name)
            assert size == len(b"test content")
            
            # Cerrar el archivo antes de intentar eliminarlo
            temp_file.close()
            os.unlink(temp_file.name)

    def test_get_file_size_nonexistent_file(self):
        """Test obtener tamaño de archivo que no existe."""
        with patch('app.utils.helpers.logger') as mock_logger:
            size = get_file_size("/nonexistent/file.txt")
            assert size is None
            mock_logger.debug.assert_called_once()

    def test_sanitize_filename_edge_cases(self):
        """Test casos edge de sanitización de nombres de archivo."""
        # Caracteres especiales
        assert sanitize_filename("file<>.txt") == "file__.txt"
        assert sanitize_filename("file:with|bad*chars.txt") == "file_with_bad_chars.txt"
        
        # Nombres muy largos
        long_name = "a" * 300 + ".txt"
        sanitized = sanitize_filename(long_name)
        assert len(sanitized) <= 255
        assert sanitized.endswith(".txt")
        
        # Sin extensión
        assert sanitize_filename("no_extension") == "no_extension"
        
        # Múltiples puntos
        assert sanitize_filename("file.name.with.dots.txt") == "file.name.with.dots.txt"

    def test_format_bytes_edge_cases(self):
        """Test casos edge de formateo de bytes."""
        # Bytes
        assert format_bytes(0) == "0.0 B"
        assert format_bytes(1) == "1.0 B"
        assert format_bytes(1023) == "1023.0 B"
        
        # Kilobytes
        assert format_bytes(1024) == "1.0 KB"
        assert format_bytes(1536) == "1.5 KB"
        
        # Megabytes
        assert format_bytes(1048576) == "1.0 MB"
        
        # Gigabytes
        assert format_bytes(1073741824) == "1.0 GB"
        
        # Terabytes
        assert format_bytes(1099511627776) == "1.0 TB"
        
        # Valores inválidos
        assert format_bytes(-1) == "0 B"
        assert format_bytes(None) == "0 B"

    def test_truncate_text_comprehensive(self):
        """Test comprehensivo de truncado de texto."""
        text = "Este es un texto de prueba para truncar"
        
        # No truncar si es más corto que el límite
        assert truncate_text(text, 100) == text
        
        # Truncar con sufijo por defecto
        truncated = truncate_text(text, 20)
        assert len(truncated) <= 20 + len("...")
        assert truncated.endswith("...")
        
        # Truncar con sufijo personalizado
        truncated_custom = truncate_text(text, 20, "***")
        assert truncated_custom.endswith("***")
        
        # Texto exactamente en el límite
        exact_text = "a" * 20
        assert truncate_text(exact_text, 20) == exact_text
        
        # Texto vacío
        assert truncate_text("", 10) == ""
        # None debería devolver None (no es una cadena)
        assert truncate_text(None, 10) is None

    def test_all_functions_importable(self):
        """Test que todas las funciones son importables y callables."""
        from app.utils.helpers import (
            ensure_directory_exists,
            format_bytes,
            generate_request_id,
            generate_secret_key,
            get_file_size,
            hash_string,
            sanitize_filename,
            truncate_text,
        )
        
        # Verificar que todas son callables
        assert callable(ensure_directory_exists)
        assert callable(format_bytes)
        assert callable(generate_request_id)
        assert callable(generate_secret_key)
        assert callable(get_file_size)
        assert callable(hash_string)
        assert callable(sanitize_filename)
        assert callable(truncate_text)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])