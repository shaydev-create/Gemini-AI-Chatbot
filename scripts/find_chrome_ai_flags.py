#!/usr/bin/env python3
"""
Script para ayudar a encontrar y configurar los flags de Chrome Built-in AI
"""

import webbrowser
import time
import sys

def print_banner():
    print("🔍 Chrome Built-in AI Flags Finder")
    print("=" * 50)
    print()

def print_flag_instructions():
    """Muestra las instrucciones para encontrar los flags"""
    
    print("📋 FLAGS DE CHROME BUILT-IN AI A BUSCAR:")
    print("-" * 40)
    
    # Lista de flags actualizados (pueden tener nombres diferentes)
    flags_to_find = [
        {
            "name": "Prompt API for Gemini Nano",
            "possible_flags": [
                "#prompt-api-for-gemini-nano",
                "#optimization-guide-on-device-model", 
                "#prompt-api",
                "#gemini-nano-api"
            ],
            "description": "Habilita la API principal de conversación"
        },
        {
            "name": "Summarization API",
            "possible_flags": [
                "#summarization-api-for-gemini-nano",
                "#summarization-api",
                "#ai-summarization"
            ],
            "description": "API para resumir textos"
        },
        {
            "name": "Rewriter API", 
            "possible_flags": [
                "#rewriter-api-for-gemini-nano",
                "#rewriter-api",
                "#ai-rewriter"
            ],
            "description": "API para reescribir y mejorar textos"
        },
        {
            "name": "Composer API",
            "possible_flags": [
                "#composer-api-for-gemini-nano", 
                "#composer-api",
                "#ai-composer"
            ],
            "description": "API para generar contenido"
        },
        {
            "name": "Translation API",
            "possible_flags": [
                "#translation-api",
                "#ai-translation",
                "#built-in-translation"
            ],
            "description": "API para traducción"
        },
        {
            "name": "AI Assistant API",
            "possible_flags": [
                "#ai-assistant-api",
                "#built-in-ai-api",
                "#experimental-web-ai"
            ],
            "description": "API general de asistente AI"
        }
    ]
    
    for i, flag_info in enumerate(flags_to_find, 1):
        print(f"{i}. 🏷️  {flag_info['name']}")
        print(f"   📝 {flag_info['description']}")
        print(f"   🔍 Buscar por:")
        for possible_flag in flag_info['possible_flags']:
            print(f"      • {possible_flag}")
        print()

def print_search_instructions():
    """Muestra cómo buscar los flags"""
    
    print("🔍 CÓMO BUSCAR LOS FLAGS:")
    print("-" * 25)
    print("1. 🌐 Abre Chrome Canary")
    print("2. 📍 Ve a: chrome://flags/")
    print("3. 🔍 Usa la caja de búsqueda en la parte superior")
    print("4. 🕵️  Busca estos términos UNO POR UNO:")
    print()
    
    search_terms = [
        "gemini",
        "nano", 
        "prompt",
        "summarization",
        "rewriter", 
        "composer",
        "translation",
        "ai assistant",
        "optimization guide",
        "on device model"
    ]
    
    for term in search_terms:
        print(f"   🔍 '{term}'")
    
    print()
    print("5. ✅ Cambia TODOS los que encuentres a 'Enabled'")
    print("6. 🔄 Reinicia Chrome Canary")
    print()

def print_verification_steps():
    """Muestra cómo verificar si funcionó"""
    
    print("✅ VERIFICACIÓN:")
    print("-" * 15)
    print("1. 🌐 Ve a tu aplicación: http://127.0.0.1:5000")
    print("2. 🎯 Busca el botón '🤖 Chrome AI'")
    print("3. 📋 Haz clic y selecciona '🧠 Local'")
    print("4. ✨ Si funciona, verás notificación de éxito")
    print("5. 🧪 Si no funciona, el botón dirá '(N/A)'")
    print()

def print_alternative_method():
    """Muestra método alternativo si los flags no aparecen"""
    
    print("🚨 SI NO ENCUENTRAS LOS FLAGS:")
    print("-" * 30)
    print("1. 📥 Asegúrate de tener Chrome Canary (no Chrome regular)")
    print("2. 🔄 Actualiza Chrome Canary a la versión más reciente")
    print("3. 🏷️  Ve a chrome://version/ y verifica que dice 'canary'")
    print("4. 🔧 Intenta estos flags alternativos:")
    print()
    
    alternative_flags = [
        "#experimental-web-ai",
        "#enable-ai-assistant",
        "#optimization-guide-model-execution",
        "#prompt-api",
        "#built-in-ai"
    ]
    
    for flag in alternative_flags:
        print(f"   • {flag}")
    print()

def open_chrome_flags():
    """Abre la página de flags de Chrome automáticamente"""
    
    print("🚀 ABRIENDO CHROME FLAGS...")
    print("Si no se abre automáticamente, copia esta URL:")
    print("chrome://flags/")
    print()
    
    try:
        # Intentar abrir Chrome flags (puede no funcionar en algunos sistemas)
        webbrowser.open("chrome://flags/")
        time.sleep(2)
        print("✅ Página abierta! Busca los flags arriba mencionados.")
    except:
        print("⚠️  No se pudo abrir automáticamente.")
        print("📋 Copia y pega manualmente: chrome://flags/")
    print()

def main():
    print_banner()
    
    print("¿Qué quieres hacer?")
    print("1. 📋 Ver lista de flags a buscar")
    print("2. 🔍 Ver instrucciones de búsqueda")
    print("3. 🌐 Abrir Chrome flags automáticamente")
    print("4. ✅ Ver cómo verificar si funciona")
    print("5. 🚨 Métodos alternativos si no encuentras flags")
    print("6. 🎯 Todo lo anterior (recomendado)")
    print()
    
    try:
        choice = input("Elige una opción (1-6): ").strip()
        print()
        
        if choice == "1":
            print_flag_instructions()
        elif choice == "2":
            print_search_instructions()
        elif choice == "3":
            open_chrome_flags()
        elif choice == "4":
            print_verification_steps()
        elif choice == "5":
            print_alternative_method()
        elif choice == "6":
            print_flag_instructions()
            print_search_instructions()
            print_verification_steps()
            print_alternative_method()
            
            answer = input("¿Quieres abrir Chrome flags ahora? (y/n): ")
            if answer.lower() in ['y', 'yes', 's', 'si']:
                open_chrome_flags()
        else:
            print("❌ Opción inválida")
            
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta luego!")
        sys.exit(0)
    
    print()
    print("💡 CONSEJO FINAL:")
    print("Si algunos flags no aparecen, no te preocupes.")
    print("Chrome Built-in AI está en desarrollo activo y")
    print("los flags pueden cambiar entre versiones.")
    print()
    print("🎯 Lo importante es habilitar TODOS los relacionados")
    print("con 'AI', 'Gemini', 'Nano' que encuentres!")

if __name__ == "__main__":
    main()