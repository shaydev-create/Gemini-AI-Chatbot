#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 SCRIPT DE VERIFICACIÓN DEL SISTEMA
Verifica el estado del proyecto, dependencias y configuración.
"""

import json
import subprocess
import sys
from pathlib import Path

def check_python_version():
    """Verifica la versión de Python."""
    version = sys.version_info
    print(f"🐍 Python: {version.major}.{version.minor}.{version.micro}")
    
    if version < (3, 11):
        print("   ⚠️  Se recomienda Python 3.11+")
        return False
    else:
        print("   ✅ Versión compatible")
        return True

def check_poetry():
    """Verifica Poetry y dependencias."""
    try:
        result = subprocess.run(["poetry", "--version"], capture_output=True, text=True, check=True)
        print(f"📦 Poetry: {result.stdout.strip()}")
        
        # Verificar dependencias
        result = subprocess.run(["poetry", "check"], capture_output=True, text=True, check=True)
        print("   ✅ Dependencias verificadas")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"   ❌ Error con Poetry: {e}")
        return False

def check_environment():
    """Verifica variables de entorno."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    print("🔧 Variables de entorno:")
    
    if not env_file.exists():
        print("   ❌ Archivo .env no encontrado")
        if env_example.exists():
            print("   💡 Ejecuta: cp .env.example .env")
        return False
    
    # Verificar variables críticas
    try:
        env_content = env_file.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        try:
            env_content = env_file.read_text(encoding='cp1252')
        except UnicodeDecodeError:
            env_content = env_file.read_text(encoding='latin1')
    critical_vars = ["GEMINI_API_KEY", "SECRET_KEY", "FLASK_APP"]
    missing_vars = []
    
    for var in critical_vars:
        if f"{var}=" not in env_content or f"{var}=your_" in env_content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"   ⚠️  Variables por configurar: {', '.join(missing_vars)}")
        return False
    else:
        print("   ✅ Variables de entorno configuradas")
        return True

def check_database():
    """Verifica el estado de la base de datos."""
    print("🗄️ Base de datos:")
    
    instance_dir = Path("instance")
    if not instance_dir.exists():
        print("   ❌ Directorio instance no existe")
        return False
    
    db_files = list(instance_dir.glob("*.db"))
    if not db_files:
        print("   ⚠️  No se encontró base de datos")
        print("   💡 Ejecuta: flask db upgrade")
        return False
    
    print(f"   ✅ Base de datos encontrada: {db_files[0].name}")
    return True

def check_project_structure():
    """Verifica la estructura del proyecto."""
    print("📁 Estructura del proyecto:")
    
    required_dirs = ["app", "app/config", "tests", "docs", "scripts"]
    missing_dirs = []
    
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print(f"   ⚠️  Directorios faltantes: {', '.join(missing_dirs)}")
        return False
    else:
        print("   ✅ Estructura del proyecto completa")
        return True

def check_git_status():
    """Verifica el estado de Git."""
    try:
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)
        print("📝 Git:")
        
        if result.stdout.strip():
            lines = result.stdout.strip().split('\n')
            print(f"   ⚠️  {len(lines)} archivo(s) modificado(s)")
        else:
            print("   ✅ Repositorio limpio")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("   ❌ Git no disponible o no es un repositorio")
        return False

def main():
    """Función principal del script de verificación."""
    print("🔍 VERIFICACIÓN DEL SISTEMA - GEMINI AI CHATBOT")
    print("=" * 55)
    
    checks = [
        check_python_version,
        check_poetry,
        check_environment,
        check_database,
        check_project_structure,
        check_git_status
    ]
    
    results = []
    for check in checks:
        results.append(check())
        print()
    
    # Resumen
    passed = sum(results)
    total = len(results)
    
    print("📊 RESUMEN")
    print("=" * 20)
    print(f"✅ Verificaciones pasadas: {passed}/{total}")
    
    if passed == total:
        print("🎉 ¡Todo está en orden!")
        print("💡 Puedes ejecutar: poetry run python run_development.py")
    else:
        print("⚠️  Algunas verificaciones fallaron")
        print("💡 Revisa los mensajes anteriores para solucionar los problemas")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)