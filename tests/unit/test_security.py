# Test de seguridad para verificar que las funciones de seguridad funcionan correctamente

import os
import sys
import pytest
from pathlib import Path

# Agregar el directorio raíz al path para importar módulos
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Intentar importar los módulos de seguridad
try:
    from scripts.security_check import check_gitignore_entries, check_env_files_exist
    from scripts.secure_env import clean_env_file
    SECURITY_MODULES_AVAILABLE = True
except ImportError:
    SECURITY_MODULES_AVAILABLE = False

@pytest.mark.skipif(not SECURITY_MODULES_AVAILABLE, 
                    reason="Módulos de seguridad no disponibles")
def test_gitignore_entries():
    """Test que verifica que las entradas de .gitignore son correctas."""
    # Verificar que la función existe
    assert callable(check_gitignore_entries)
    
    # Crear un archivo .gitignore temporal para pruebas
    test_gitignore = Path(project_root) / ".gitignore.test"
    try:
        with open(test_gitignore, "w") as f:
            f.write(".env\n*.env\n.env.backup\n")
        
        # Verificar que la función detecta correctamente las entradas
        result = check_gitignore_entries(gitignore_path=str(test_gitignore))
        assert result is True, "La función debería detectar las entradas correctas"
        
    finally:
        # Limpiar archivo temporal
        if test_gitignore.exists():
            test_gitignore.unlink()

@pytest.mark.skipif(not SECURITY_MODULES_AVAILABLE, 
                    reason="Módulos de seguridad no disponibles")
def test_env_files_exist():
    """Test que verifica que la función de verificación de archivos .env funciona."""
    # Verificar que la función existe
    assert callable(check_env_files_exist)
    
    # Crear archivos temporales para pruebas
    test_env = Path(project_root) / ".env.test"
    test_env_example = Path(project_root) / ".env.example.test"
    
    try:
        # Crear archivos de prueba
        test_env.touch()
        test_env_example.touch()
        
        # Verificar que la función detecta correctamente los archivos
        result = check_env_files_exist(
            env_path=str(test_env),
            env_example_path=str(test_env_example)
        )
        assert result is True, "La función debería detectar los archivos correctamente"
        
    finally:
        # Limpiar archivos temporales
        if test_env.exists():
            test_env.unlink()
        if test_env_example.exists():
            test_env_example.unlink()

@pytest.mark.skipif(not SECURITY_MODULES_AVAILABLE, 
                    reason="Módulos de seguridad no disponibles")
def test_clean_env_file():
    """Test que verifica que la función de limpieza de archivos .env funciona."""
    # Verificar que la función existe
    assert callable(clean_env_file)
    
    # Crear un archivo .env temporal para pruebas
    test_env = Path(project_root) / ".env.test"
    test_env_backup = Path(project_root) / ".env.test.backup"
    
    try:
        # Crear archivo de prueba con credenciales de ejemplo
        with open(test_env, "w") as f:
            f.write("API_KEY=test_api_key_123456\nSECRET=test_secret_value\n")
        
        # Ejecutar la función de limpieza
        clean_env_file(env_path=str(test_env))
        
        # Verificar que se creó el archivo de backup
        assert test_env_backup.exists(), "Debería haberse creado un archivo de backup"
        
        # Verificar que el archivo original fue limpiado
        with open(test_env, "r") as f:
            content = f.read()
            assert "test_api_key_123456" not in content, "Las credenciales deberían haber sido eliminadas"
            assert "test_secret_value" not in content, "Las credenciales deberían haber sido eliminadas"
        
    finally:
        # Limpiar archivos temporales
        if test_env.exists():
            test_env.unlink()
        if test_env_backup.exists():
            test_env_backup.unlink()