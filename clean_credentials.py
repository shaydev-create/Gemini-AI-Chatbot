#!/usr/bin/env python3
"""
Script de limpieza automática de credenciales
Protege tu proyecto antes de subirlo a GitHub
"""

import os
import shutil
import re
from pathlib import Path


def clean_credentials():
    """Limpia credenciales sensibles del proyecto"""

    print("🔒 Iniciando limpieza de credenciales...")

    # Archivos a proteger/eliminar
    sensitive_files = [
        '.env',
        '.env.backup',
        '.env.local',
        '.env.dev',
        '.env.prod',
        'credentials/',
        'vertex-ai-key.json'
    ]

    # Crear backup de .env si existe
    if os.path.exists('.env'):
        print("📋 Creando backup de .env...")
        shutil.copy('.env', '.env.local.backup')
        print("✅ Backup creado: .env.local.backup")

    # Eliminar archivos sensibles
    for file_path in sensitive_files:
        if os.path.exists(file_path):
            if os.path.isdir(file_path):
                print(f"🗂️  Eliminando directorio: {file_path}")
                shutil.rmtree(file_path)
            else:
                print(f"🗑️  Eliminando archivo: {file_path}")
                os.remove(file_path)

    # Verificar .env.example
    if os.path.exists('.env.example'):
        print("🔍 Verificando .env.example...")
        with open('.env.example', 'r', encoding='utf-8') as f:
            content = f.read()

        # Patrones de credenciales reales a detectar
        dangerous_patterns = [
            r'AIza[0-9A-Za-z-_]{35}',  # Google API Keys
            r'[A-Za-z0-9+/]{64,}={0,2}',  # Base64 keys largas
            r'sk-[a-zA-Z0-9]{48}',  # OpenAI keys
            r'[a-f0-9]{64}',  # Hex keys de 64 caracteres
        ]

        has_real_credentials = False
        for pattern in dangerous_patterns:
            if re.search(pattern, content):
                has_real_credentials = True
                break

        if has_real_credentials:
            print("⚠️  ADVERTENCIA: .env.example contiene credenciales reales!")
            print("   Revisa manualmente el archivo antes de hacer commit")
        else:
            print("✅ .env.example está limpio")

    # Verificar .gitignore
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'r', encoding='utf-8') as f:
            gitignore_content = f.read()

        required_entries = ['.env', '*.env', '.env.backup', 'credentials/']
        missing_entries = []

        for entry in required_entries:
            if entry not in gitignore_content:
                missing_entries.append(entry)

        if missing_entries:
            print(f"⚠️  Faltan entradas en .gitignore: {missing_entries}")
        else:
            print("✅ .gitignore está configurado correctamente")

    print("\n🎉 Limpieza completada!")
    print("\n📝 Pasos siguientes:")
    print("1. Revisa que .env.example no tenga credenciales reales")
    print("2. Ejecuta: git add .")
    print("3. Ejecuta: git commit -m 'Limpieza de credenciales'")
    print("4. Ejecuta: git push")
    print("\n🔄 Para restaurar tu .env local:")
    print("   cp .env.local.backup .env")


def check_git_status():
    """Verifica el estado de Git"""
    print("\n🔍 Verificando estado de Git...")
    os.system('git status --porcelain')


if __name__ == "__main__":
    clean_credentials()
    check_git_status()
