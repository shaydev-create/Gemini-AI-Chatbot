#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛠️ SCRIPT DE CONFIGURACIÓN INICIAL
Script automatizado para configurar el proyecto Gemini AI Chatbot.
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description, check=True):
    """Ejecuta un comando del sistema con manejo de errores."""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(f"   ✅ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e.stderr.strip()}")
        return False

def check_poetry():
    """Verifica si Poetry está instalado."""
    try:
        subprocess.run(["poetry", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def main():
    """Función principal del script de configuración."""
    print("🚀 CONFIGURACIÓN INICIAL - GEMINI AI CHATBOT")
    print("=" * 50)
    
    # Verificar Poetry
    if not check_poetry():
        print("❌ Poetry no está instalado. Instalando...")
        if not run_command("pip install poetry", "Instalando Poetry"):
            print("💥 Error al instalar Poetry. Instálalo manualmente.")
            sys.exit(1)
    else:
        print("✅ Poetry ya está instalado")
    
    # Instalar dependencias
    run_command("poetry install", "Instalando dependencias")
    
    # Crear archivo .env si no existe
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("📝 Creando archivo .env desde .env.example...")
        env_file.write_text(env_example.read_text())
        print("   ⚠️  Recuerda configurar GEMINI_API_KEY en .env")
    
    # Crear directorios necesarios
    dirs_to_create = ["instance", "logs", "reports", "uploads"]
    for dir_name in dirs_to_create:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"📁 Directorio {dir_name} creado/verificado")
    
    # Inicializar base de datos
    print("🗄️ Configurando base de datos...")
    run_command("poetry run flask db upgrade", "Aplicando migraciones de DB", check=False)
    
    print("\n🎉 ¡Configuración completada!")
    print("📋 Próximos pasos:")
    print("   1. Configura GEMINI_API_KEY en .env")
    print("   2. Ejecuta: poetry run python run_development.py")
    print("   3. Abre http://localhost:5000")

if __name__ == "__main__":
    main()