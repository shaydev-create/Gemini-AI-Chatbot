def show_api_key_status(gemini_key, google_key):
    print("📋 ESTADO ACTUAL DE LAS CLAVES API:")
    if gemini_key:
        masked_key = gemini_key[:4] + "*" * (len(gemini_key) - 8) + gemini_key[-4:]
        print(f"✅ GEMINI_API_KEY: {masked_key}")
    else:
        print("❌ GEMINI_API_KEY: No configurada")
    if google_key:
        masked_key = google_key[:4] + "*" * (len(google_key) - 8) + google_key[-4:]
        print(f"✅ GOOGLE_API_KEY: {masked_key}")
    else:
        print("❌ GOOGLE_API_KEY: No configurada")
    print()

def prompt_for_new_api_key():
    print("🔑 CONFIGURACIÓN DE NUEVA API KEY")
    print("Obtén tu API key en: https://aistudio.google.com/")
    print()
    new_key = input("Ingresa tu API key de Gemini: ").strip()
    if not new_key:
        print("❌ No se ingresó ninguna API key")
        return None
    if not is_valid_api_key(new_key):
        print("⚠️ El formato de la API key no parece correcto")
        response = input("¿Deseas continuar de todos modos? (s/n): ").lower()
        if response != "s":
            print("❌ Configuración cancelada")
            return None
    print("🔍 Probando nueva API key...")
    success, message = test_gemini_api(new_key)
    if success:
        print(f"✅ API key válida: {message}")
    else:
        print(f"❌ API key inválida: {message}")
        response = input("¿Deseas guardar esta API key de todos modos? (s/n): ").lower()
        if response != "s":
            print("❌ Configuración cancelada")
            return None
    return new_key
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔑 CONFIGURADOR DE API KEYS - GEMINI AI CHATBOT

Este script ayuda a configurar las claves API de forma segura.
Permite configurar y probar las claves API de Gemini sin exponerlas.
"""

import os
import re
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

# Constantes
ENV_FILE = ".env"
ENV_SAMPLE_FILE = ".env-sample"
ENV_EXAMPLE_FILE = ".env.example"


def print_banner():
    """Mostrar banner del script"""
    print("🔑 CONFIGURADOR DE API KEYS - GEMINI AI CHATBOT")
    print("=" * 60)
    print()


def setup_env_file():
    """Configurar archivo .env si no existe"""
    env_path = Path(ENV_FILE)

    if env_path.exists():
        print(f"✅ Archivo {ENV_FILE} encontrado")
        return True

    # Buscar archivos de ejemplo
    sample_files = [ENV_SAMPLE_FILE, ENV_EXAMPLE_FILE]
    sample_path = None

    for sample in sample_files:
        if Path(sample).exists():
            sample_path = Path(sample)
            break

    if not sample_path:
        print(
            f"❌ No se encontró ningún archivo de ejemplo ({
                ', '.join(sample_files)})"
        )
        print(f"❌ Crea un archivo {ENV_FILE} manualmente")
        return False

    # Copiar archivo de ejemplo
    with open(sample_path, "r", encoding="utf-8") as f:
        sample_content = f.read()

    with open(env_path, "w", encoding="utf-8") as f:
        f.write(sample_content)

    print(f"✅ Archivo {ENV_FILE} creado a partir de {sample_path}")
    return True


def load_current_keys():
    """Cargar claves actuales del archivo .env"""
    load_dotenv(ENV_FILE)

    keys = {
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY", ""),
    }

    # Si GOOGLE_API_KEY está vacío pero GEMINI_API_KEY no, copiar valor
    if not keys["GOOGLE_API_KEY"] and keys["GEMINI_API_KEY"]:
        keys["GOOGLE_API_KEY"] = keys["GEMINI_API_KEY"]

    # Si GEMINI_API_KEY está vacío pero GOOGLE_API_KEY no, copiar valor
    if not keys["GEMINI_API_KEY"] and keys["GOOGLE_API_KEY"]:
        keys["GEMINI_API_KEY"] = keys["GOOGLE_API_KEY"]

    return keys


def is_valid_api_key(api_key):
    """Verificar si una API key tiene el formato correcto"""
    if not api_key:
        return False

    # Patrón típico de API key de Google
    pattern = r"^AIza[0-9A-Za-z\-_]{35,}$"
    return bool(re.match(pattern, api_key))


def test_gemini_api(api_key):
    """Probar API key de Gemini con una solicitud simple"""
    if not api_key:
        return False, "API key no proporcionada"

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": api_key}

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Hola, ¿puedes responder con una frase corta para verificar que la API funciona?"
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(
            url, headers=headers, params=params, json=data, timeout=10
        )

        if response.status_code == 200:
            return True, "API key válida"
        elif response.status_code == 400:
            return False, "Error en la solicitud"
        elif response.status_code == 401:
            return False, "API key inválida o no autorizada"
        elif response.status_code == 403:
            return False, "API key sin permisos suficientes"
        elif response.status_code == 429:
            return False, "Límite de cuota excedido"
        else:
            return False, f"Error desconocido (código {response.status_code})"

    except Exception as e:
        return False, f"Error de conexión: {str(e)}"


def update_env_file(key_name, key_value):
    """Actualizar clave en archivo .env"""
    env_path = Path(ENV_FILE)

    if not env_path.exists():
        print(f"❌ Archivo {ENV_FILE} no encontrado")
        return False

    try:
        # Leer contenido actual
        with open(env_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Buscar la clave en el archivo
        pattern = f"^{key_name}=.*$"
        replacement = f"{key_name}={key_value}"

        if re.search(pattern, content, re.MULTILINE):
            # Reemplazar valor existente
            new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        else:
            # Añadir nueva clave al final
            new_content = content.rstrip() + f"\n{replacement}\n"

        # Guardar cambios
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        return True

    except Exception as e:
        print(f"❌ Error al actualizar {ENV_FILE}: {str(e)}")
        return False


def setup_api_keys():
    """Configurar claves API interactivamente"""
    current_keys = load_current_keys()
    gemini_key = current_keys["GEMINI_API_KEY"]
    google_key = current_keys["GOOGLE_API_KEY"]
    show_api_key_status(gemini_key, google_key)
    if gemini_key and is_valid_api_key(gemini_key):
        print("🔍 Probando API key actual...")
        success, message = test_gemini_api(gemini_key)
        if success:
            print(f"✅ API key actual válida: {message}")
            print()
            response = input("¿Deseas configurar una nueva API key? (s/n): ").lower()
            if response != "s":
                print("✅ Configuración actual mantenida")
                return True
        else:
            print(f"❌ API key actual inválida: {message}")
            print()
    new_key = prompt_for_new_api_key()
    if not new_key:
        return False
    print("💾 Guardando API key en archivo .env...")
    if update_env_file("GEMINI_API_KEY", new_key) and update_env_file("GOOGLE_API_KEY", new_key):
        print("✅ API key guardada correctamente")
        return True
    else:
        print("❌ Error al guardar API key")
        return False


def main():
    """Función principal"""
    print_banner()

    # Configurar archivo .env
    if not setup_env_file():
        return False

    # Configurar claves API
    if not setup_api_keys():
        return False

    print()
    print("✅ CONFIGURACIÓN COMPLETADA")
    print("🚀 Ahora puedes ejecutar la aplicación con 'python app/main.py'")

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
