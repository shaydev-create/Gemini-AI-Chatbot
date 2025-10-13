#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ VERIFICADOR DE SEGURIDAD - GEMINI AI CHATBOT

Este script ejecuta todas las verificaciones de seguridad en un solo comando.
Verifica credenciales expuestas, limpia archivos sensibles y muestra recomendaciones.
"""

import subprocess
import sys
from pathlib import Path


def print_banner():
    """Mostrar banner del script"""
    print("🛡️ VERIFICADOR DE SEGURIDAD - GEMINI AI CHATBOT")
    print("=" * 60)
    print()


def run_script(script_name, description):
    """Ejecutar un script Python y mostrar resultado"""
    script_path = Path('scripts') / script_name

    if not script_path.exists():
        print(f"❌ Script no encontrado: {script_path}")
        return False

    print(f"🔍 {description}...")
    print("-" * 60)

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            check=False
        )
        success = result.returncode == 0

        if success:
            print(f"✅ {description} completado")
        else:
            print(f"⚠️ {description} completado con advertencias")

        print()
        return success

    except Exception as e:
        print(f"❌ Error al ejecutar {script_name}: {e}")
        print()
        return False


def check_gitignore():
    """Verificar que .gitignore contiene entradas para archivos sensibles"""
    gitignore_path = Path('.gitignore')

    if not gitignore_path.exists():
        print("❌ Archivo .gitignore no encontrado")
        return False

    with open(gitignore_path, 'r', encoding='utf-8') as f:
        content = f.read()

    required_entries = [
        '.env',
        '*.env',
        '.env.*',
        '!.env.example',
        '!.env-sample',
    ]

    missing_entries = []
    for entry in required_entries:
        if entry not in content:
            missing_entries.append(entry)

    if missing_entries:
        print("⚠️ Entradas faltantes en .gitignore:")
        for entry in missing_entries:
            print(f"   - {entry}")
        print()
        return False
    else:
        print("✅ Archivo .gitignore correctamente configurado")
        print()
        return True


def check_env_files():
    """Verificar archivos de entorno"""
    env_path = Path('.env')
    env_example_path = Path('.env.example')
    env_sample_path = Path('.env-sample')

    if not env_path.exists():
        print("⚠️ Archivo .env no encontrado")
    else:
        print("✅ Archivo .env encontrado")

    if not (env_example_path.exists() or env_sample_path.exists()):
        print("⚠️ No se encontró archivo de ejemplo (.env.example o .env-sample)")
        return False
    else:
        print("✅ Archivo de ejemplo encontrado")

    print()
    return True


def check_gitattributes():
    """Verificar archivo .gitattributes"""
    gitattributes_path = Path('.gitattributes')

    if not gitattributes_path.exists():
        print("⚠️ Archivo .gitattributes no encontrado")
        return False

    with open(gitattributes_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if '.env filter=git-crypt' not in content:
        print("⚠️ Configuración de git-crypt no encontrada en .gitattributes")
        return False
    else:
        print("✅ Archivo .gitattributes correctamente configurado")

    print()
    return True


def show_recommendations():
    """Mostrar recomendaciones finales"""
    print("🔐 RECOMENDACIONES DE SEGURIDAD")
    print("-" * 60)
    print("1. Antes de hacer commit, ejecuta: python scripts/secure_env.py")
    print("2. Verifica regularmente: python scripts/check_exposed_credentials.py")
    print("3. Para configurar API keys: python scripts/setup_api_keys.py")
    print("4. Lee la guía completa: docs/SEGURIDAD_CREDENCIALES.md")
    print()
    print("⚠️  IMPORTANTE: Nunca subas credenciales reales a GitHub")
    print()


def main():
    """Función principal"""
    print_banner()

    # Verificar archivos de configuración
    check_gitignore()
    check_env_files()
    check_gitattributes()

    # Ejecutar scripts de seguridad
    run_script(
        'check_exposed_credentials.py',
        'Verificando credenciales expuestas')
    run_script('secure_env.py', 'Limpiando archivo .env')

    # Mostrar recomendaciones
    show_recommendations()

    print("✅ VERIFICACIÓN DE SEGURIDAD COMPLETADA")
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
