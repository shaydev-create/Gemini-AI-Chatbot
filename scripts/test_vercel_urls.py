#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 VERIFICADOR DE URLs DE VERCEL
===============================

Script para probar qué URLs de Vercel están funcionando
y obtener información sobre el estado de cada deployment.
"""

import requests
import time
from datetime import datetime
import json


def test_url(url, timeout=10):
    """Testa una URL y retorna información sobre su estado."""
    try:
        print(f"🔍 Probando: {url}")
        response = requests.get(url, timeout=timeout)
        
        status_info = {
            'url': url,
            'status_code': response.status_code,
            'response_time': response.elapsed.total_seconds(),
            'accessible': response.status_code == 200,
            'headers': dict(response.headers),
            'content_length': len(response.content) if response.content else 0
        }
        
        if response.status_code == 200:
            print(f"✅ FUNCIONANDO - {response.status_code} ({response.elapsed.total_seconds():.2f}s)")
            
            # Verificar si es una app Flask/HTML válida
            content = response.text.lower()
            if 'gemini' in content or 'chatbot' in content or 'flask' in content:
                print(f"   🎯 Contenido válido detectado")
                status_info['valid_content'] = True
            else:
                print(f"   ⚠️  Contenido inesperado")
                status_info['valid_content'] = False
                
        else:
            print(f"❌ ERROR - {response.status_code}")
            status_info['accessible'] = False
            
        return status_info
        
    except requests.exceptions.Timeout:
        print(f"⏰ TIMEOUT - No responde en {timeout}s")
        return {'url': url, 'status': 'timeout', 'accessible': False}
    except requests.exceptions.ConnectionError:
        print(f"🔌 CONNECTION ERROR - URL no existe")
        return {'url': url, 'status': 'connection_error', 'accessible': False}
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return {'url': url, 'status': f'error: {e}', 'accessible': False}


def main():
    """Función principal para probar todas las URLs."""
    print("🚀 VERIFICADOR DE URLs DE VERCEL")
    print("=" * 50)
    print()
    
    # URLs de Vercel a probar
    urls = [
        "https://gemini-ai-chatbot.vercel.app",
        "https://gemini-ai-chatbot-c3jw.vercel.app", 
        "https://gemini-ai-chatbot-h3kb.vercel.app",
        "https://gemini-ai-chatbot-jf4t.vercel.app",
        "https://gemini-ai-chatbot-xvhi.vercel.app",
        "https://gemini-chatbot-2025-final.vercel.app",
        "https://my-gemini-chatbot.vercel.app"
    ]
    
    results = []
    working_urls = []
    
    for i, url in enumerate(urls, 1):
        print(f"\n{i}/{len(urls)} - ", end="")
        result = test_url(url)
        results.append(result)
        
        if result.get('accessible', False):
            working_urls.append(url)
        
        # Pausa entre requests para ser amigable
        time.sleep(1)
    
    # Resumen de resultados
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE RESULTADOS:")
    print("=" * 50)
    
    print(f"✅ URLs funcionando: {len(working_urls)}/{len(urls)}")
    print(f"❌ URLs con problemas: {len(urls) - len(working_urls)}/{len(urls)}")
    print()
    
    if working_urls:
        print("🌐 URLs FUNCIONANDO:")
        for url in working_urls:
            print(f"   ✅ {url}")
        print()
    
    # URLs con problemas
    problem_urls = [r['url'] for r in results if not r.get('accessible', False)]
    if problem_urls:
        print("❌ URLs CON PROBLEMAS:")
        for url in problem_urls:
            print(f"   ❌ {url}")
        print()
    
    # Recomendaciones
    print("💡 RECOMENDACIONES:")
    if len(working_urls) >= 1:
        print(f"✅ Tienes {len(working_urls)} deployment(s) funcionando")
        print(f"🎯 URL principal recomendada: {working_urls[0]}")
        if len(working_urls) > 2:
            print(f"🧹 Considera limpiar {len(working_urls) - 2} deployments extra")
    else:
        print("⚠️  Ninguna URL está funcionando - revisar configuración")
    
    # Guardar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reports/vercel_test_{timestamp}.json"
    
    try:
        import os
        os.makedirs('reports', exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': timestamp,
                'total_urls': len(urls),
                'working_urls': len(working_urls),
                'results': results
            }, f, indent=2, ensure_ascii=False)
        print(f"📄 Resultados guardados en: {filename}")
    except Exception as e:
        print(f"⚠️  No se pudo guardar el reporte: {e}")
    
    return working_urls


if __name__ == "__main__":
    working_urls = main()
    
    if working_urls:
        print(f"\n🎉 ¡Éxito! Tu aplicación está en línea en {len(working_urls)} URL(s)")
        print("🌐 Puedes compartir estas URLs con cualquier persona en el mundo")
    else:
        print("\n⚠️ Ninguna URL está funcionando. Revisar configuración de Vercel.")