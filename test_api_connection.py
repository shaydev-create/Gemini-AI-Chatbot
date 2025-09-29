#!/usr/bin/env python3
"""
Script de diagnóstico para probar la conexión con la API de Google Gemini.
"""

import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

def test_api_connection():
    """Probar la conexión con la API de Gemini."""
    
    print("🔍 Diagnóstico de conexión API de Google Gemini")
    print("=" * 50)
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Verificar que existe el archivo .env
    env_file = ".env"
    if not os.path.exists(env_file):
        print("❌ ERROR: No se encontró el archivo .env")
        return False
    
    print(f"✅ Archivo .env encontrado: {env_file}")
    
    # Verificar API Key
    api_key = os.getenv('GOOGLE_API_KEY')
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    
    print(f"\n📋 Variables de entorno:")
    print(f"   GOOGLE_API_KEY: {'✅ Configurada' if api_key else '❌ No encontrada'}")
    print(f"   GEMINI_API_KEY: {'✅ Configurada' if gemini_api_key else '❌ No encontrada'}")
    
    # Usar la API Key disponible
    final_api_key = api_key or gemini_api_key
    
    if not final_api_key:
        print("\n❌ ERROR: No se encontró ninguna API Key válida")
        print("   Verifica que GOOGLE_API_KEY o GEMINI_API_KEY estén configuradas en .env")
        return False
    
    # Mostrar información de la API Key (parcialmente oculta por seguridad)
    masked_key = final_api_key[:8] + "*" * (len(final_api_key) - 12) + final_api_key[-4:]
    print(f"   API Key detectada: {masked_key}")
    
    # Configurar Gemini
    try:
        genai.configure(api_key=final_api_key)
        print("\n✅ API Key configurada correctamente")
    except Exception as e:
        print(f"\n❌ ERROR al configurar API Key: {e}")
        return False
    
    # Probar conexión con un mensaje simple
    try:
        print("\n🧪 Probando conexión con la API...")
        model = genai.GenerativeModel("gemini-2.0-flash-001")
        
        response = model.generate_content("Hola, responde solo con 'Conexión exitosa'")
        
        if response and response.text:
            print(f"✅ CONEXIÓN EXITOSA!")
            print(f"   Respuesta: {response.text.strip()}")
            return True
        else:
            print("❌ ERROR: Respuesta vacía de la API")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR de conexión: {e}")
        
        # Diagnóstico específico de errores
        error_str = str(e).lower()
        
        if "api_key_invalid" in error_str or "invalid" in error_str:
            print("\n🔧 DIAGNÓSTICO:")
            print("   - La API Key parece ser inválida")
            print("   - Verifica que copiaste la API Key completa")
            print("   - Genera una nueva API Key en: https://makersuite.google.com/app/apikey")
            
        elif "403" in error_str or "permission" in error_str:
            print("\n🔧 DIAGNÓSTICO:")
            print("   - Permisos denegados")
            print("   - Verifica que la API Key tenga permisos para Gemini")
            print("   - Asegúrate de que la API de Gemini esté habilitada")
            
        elif "429" in error_str or "quota" in error_str:
            print("\n🔧 DIAGNÓSTICO:")
            print("   - Has excedido el límite de la API")
            print("   - Espera un momento antes de intentar de nuevo")
            print("   - Verifica tu cuota en Google AI Studio")
            
        elif "network" in error_str or "connection" in error_str:
            print("\n🔧 DIAGNÓSTICO:")
            print("   - Problema de conexión de red")
            print("   - Verifica tu conexión a internet")
            print("   - Intenta de nuevo en unos momentos")
            
        else:
            print(f"\n🔧 DIAGNÓSTICO:")
            print(f"   - Error desconocido: {e}")
            print("   - Verifica la documentación de la API")
        
        return False

def main():
    """Función principal."""
    success = test_api_connection()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 RESULTADO: La API de Gemini está funcionando correctamente")
    else:
        print("💥 RESULTADO: Hay problemas con la conexión a la API")
        print("\n📝 PASOS RECOMENDADOS:")
        print("1. Verifica tu API Key en https://makersuite.google.com/app/apikey")
        print("2. Asegúrate de que la API Key esté correctamente copiada en .env")
        print("3. Verifica que no haya espacios extra al inicio o final")
        print("4. Intenta generar una nueva API Key si el problema persiste")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())