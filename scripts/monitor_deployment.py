#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 MONITOR DE RE-DEPLOYMENT
==========================

Script para monitorear el re-deployment en Vercel después
de los cambios de configuración.
"""

import requests
import time
from datetime import datetime


def test_deployment_progress(url, max_attempts=20):
    """Monitorea el progreso del deployment."""
    print(f"🔄 MONITOREANDO RE-DEPLOYMENT EN: {url}")
    print("=" * 60)
    print()
    
    for attempt in range(1, max_attempts + 1):
        print(f"📡 Intento {attempt}/{max_attempts} - {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                content = response.text
                
                # Verificar si ahora es una aplicación Flask
                flask_indicators = [
                    'flask' in content.lower(),
                    'gemini' in content.lower() and 'api' in content.lower(),
                    'form' in content.lower() and 'action' in content.lower(),
                    len(content) > 2000,  # Flask apps suelen ser más grandes
                    'csrf' in content.lower(),
                    'jinja' in content.lower() or '{{' in content
                ]
                
                flask_score = sum(flask_indicators)
                
                print(f"   📊 Status: {response.status_code}")
                print(f"   📄 Tamaño: {len(content)} caracteres")
                print(f"   🐍 Flask Score: {flask_score}/6")
                
                if flask_score >= 3:
                    print(f"   ✅ PARECE SER FLASK APP!")
                    
                    # Verificar contenido específico
                    if 'chatbot' in content.lower() and 'gemini' in content.lower():
                        print(f"   🎉 DEPLOYMENT EXITOSO!")
                        print(f"   🌐 Tu aplicación Flask está funcionando!")
                        return True
                    else:
                        print(f"   🔄 Flask detectado pero aún desplegando...")
                else:
                    print(f"   ⏳ Aún sirviendo contenido estático...")
                    
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout - el servidor puede estar reiniciando")
        except requests.exceptions.ConnectionError:
            print(f"   🔌 Error de conexión - posible rebuild en progreso")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        if attempt < max_attempts:
            print(f"   ⏳ Esperando 10 segundos...")
            time.sleep(10)
        print()
    
    print(f"❌ No se detectó deployment de Flask después de {max_attempts} intentos")
    return False


def check_both_urls():
    """Verifica ambas URLs."""
    urls = [
        "https://gemini-ai-chatbot.vercel.app",
        "https://my-gemini-chatbot.vercel.app"
    ]
    
    results = {}
    
    for url in urls:
        print(f"\n{'='*70}")
        success = test_deployment_progress(url, max_attempts=10)
        results[url] = success
        
        if success:
            print(f"🎉 {url} - DEPLOYMENT EXITOSO!")
        else:
            print(f"⚠️  {url} - Aún en proceso o con problemas")
    
    return results


def main():
    """Función principal."""
    print("🔄 MONITOR DE RE-DEPLOYMENT DE VERCEL")
    print("=" * 45)
    print("🕒 Iniciado:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print()
    print("💡 CAMBIOS ENVIADOS:")
    print("   ✅ vercel.json - Configuración de Flask")
    print("   ✅ requirements.txt - Dependencias Python")
    print("   ✅ runtime.txt - Versión Python 3.11")
    print("   ✅ app/__init__.py - Entry point Flask")
    print()
    print("⏳ Esperando que Vercel detecte y redespliegue...")
    print("📝 Esto puede tomar 1-3 minutos")
    print()
    
    results = check_both_urls()
    
    # Resumen final
    print(f"\n{'🎯'*30}")
    print("📊 RESUMEN FINAL:")
    print(f"{'🎯'*30}")
    
    success_count = sum(results.values())
    
    if success_count == 2:
        print("🎉 ¡AMBAS URLs FUNCIONANDO CON FLASK!")
        print("✅ Re-deployment completamente exitoso")
        print("🚀 Tu aplicación ahora está funcionando correctamente")
    elif success_count == 1:
        print("⚠️  1 URL funcionando, la otra aún en proceso")
        print("💡 Puede necesitar más tiempo o configuración adicional")
    else:
        print("❌ Ninguna URL funcionando aún")
        print("💡 Posibles acciones:")
        print("   1. 🔑 Añadir GEMINI_API_KEY en Vercel Dashboard")
        print("   2. 🔄 Esperar más tiempo (deployments pueden tomar hasta 5 min)")
        print("   3. 📊 Verificar logs en Vercel Dashboard")
    
    print(f"\n🌐 PRÓXIMOS PASOS:")
    print("1. 🔑 Configurar GEMINI_API_KEY en Vercel")
    print("2. 🧪 Probar la funcionalidad del chatbot")
    print("3. 🎊 ¡Disfrutar tu app funcionando!")


if __name__ == "__main__":
    main()