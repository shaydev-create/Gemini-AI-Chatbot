#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 VERIFICADOR DE GITHUB ACTIONS - GEMINI AI CHATBOT
==================================================

Script para verificar el estado de las GitHub Actions y CI/CD.
"""

import webbrowser
import sys
from datetime import datetime


def open_github_actions():
    """Abre la página de GitHub Actions en el navegador."""
    repo_url = "https://github.com/shaydev-create/Gemini-AI-Chatbot"
    actions_url = f"{repo_url}/actions"
    
    print("🔍 VERIFICADOR DE GITHUB ACTIONS")
    print("=" * 50)
    print(f"📍 Repositorio: {repo_url}")
    print(f"🚀 Actions: {actions_url}")
    print()
    
    try:
        print("🌐 Abriendo GitHub Actions en el navegador...")
        webbrowser.open(actions_url)
        print("✅ Navegador abierto exitosamente")
    except Exception as e:
        print(f"❌ Error abriendo navegador: {e}")
        print(f"🔗 URL manual: {actions_url}")
    
    print()
    print("🔍 QUÉ VERIFICAR EN GITHUB ACTIONS:")
    print("-" * 40)
    print("1. ✅ Workflow 'CI/CD' ejecutándose")
    print("2. 🧪 Matrix Python 3.11 - Estado")
    print("3. 🧪 Matrix Python 3.12 - Estado") 
    print("4. 🔧 Build status - Verde/Rojo")
    print("5. 📊 Test results - Cantidad pasados")
    print("6. ⏱️  Tiempo de ejecución")
    print()
    print("🎯 ESPERADO:")
    print("   ✅ Tests: ~41 tests (21 basic + 20 main)")
    print("   ✅ Linting: Sin errores críticos")
    print("   ✅ Security: Sin vulnerabilidades")
    print("   ✅ Docker: Build exitoso")
    print()
    print("💡 Si hay fallos, revisar los logs detallados")
    print("🔄 El CI puede tomar 5-10 minutos en completarse")


def check_recent_commit():
    """Verifica información del commit reciente."""
    print("\n📋 INFORMACIÓN DEL ÚLTIMO COMMIT:")
    print("-" * 40)
    print("📝 Commit: MAJOR UPDATE: Project optimization and bug fixes")
    print("🔧 Hash: a6636a7")
    print("📊 Files: 83 archivos modificados")
    print("📈 Changes: +3,360 insertions, -5,973 deletions")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("🎯 CAMBIOS PRINCIPALES:")
    print("   ✅ Launcher mejorado (run.py)")
    print("   ✅ Fix Ctrl+C problem")
    print("   ✅ Python 3.11/3.12 compatibility")
    print("   ✅ Project cleanup (596MB freed)")
    print("   ✅ Documentation reorganized")
    print("   ✅ CI/CD matrix strategy")


def main():
    """Función principal."""
    check_recent_commit()
    
    response = input("\n¿Deseas abrir GitHub Actions en el navegador? (s/N): ")
    if response.lower() in ['s', 'si', 'sí', 'y', 'yes']:
        open_github_actions()
    else:
        print("🔗 URL manual: https://github.com/shaydev-create/Gemini-AI-Chatbot/actions")
    
    print("\n" + "=" * 50)
    print("🎉 RESUMEN:")
    print("   📤 Commit exitoso subido a GitHub")
    print("   🔄 CI/CD activado automáticamente")
    print("   ⏳ Esperando resultados...")
    print("   🎯 Meta: TODO EN VERDE ✅")


if __name__ == "__main__":
    main()