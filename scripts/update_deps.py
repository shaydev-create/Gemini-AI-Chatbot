#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 SCRIPT DE ACTUALIZACIÓN DE DEPENDENCIAS
Actualiza las dependencias del proyecto de manera segura.
"""

import subprocess
import sys
from pathlib import Path

def run_command(command, description, check=True):
    """Ejecuta un comando con manejo de errores."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(f"   ✅ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e.stderr.strip()}")
        return False

def main():
    """Función principal del script de actualización."""
    print("🔄 ACTUALIZACIÓN DE DEPENDENCIAS - GEMINI AI CHATBOT")
    print("=" * 55)
    
    # Verificar que estamos en un proyecto Poetry
    if not Path("pyproject.toml").exists():
        print("❌ No se encontró pyproject.toml")
        sys.exit(1)
    
    # Mostrar dependencias actuales
    print("📋 Dependencias actuales:")
    run_command("poetry show --tree", "Mostrando árbol de dependencias", check=False)
    
    # Verificar dependencias obsoletas
    print("\n🔍 Verificando dependencias obsoletas:")
    run_command("poetry show --outdated", "Verificando actualizaciones", check=False)
    
    # Preguntiar antes de actualizar
    response = input("\n❓ ¿Quieres actualizar las dependencias? (y/N): ").lower()
    
    if response in ['y', 'yes', 'sí', 's']:
        # Actualizar dependencias
        run_command("poetry update", "Actualizando dependencias")
        
        # Verificar que todo funciona
        print("\n🧪 Verificando instalación:")
        if run_command("poetry install --sync", "Sincronizando dependencias"):
            print("✅ Dependencias actualizadas correctamente")
            
            # Ejecutar tests básicos
            run_command("poetry run python -c 'import app; print(\"App importada correctamente\")'", 
                       "Verificando importaciones", check=False)
        else:
            print("❌ Error en la actualización")
    else:
        print("⏭️  Actualización cancelada")

if __name__ == "__main__":
    main()