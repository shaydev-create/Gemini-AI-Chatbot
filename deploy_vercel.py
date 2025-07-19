#!/usr/bin/env python3
"""
🚀 SCRIPT DE DEPLOYMENT AUTOMÁTICO PARA VERCEL
Automatiza el proceso de deployment y configuración
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_vercel_cli():
    """Verificar si Vercel CLI está instalado"""
    try:
        result = subprocess.run(['vercel', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Vercel CLI instalado: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Vercel CLI no está instalado")
        print("📦 Instálalo con: npm i -g vercel")
        return False

def check_git_status():
    """Verificar estado de Git"""
    try:
        # Verificar si hay cambios sin commit
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        
        if result.stdout.strip():
            print("⚠️  Hay cambios sin commit:")
            print(result.stdout)
            
            response = input("¿Quieres hacer commit automáticamente? (y/n): ")
            if response.lower() == 'y':
                subprocess.run(['git', 'add', '.'], check=True)
                subprocess.run(['git', 'commit', '-m', 'Deploy: Configuración Vercel optimizada'], check=True)
                print("✅ Cambios commiteados")
            else:
                print("❌ Deployment cancelado. Haz commit de los cambios primero.")
                return False
        
        return True
    except subprocess.CalledProcessError:
        print("❌ Error verificando Git status")
        return False

def deploy_to_vercel():
    """Ejecutar deployment a Vercel"""
    try:
        print("🚀 Iniciando deployment a Vercel...")
        
        # Deploy a preview primero
        print("📋 Deploying preview...")
        result = subprocess.run(['vercel'], capture_output=True, text=True, check=True)
        preview_url = result.stdout.strip().split('\n')[-1]
        print(f"✅ Preview URL: {preview_url}")
        
        # Preguntar si hacer deploy a producción
        response = input("¿Quieres hacer deploy a producción? (y/n): ")
        if response.lower() == 'y':
            print("🌍 Deploying a producción...")
            result = subprocess.run(['vercel', '--prod'], 
                                  capture_output=True, text=True, check=True)
            prod_url = result.stdout.strip().split('\n')[-1]
            print(f"✅ Production URL: {prod_url}")
            return prod_url
        
        return preview_url
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en deployment: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return None

def show_env_instructions():
    """Mostrar instrucciones para configurar variables de entorno"""
    print("\n" + "="*60)
    print("🔧 CONFIGURACIÓN DE VARIABLES DE ENTORNO")
    print("="*60)
    print()
    print("1. Ve a tu dashboard de Vercel: https://vercel.com/dashboard")
    print("2. Selecciona tu proyecto: gemini-ai-chatbot")
    print("3. Ve a Settings > Environment Variables")
    print("4. Agrega estas variables (usa el archivo .env.vercel como referencia):")
    print()
    
    env_vars = [
        "SECRET_KEY",
        "GOOGLE_API_KEY", 
        "FLASK_ENV=production",
        "FLASK_DEBUG=False",
        "GEMINI_MODEL=gemini-1.5-flash"
    ]
    
    for var in env_vars:
        print(f"   • {var}")
    
    print()
    print("5. Guarda y redeploy automáticamente")
    print("="*60)

def main():
    """Función principal"""
    print("🚀 DEPLOYMENT AUTOMÁTICO A VERCEL")
    print("="*50)
    
    # Verificaciones previas
    if not check_vercel_cli():
        return
    
    if not check_git_status():
        return
    
    # Verificar archivos de configuración
    config_files = ['vercel.json', '.vercelignore', '.env.vercel']
    for file in config_files:
        if not Path(file).exists():
            print(f"❌ Archivo {file} no encontrado")
            return
        else:
            print(f"✅ {file} encontrado")
    
    # Ejecutar deployment
    url = deploy_to_vercel()
    
    if url:
        print(f"\n🎉 ¡DEPLOYMENT EXITOSO!")
        print(f"🌐 URL: {url}")
        
        # Mostrar instrucciones para variables de entorno
        show_env_instructions()
        
        print(f"\n🔗 Abre tu aplicación: {url}")
    else:
        print("\n❌ Deployment falló")

if __name__ == "__main__":
    main()