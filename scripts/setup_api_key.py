#!/usr/bin/env python3
"""
🔑 CONFIGURADOR DE API KEY - GEMINI AI CHATBOT

Este script te ayuda a configurar correctamente la API key de Google Gemini.
"""

import os
import sys
from pathlib import Path
import re

def print_banner():
    """Mostrar banner del configurador"""
    print("🔑 CONFIGURADOR DE API KEY - GEMINI AI CHATBOT")
    print("=" * 60)
    print()

def check_current_config():
    """Verificar configuración actual"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ Archivo .env no encontrado")
        return None
    
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar API keys
    gemini_key_match = re.search(r'GEMINI_API_KEY=(.+)', content)
    google_key_match = re.search(r'GOOGLE_API_KEY=(.+)', content)
    
    current_gemini = gemini_key_match.group(1).strip() if gemini_key_match else None
    current_google = google_key_match.group(1).strip() if google_key_match else None
    
    print("📋 CONFIGURACIÓN ACTUAL:")
    print(f"   GEMINI_API_KEY: {current_gemini}")
    print(f"   GOOGLE_API_KEY: {current_google}")
    print()
    
    # Verificar si son keys de prueba
    test_keys = ['test_key_for_validation', 'your_api_key_here', 'tu_api_key_aqui']
    
    if current_gemini in test_keys or current_google in test_keys:
        print("⚠️  DETECTADAS CLAVES DE PRUEBA - Se requiere configuración")
        return False
    elif current_gemini and len(current_gemini) > 30:
        print("✅ API Key configurada (verificando validez...)")
        return current_gemini
    else:
        print("❌ API Key no configurada correctamente")
        return False

def validate_api_key(api_key):
    """Validar formato de API key"""
    if not api_key:
        return False, "API key vacía"
    
    if len(api_key) < 30:
        return False, "API key demasiado corta"
    
    if api_key.startswith('AIza'):
        return True, "Formato válido de Google API Key"
    else:
        return False, "Formato de API key no reconocido (debería empezar con 'AIza')"

def test_api_key(api_key):
    """Probar API key con Google Gemini"""
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Hacer una prueba simple
        response = model.generate_content("Responde solo con 'OK' si puedes leer este mensaje")
        
        if response and response.text:
            return True, "API key válida y funcional"
        else:
            return False, "API key no responde correctamente"
            
    except Exception as e:
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg:
            return False, "API key inválida"
        elif "PERMISSION_DENIED" in error_msg:
            return False, "API key sin permisos para Gemini"
        else:
            return False, f"Error de conexión: {error_msg}"

def update_env_file(new_api_key):
    """Actualizar archivo .env con nueva API key"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ Archivo .env no encontrado")
        return False
    
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Actualizar ambas claves
    content = re.sub(r'GEMINI_API_KEY=.+', f'GEMINI_API_KEY={new_api_key}', content)
    content = re.sub(r'GOOGLE_API_KEY=.+', f'GOOGLE_API_KEY={new_api_key}', content)
    
    # Crear backup
    backup_file = env_file.with_suffix('.env.backup')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(open(env_file, 'r', encoding='utf-8').read())
    
    # Escribir nueva configuración
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Archivo .env actualizado (backup en {backup_file.name})")
    return True

def show_instructions():
    """Mostrar instrucciones para obtener API key"""
    print("📖 CÓMO OBTENER TU API KEY DE GOOGLE GEMINI:")
    print()
    print("1. 🌐 Ve a Google AI Studio:")
    print("   https://makersuite.google.com/app/apikey")
    print()
    print("2. 🔐 Inicia sesión con tu cuenta de Google")
    print()
    print("3. ➕ Haz clic en 'Create API Key'")
    print()
    print("4. 📋 Copia la API key generada")
    print("   (Debería empezar con 'AIza...')")
    print()
    print("5. 🔒 Guarda la clave de forma segura")
    print("   (No la compartas públicamente)")
    print()
    print("⚠️  IMPORTANTE:")
    print("   • La API key es gratuita para uso básico")
    print("   • Revisa los límites de uso en Google AI Studio")
    print("   • Mantén tu clave privada y segura")
    print()

def main():
    """Función principal"""
    print_banner()
    
    # Verificar configuración actual
    current_config = check_current_config()
    
    if current_config and current_config != False:
        # Probar API key actual
        print("🧪 Probando API key actual...")
        is_valid, message = test_api_key(current_config)
        
        if is_valid:
            print(f"✅ {message}")
            print()
            print("🎉 ¡Tu API key está configurada y funcionando correctamente!")
            return True
        else:
            print(f"❌ {message}")
            print()
    
    # Mostrar instrucciones
    show_instructions()
    
    # Solicitar nueva API key
    print("🔑 CONFIGURAR NUEVA API KEY:")
    print()
    
    while True:
        api_key = input("Ingresa tu API key de Google Gemini: ").strip()
        
        if not api_key:
            print("❌ No ingresaste ninguna clave. Intenta de nuevo.")
            continue
        
        # Validar formato
        is_valid_format, format_msg = validate_api_key(api_key)
        if not is_valid_format:
            print(f"❌ {format_msg}")
            continue
        
        print(f"✅ {format_msg}")
        
        # Probar API key
        print("🧪 Probando API key...")
        is_working, test_msg = test_api_key(api_key)
        
        if is_working:
            print(f"✅ {test_msg}")
            
            # Actualizar archivo .env
            if update_env_file(api_key):
                print()
                print("🎉 ¡API key configurada exitosamente!")
                print()
                print("📋 PRÓXIMOS PASOS:")
                print("   1. Reinicia el servidor (Ctrl+C y luego python app.py)")
                print("   2. Prueba el chatbot en https://localhost:5000")
                print("   3. ¡Disfruta de tu chatbot con IA!")
                return True
            else:
                print("❌ Error actualizando configuración")
                return False
        else:
            print(f"❌ {test_msg}")
            
            retry = input("\n¿Quieres intentar con otra API key? (s/n): ").lower()
            if retry != 's':
                break
    
    print("\n⚠️  Configuración cancelada. El chatbot no funcionará sin una API key válida.")
    return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Configuración cancelada por el usuario.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)