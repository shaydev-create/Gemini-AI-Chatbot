#!/usr/bin/env python3
"""
Script para listar los modelos disponibles de Google Gemini.
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

def list_available_models():
    """Listar todos los modelos disponibles de Gemini."""
    
    print("📋 Modelos disponibles de Google Gemini")
    print("=" * 50)
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Obtener API Key
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ ERROR: No se encontró API Key")
        return
    
    # Configurar Gemini
    genai.configure(api_key=api_key)
    
    try:
        print("🔍 Obteniendo lista de modelos...")
        models = genai.list_models()
        
        print(f"\n✅ Modelos encontrados:")
        print("-" * 30)
        
        for model in models:
            print(f"📦 {model.name}")
            if hasattr(model, 'display_name'):
                print(f"   Nombre: {model.display_name}")
            if hasattr(model, 'description'):
                print(f"   Descripción: {model.description}")
            if hasattr(model, 'supported_generation_methods'):
                print(f"   Métodos: {', '.join(model.supported_generation_methods)}")
            print()
            
    except Exception as e:
        print(f"❌ ERROR al obtener modelos: {e}")

if __name__ == "__main__":
    list_available_models()