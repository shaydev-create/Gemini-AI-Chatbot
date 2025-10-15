#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 INVESTIGADOR DE VERCEL DEPLOYMENTS
===================================

Script para entender qué son los 7 despliegues de Vercel
y cómo acceder a ellos.
"""

import webbrowser
import sys


def explain_vercel():
    """Explica qué es Vercel y por qué aparecen 7 despliegues."""
    print("🚀 VERCEL DEPLOYMENTS EXPLICADO")
    print("=" * 50)
    print()
    
    print("📖 ¿QUÉ ES VERCEL?")
    print("-" * 30)
    print("🌐 Plataforma de hosting automático")
    print("⚡ Despliegue instantáneo desde GitHub")
    print("🔄 CI/CD integrado")
    print("🌍 CDN global automático")
    print("📱 Optimizado para aplicaciones web")
    print()
    
    print("🔍 TUS 7 DESPLIEGUES:")
    print("-" * 30)
    deployments = [
        ("gemini-ai-chatbot", "Versión principal del proyecto"),
        ("gemini-ai-chatbot-c3jw", "Versión con hash único (branch/commit específico)"),
        ("gemini-ai-chatbot-h3kb", "Versión con hash único (branch/commit específico)"),
        ("gemini-ai-chatbot-jf4t", "Versión con hash único (branch/commit específico)"),
        ("gemini-ai-chatbot-xvhi", "Versión con hash único (branch/commit específico)"),
        ("gemini-chatbot-2025-final", "Versión nombrada específicamente"),
        ("my-gemini-chatbot", "Versión personalizada")
    ]
    
    for i, (name, description) in enumerate(deployments, 1):
        print(f"{i}. 🌐 {name}")
        print(f"   └─ {description}")
        print(f"   🔗 Probable URL: https://{name}.vercel.app")
        print()


def generate_urls():
    """Genera las URLs probables de Vercel."""
    print("🔗 URLS PROBABLES DE TUS DESPLIEGUES:")
    print("-" * 50)
    
    deployments = [
        "gemini-ai-chatbot",
        "gemini-ai-chatbot-c3jw", 
        "gemini-ai-chatbot-h3kb",
        "gemini-ai-chatbot-jf4t",
        "gemini-ai-chatbot-xvhi",
        "gemini-chatbot-2025-final",
        "my-gemini-chatbot"
    ]
    
    urls = []
    for deployment in deployments:
        url = f"https://{deployment}.vercel.app"
        urls.append(url)
        print(f"🌐 {url}")
    print()
    
    return urls


def check_vercel_dashboard():
    """Información sobre cómo acceder al dashboard de Vercel."""
    print("📊 CÓMO VERIFICAR EN VERCEL:")
    print("-" * 40)
    print("1. 🌐 Ve a: https://vercel.com/dashboard")
    print("2. 🔑 Inicia sesión (si tienes cuenta)")
    print("3. 📂 Busca 'gemini' en tus proyectos")
    print("4. 🔍 Revisa cada deployment")
    print("5. ⚙️  Ve settings y configuraciones")
    print()
    
    print("❓ SI NO TIENES CUENTA DE VERCEL:")
    print("   • Los despliegues pueden ser automáticos")
    print("   • GitHub puede haber conectado automáticamente")
    print("   • Vercel detecta repositórios públicos populares")
    print("   • Algunos pueden ser de colaboradores/forks")


def possible_reasons():
    """Explica por qué hay 7 versiones."""
    print("🤔 ¿POR QUÉ 7 VERSIONES?")
    print("-" * 35)
    print("1. 🔄 Múltiples importaciones del repo")
    print("2. 🌿 Diferentes branches/ramas")
    print("3. 👥 Colaboradores que importaron el proyecto")
    print("4. 🧪 Versiones de prueba/experimentación")
    print("5. 📝 Diferentes configuraciones de deployment")
    print("6. 🔀 Forks del repositorio")
    print("7. 🤖 Auto-deployment por popularidad del repo")


def recommendations():
    """Recomendaciones sobre qué hacer."""
    print("\n💡 RECOMENDACIONES:")
    print("-" * 25)
    print("✅ MANTENER:")
    print("   • gemini-ai-chatbot (principal)")
    print("   • my-gemini-chatbot (personalizada)")
    print()
    print("🔍 INVESTIGAR:")
    print("   • Las versiones con hash (c3jw, h3kb, etc.)")
    print("   • gemini-chatbot-2025-final")
    print()
    print("🧹 POSIBLE LIMPIEZA:")
    print("   • Eliminar versiones duplicadas")
    print("   • Mantener solo 1-2 versiones activas")
    print("   • Configurar la principal como producción")


def main():
    """Función principal."""
    explain_vercel()
    urls = generate_urls()
    check_vercel_dashboard()
    possible_reasons()
    recommendations()
    
    print("\n" + "=" * 50)
    response = input("¿Deseas abrir la primera URL en el navegador? (s/N): ")
    if response.lower() in ['s', 'si', 'sí', 'y', 'yes']:
        try:
            import webbrowser
            webbrowser.open(urls[0])
            print(f"🌐 Abriendo: {urls[0]}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n🎯 PRÓXIMOS PASOS:")
    print("1. 🔍 Verificar qué URLs funcionan")
    print("2. 🌐 Probar la aplicación en línea")
    print("3. 📊 Revisar dashboard de Vercel (si tienes acceso)")
    print("4. 🧹 Limpiar versiones innecesarias")


if __name__ == "__main__":
    main()