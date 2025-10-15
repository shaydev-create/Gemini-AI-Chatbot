#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 SCRIPT DE VERIFICACIÓN DE COMPATIBILIDAD PYTHON 3.11/3.12
===========================================================

Este script ejecuta tests específicos para verificar que el proyecto
funciona correctamente en ambas versiones de Python.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> tuple[bool, str]:
    """Ejecuta un comando y devuelve el resultado."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            cwd=Path(__file__).parent.parent,
        )
        print(f"✅ {description} - EXITOSO")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FALLÓ")
        print(f"Error: {e.stderr}")
        return False, e.stderr
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False, str(e)


def check_python_version():
    """Verifica la versión actual de Python."""
    version = sys.version_info
    print(f"🐍 Python actual: {version.major}.{version.minor}.{version.micro}")

    if version[:2] not in [(3, 11), (3, 12), (3, 13)]:
        print(
            f"⚠️  Advertencia: Versión {version.major}.{version.minor} no está en el rango soportado"
        )
        return False
    return True


def run_compatibility_tests():
    """Ejecuta una serie de tests de compatibilidad."""
    print("🚀 Iniciando verificación de compatibilidad Python 3.11/3.12\n")

    if not check_python_version():
        print("❌ Versión de Python no soportada")
        return False

    # Lista de comandos a ejecutar
    tests = [
        {
            "cmd": [sys.executable, "-m", "ruff", "check", ".", "--quiet"],
            "description": "Verificación de linting (Ruff)",
        },
        {
            "cmd": [
                sys.executable,
                "-m",
                "pytest",
                "tests/test_basic.py",
                "-v",
                "--tb=short",
            ],
            "description": "Tests básicos",
        },
        {
            "cmd": [
                sys.executable,
                "-m",
                "pytest",
                "tests/test_main.py",
                "-v",
                "--tb=short",
            ],
            "description": "Tests principales",
        },
        {
            "cmd": [sys.executable, "-c", "import app; print('Import app exitoso')"],
            "description": "Verificación de imports principales",
        },
        {
            "cmd": [
                sys.executable,
                "-c",
                "from app.services.gemini_service import GeminiService; print('Import GeminiService exitoso')",
            ],
            "description": "Verificación de servicios",
        },
        {
            "cmd": [
                sys.executable,
                "-c",
                "from app.config.database import check_db_connection; print('Import database config exitoso')",
            ],
            "description": "Verificación de configuración de DB",
        },
        {
            "cmd": [
                sys.executable,
                "-c",
                'import flask; import sqlalchemy; from importlib import metadata; print(f\'Flask {metadata.version("flask")}, SQLAlchemy {metadata.version("sqlalchemy")}\')',
            ],
            "description": "Verificación de dependencias principales",
        },
    ]

    # Ejecutar todos los tests
    passed = 0
    failed = 0

    for test in tests:
        success, output = run_command(test["cmd"], test["description"])
        if success:
            passed += 1
            if output.strip():
                print(f"   📄 Output: {output.strip()}")
        else:
            failed += 1
        print()  # Línea en blanco

    # Resultados finales
    total = passed + failed
    print("=" * 60)
    print("📊 RESULTADOS FINALES:")
    print(f"   ✅ Pasaron: {passed}/{total}")
    print(f"   ❌ Fallaron: {failed}/{total}")
    print(f"   📈 Porcentaje éxito: {(passed / total * 100):.1f}%")

    if failed == 0:
        print("\n🎉 ¡TODOS LOS TESTS DE COMPATIBILIDAD PASARON!")
        print(
            f"✅ El proyecto es compatible con Python {sys.version_info.major}.{sys.version_info.minor}"
        )
        return True
    else:
        print(f"\n⚠️  {failed} test(s) fallaron. Revisar errores arriba.")
        return False


def main():
    """Función principal."""
    success = run_compatibility_tests()

    if success:
        print("\n🚀 Proyecto listo para CI/CD con múltiples versiones de Python!")
        sys.exit(0)
    else:
        print("\n❌ Se detectaron problemas de compatibilidad.")
        sys.exit(1)


if __name__ == "__main__":
    main()
