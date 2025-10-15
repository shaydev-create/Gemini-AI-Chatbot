#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 DIAGNÓSTICO DE APLICACIÓN NO RESPONSIVA
=========================================

Script para diagnosticar por qué la aplicación en Vercel
no está respondiendo correctamente.
"""

import requests
import time
from datetime import datetime


def test_app_functionality(url):
    """Prueba la funcionalidad específica de la aplicación."""
    print(f"🔍 PROBANDO FUNCIONALIDAD EN: {url}")
    print("-" * 50)
    
    try:
        # Test básico de conexión
        response = requests.get(url, timeout=15)
        print(f"📡 Conexión: {response.status_code}")
        print(f"⏱️  Tiempo: {response.elapsed.total_seconds():.2f}s")
        
        if response.status_code == 200:
            content = response.text
            print(f"📄 Tamaño contenido: {len(content)} caracteres")
            
            # Verificar contenido específico
            checks = {
                'HTML básico': '<html' in content.lower(),
                'Título': '<title>' in content.lower(),
                'CSS': '<style>' in content.lower() or '.css' in content.lower(),
                'JavaScript': '<script>' in content.lower() or '.js' in content.lower(),
                'Flask/Python': 'flask' in content.lower() or 'python' in content.lower(),
                'Gemini': 'gemini' in content.lower(),
                'Chatbot': 'chatbot' in content.lower() or 'chat' in content.lower(),
                'Formulario': '<form' in content.lower() or 'input' in content.lower(),
                'API Key': 'api' in content.lower() and 'key' in content.lower()
            }
            
            print(f"\n🔍 ANÁLISIS DE CONTENIDO:")
            for check, result in checks.items():
                status = "✅" if result else "❌"
                print(f"   {status} {check}")
            
            # Mostrar las primeras líneas del HTML
            print(f"\n📄 PRIMERAS LÍNEAS DEL HTML:")
            lines = content.split('\n')[:10]
            for i, line in enumerate(lines, 1):
                if line.strip():
                    print(f"   {i:2d}: {line.strip()[:80]}")
            
            return True, content, checks
            
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False, None, {}
            
    except requests.exceptions.Timeout:
        print("⏰ TIMEOUT: La aplicación no responde en 15 segundos")
        return False, None, {}
    except requests.exceptions.ConnectionError:
        print("🔌 ERROR DE CONEXIÓN: No se puede conectar")
        return False, None, {}
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False, None, {}


def check_common_issues(content, checks):
    """Verifica problemas comunes."""
    print(f"\n🚨 DIAGNÓSTICO DE PROBLEMAS:")
    print("-" * 35)
    
    issues = []
    solutions = []
    
    # Error 1: Página estática sin funcionalidad
    if checks.get('HTML básico') and not checks.get('Flask/Python'):
        issues.append("📄 La página parece ser HTML estático")
        solutions.append("🔧 Verificar que Flask esté configurado correctamente")
    
    # Error 2: Sin formulario de chat
    if not checks.get('Formulario'):
        issues.append("💬 No se detectó formulario de chat")
        solutions.append("🔧 Verificar que el HTML incluya inputs para el chat")
    
    # Error 3: Sin JavaScript
    if not checks.get('JavaScript'):
        issues.append("⚡ No se detectó JavaScript")
        solutions.append("🔧 El chat necesita JS para enviar mensajes")
    
    # Error 4: Posible problema de API Key
    if not checks.get('API Key'):
        issues.append("🔑 No se menciona configuración de API")
        solutions.append("🔧 Verificar GEMINI_API_KEY en variables de entorno")
    
    # Error 5: Contenido muy pequeño
    if content and len(content) < 1000:
        issues.append("📏 Contenido HTML muy pequeño")
        solutions.append("🔧 Posible error en el template o routing")
    
    if issues:
        print("❌ PROBLEMAS DETECTADOS:")
        for issue in issues:
            print(f"   {issue}")
        
        print(f"\n💡 SOLUCIONES SUGERIDAS:")
        for solution in solutions:
            print(f"   {solution}")
    else:
        print("✅ No se detectaron problemas obvios")
    
    return issues, solutions


def check_vercel_configuration():
    """Verifica la configuración de Vercel."""
    print(f"\n⚙️ VERIFICANDO CONFIGURACIÓN DE VERCEL:")
    print("-" * 45)
    
    # Verificar archivos de configuración
    import os
    
    config_files = [
        ('vercel.json', 'Configuración de Vercel'),
        ('requirements.txt', 'Dependencias Python'),
        ('runtime.txt', 'Versión de Python'),
        ('app.py', 'Aplicación principal'),
        ('wsgi.py', 'WSGI entry point'),
        ('Procfile', 'Proceso de inicio')
    ]
    
    print("📁 ARCHIVOS DE CONFIGURACIÓN:")
    for filename, description in config_files:
        if os.path.exists(filename):
            print(f"   ✅ {filename} - {description}")
        else:
            print(f"   ❌ {filename} - {description} (FALTANTE)")
    
    # Verificar estructura de la app
    print(f"\n📂 ESTRUCTURA DE LA APLICACIÓN:")
    app_files = [
        'app/__init__.py',
        'app/main/__init__.py', 
        'app/main/routes.py',
        'app/templates/',
        'app/static/'
    ]
    
    for filepath in app_files:
        if os.path.exists(filepath):
            print(f"   ✅ {filepath}")
        else:
            print(f"   ❌ {filepath} (FALTANTE)")


def suggest_fixes():
    """Sugiere fixes para problemas comunes."""
    print(f"\n🔧 POSIBLES SOLUCIONES:")
    print("=" * 30)
    
    print("1. 🔑 VERIFICAR API KEY:")
    print("   • Ve a Vercel Dashboard → tu proyecto → Settings")
    print("   • Environment Variables → añadir GEMINI_API_KEY")
    print("   • Valor: tu clave real de Google AI Studio")
    print()
    
    print("2. 📄 VERIFICAR ENTRY POINT:")
    print("   • Vercel debe saber qué archivo ejecutar")
    print("   • Crear vercel.json con configuración correcta")
    print("   • Verificar que app/__init__.py exporte la app")
    print()
    
    print("3. 🐍 VERIFICAR PYTHON VERSION:")
    print("   • Crear runtime.txt con: python-3.11.0")
    print("   • Verificar requirements.txt actualizado")
    print()
    
    print("4. 🌐 VERIFICAR WSGI:")
    print("   • Crear wsgi.py que importe la app Flask")
    print("   • Configurar vercel.json para usar wsgi.py")
    print()
    
    print("5. 🔄 RE-DEPLOY:")
    print("   • Hacer un commit pequeño")
    print("   • Push a GitHub para trigger re-deployment")


def main():
    """Función principal."""
    print("🔍 DIAGNÓSTICO DE APLICACIÓN NO RESPONSIVA")
    print("=" * 50)
    print()
    
    # Probar ambas URLs
    urls = [
        "https://gemini-ai-chatbot.vercel.app",
        "https://my-gemini-chatbot.vercel.app"
    ]
    
    results = {}
    
    for url in urls:
        print(f"\n{'='*60}")
        success, content, checks = test_app_functionality(url)
        results[url] = {'success': success, 'content': content, 'checks': checks}
        
        if success and content:
            issues, solutions = check_common_issues(content, checks)
            results[url]['issues'] = issues
            results[url]['solutions'] = solutions
        
        time.sleep(2)  # Pausa entre requests
    
    # Verificar configuración local
    check_vercel_configuration()
    
    # Sugerir fixes
    suggest_fixes()
    
    # Resumen final
    print(f"\n🎯 RESUMEN FINAL:")
    print("=" * 20)
    working_count = sum(1 for r in results.values() if r['success'])
    
    if working_count == 0:
        print("❌ NINGUNA URL FUNCIONA CORRECTAMENTE")
        print("🔧 ACCIÓN REQUERIDA: Revisar configuración de Vercel")
    elif working_count == len(urls):
        print("✅ TODAS LAS URLs RESPONDEN")
        print("🔍 Pero puede haber problemas de funcionalidad")
    else:
        print(f"⚠️  {working_count}/{len(urls)} URLs funcionando")
    
    # Próximos pasos
    print(f"\n📋 PRÓXIMOS PASOS RECOMENDADOS:")
    print("1. 🔧 Verificar configuración de Vercel")
    print("2. 🔑 Añadir GEMINI_API_KEY en environment variables")
    print("3. 📄 Crear vercel.json si no existe")
    print("4. 🔄 Hacer redeploy con git push")
    print("5. 🧪 Probar localmente con 'python run.py'")


if __name__ == "__main__":
    main()