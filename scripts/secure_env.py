#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔒 PROTECTOR DE CREDENCIALES - GEMINI AI CHATBOT

Este script limpia el archivo .env de credenciales reales y las reemplaza con placeholders seguros.
Úsalo antes de hacer commit para evitar exponer información sensible.
"""

import re
import sys
from pathlib import Path


def print_banner():
    """Mostrar banner del script"""
    print("🔒 PROTECTOR DE CREDENCIALES - GEMINI AI CHATBOT")
    print("=" * 60)
    print()


def backup_env_file():
    """Crear backup del archivo .env"""
    env_file = Path(".env")
    backup_file = Path(".env.backup")

    if not env_file.exists():
        print("❌ Archivo .env no encontrado")
        return False

    # Crear backup
    with open(backup_file, "w", encoding="utf-8") as f:
        f.write(open(env_file, "r", encoding="utf-8").read())

    print(f"✅ Backup creado en {backup_file}")
    return True


def clean_env_file():
    """Limpiar credenciales del archivo .env"""
    env_file = Path(".env")
    env_example = Path(".env.example")

    if not env_file.exists():
        print("❌ Archivo .env no encontrado")
        return False

    if not env_example.exists():
        print("❌ Archivo .env.example no encontrado")
        return False

    # Leer contenido actual
    with open(env_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Leer ejemplo
    with open(env_example, "r", encoding="utf-8") as f:
        f.read()

    # Patrones a buscar y reemplazar
    patterns = [
        # API Keys
        (r"GOOGLE_API_KEY=([^\n]+)", "GOOGLE_API_KEY=tu_gemini_api_key_aqui"),
        (r"GEMINI_API_KEY=([^\n]+)", "GEMINI_API_KEY=tu_gemini_api_key_aqui"),
        # Claves de seguridad
        (r"SECRET_KEY=([^\n]+)", "SECRET_KEY=tu_secret_key_muy_seguro_aqui"),
        (r"JWT_SECRET_KEY=([^\n]+)", "JWT_SECRET_KEY=tu_jwt_secret_key_aqui"),
        # Credenciales de email
        (r"MAIL_USERNAME=([^\n]+)", "MAIL_USERNAME=your_email@gmail.com"),
        (r"MAIL_PASSWORD=([^\n]+)", "MAIL_PASSWORD=your_app_password"),
        # Claves PWA
        (r"VAPID_PUBLIC_KEY=([^\n]+)", "VAPID_PUBLIC_KEY=tu_vapid_public_key_aqui"),
        (r"VAPID_PRIVATE_KEY=([^\n]+)", "VAPID_PRIVATE_KEY=tu_vapid_private_key_aqui"),
    ]

    # Aplicar reemplazos
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    # Guardar archivo limpio
    with open(env_file, "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Archivo .env limpiado de credenciales")
    return True


def main():
    """Función principal"""
    print_banner()

    print("⚠️  Este script limpiará las credenciales reales del archivo .env")
    print("⚠️  Se creará un backup en .env.backup")
    print()

    response = input("¿Deseas continuar? (s/n): ").lower()
    if response != "s":
        print("❌ Operación cancelada")
        return False

    # Crear backup
    if not backup_env_file():
        return False

    # Limpiar archivo
    if not clean_env_file():
        return False

    print()
    print("✅ PROCESO COMPLETADO")
    print("📋 Ahora puedes hacer commit de forma segura")
    print("💡 Para restaurar tus credenciales, copia .env.backup a .env")

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Operación cancelada por el usuario.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
