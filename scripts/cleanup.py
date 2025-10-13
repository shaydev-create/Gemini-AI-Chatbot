#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧹 LIMPIEZA DE ARCHIVOS INNECESARIOS - GEMINI AI CHATBOT

Este script elimina archivos duplicados y obsoletos para mantener un código limpio.
Identifica y elimina:
- Archivos de entorno duplicados
- Scripts redundantes
- Archivos temporales
- Archivos de configuración duplicados
"""

import argparse
import os
import re
import shutil
from pathlib import Path

# Constantes
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# Archivos a eliminar (rutas relativas al directorio raíz del proyecto)
FILES_TO_REMOVE = [
    # Archivos de configuración antiguos reemplazados por pyproject.toml
    "requirements.txt",
    "requirements-dev.txt",
    "setup.py",
    "pytest.ini",
    # Archivos de entorno duplicados (mantener solo .env y .env.example)
    ".env.backup",
    # Scripts redundantes (mantener versiones más recientes o completas)
    "scripts/setup_api_key.py",  # Reemplazado por setup_api_keys.py
]

# Directorios temporales a limpiar
DIRS_TO_CLEAN = ["__pycache__", ".pytest_cache", "build", "dist", "temp", "tmp"]

# Patrones de archivos temporales a eliminar
TEMP_FILE_PATTERNS = [
    r".*\.pyc$",
    r".*\.pyo$",
    r".*~$",
    r".*\.bak$",
    r".*\.swp$",
    r".*\.tmp$",
]


def print_banner():
    """Mostrar banner del script"""
    print("🧹 LIMPIEZA DE ARCHIVOS INNECESARIOS - GEMINI AI CHATBOT")
    print("=" * 60)
    print()


def remove_files():
    """Eliminar archivos específicos"""
    print("📋 Eliminando archivos duplicados o obsoletos...")

    for file_path in FILES_TO_REMOVE:
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            try:
                full_path.unlink()
                print(f"  ✅ Eliminado: {file_path}")
            except Exception as e:
                print(f"  ❌ Error al eliminar {file_path}: {str(e)}")
        else:
            print(f"  ⚠️ No encontrado: {file_path}")

    print()


def clean_temp_dirs():
    """Limpiar directorios temporales"""
    print("📋 Limpiando directorios temporales...")

    for root, dirs, files in os.walk(PROJECT_ROOT, topdown=True):
        # Excluir directorios .git y venv
        dirs[:] = [d for d in dirs if d not in [".git", "venv", "env"]]

        for dir_name in dirs.copy():
            if dir_name in DIRS_TO_CLEAN:
                dir_path = Path(root) / dir_name
                try:
                    shutil.rmtree(dir_path)
                    rel_path = dir_path.relative_to(PROJECT_ROOT)
                    print(f"  ✅ Eliminado directorio: {rel_path}")
                except Exception as e:
                    rel_path = dir_path.relative_to(PROJECT_ROOT)
                    print(
                        f"  ❌ Error al eliminar directorio {rel_path}: {
                            str(e)}"
                    )

    print()


def remove_temp_files():
    """Eliminar archivos temporales"""
    print("📋 Eliminando archivos temporales...")

    patterns = [re.compile(pattern) for pattern in TEMP_FILE_PATTERNS]

    for root, dirs, files in os.walk(PROJECT_ROOT, topdown=True):
        # Excluir directorios .git y venv
        dirs[:] = [d for d in dirs if d not in [".git", "venv", "env"]]

        for file_name in files:
            file_path = Path(root) / file_name
            for pattern in patterns:
                if pattern.match(file_name):
                    try:
                        file_path.unlink()
                        rel_path = file_path.relative_to(PROJECT_ROOT)
                        print(f"  ✅ Eliminado archivo temporal: {rel_path}")
                    except Exception as e:
                        rel_path = file_path.relative_to(PROJECT_ROOT)
                        print(
                            f"  ❌ Error al eliminar archivo {rel_path}: {
                                str(e)}"
                        )
                    break

    print()


def simulate_cleanup():
    """Simular el proceso de limpieza sin realizar cambios"""
    print("📋 Archivos que serían eliminados:")

    for file_path in FILES_TO_REMOVE:
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            print(f"  🔍 Se eliminaría: {file_path}")
        else:
            print(f"  ⚠️ No encontrado: {file_path}")

    print()
    print("📋 Directorios temporales que serían limpiados:")

    for dir_name in DIRS_TO_CLEAN:
        found = False
        for root, dirs, files in os.walk(PROJECT_ROOT, topdown=True):
            # Excluir directorios .git y venv
            if any(excluded in root for excluded in [".git", "venv", "env"]):
                continue

            if dir_name in dirs:
                dir_path = Path(root) / dir_name
                rel_path = dir_path.relative_to(PROJECT_ROOT)
                print(f"  🔍 Se limpiaría: {rel_path}")
                found = True

        if not found:
            print(f"  ⚠️ No se encontraron directorios: {dir_name}")

    print()
    print("📋 Patrones de archivos temporales que serían eliminados:")
    for pattern in TEMP_FILE_PATTERNS:
        print(f"  🔍 Patrón: {pattern}")

    print()


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Limpieza de archivos innecesarios")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostrar qué se eliminaría sin realizar cambios",
    )
    args = parser.parse_args()

    print_banner()

    if args.dry_run:
        print("⚠️ MODO SIMULACIÓN - No se realizarán cambios reales")
        print()
        simulate_cleanup()
    else:
        remove_files()
        clean_temp_dirs()
        remove_temp_files()

    print("✅ Proceso de limpieza completado")


if __name__ == "__main__":
    main()
