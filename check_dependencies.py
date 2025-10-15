#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 VERIFICADOR DE DEPENDENCIAS - GEMINI AI CHATBOT
=================================================

Script para diagnosticar problemas con las dependencias
y verificar que todo esté correctamente instalado.
"""

import sys
import importlib
from typing import Dict, List, Tuple


def check_import(module_name: str, description: str = "") -> Tuple[bool, str]:
    """Verifica si un módulo se puede importar correctamente."""
    try:
        module = importlib.import_module(module_name)
        version = getattr(module, '__version__', 'desconocida')
        return True, version
    except ImportError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Error: {e}"


def main():
    """Función principal de verificación."""
    print("🔍 VERIFICADOR DE DEPENDENCIAS - GEMINI AI CHATBOT")
    print("=" * 60)
    print(f"🐍 Python: {sys.version}")
    print(f"📁 Ejecutable: {sys.executable}")
    print()
    
    # Lista de dependencias críticas
    critical_deps = [
        ("flask", "Framework web principal"),
        ("flask_socketio", "WebSockets para tiempo real"),
        ("sqlalchemy", "ORM para base de datos"),
        ("google.generativeai", "API de Gemini AI"),
        ("dotenv", "Variables de entorno"),
        ("werkzeug", "Servidor WSGI"),
    ]
    
    # Lista de dependencias opcionales
    optional_deps = [
        ("redis", "Cache Redis"),
        ("celery", "Tareas asíncronas"),
        ("gunicorn", "Servidor de producción"),
        ("pytest", "Testing"),
        ("ruff", "Linting y formateo"),
    ]
    
    # Lista de dependencias problemáticas conocidas
    problematic_deps = [
        ("IPython", "Jupyter/IPython"),
        ("astroid", "Análisis estático"),
        ("stack_data", "Depuración"),
        ("asttokens", "Tokens AST"),
    ]
    
    print("🔧 DEPENDENCIAS CRÍTICAS:")
    print("-" * 30)
    critical_issues = 0
    for module, desc in critical_deps:
        success, version = check_import(module)
        status = "✅" if success else "❌"
        print(f"{status} {module:<20} | {desc}")
        if success:
            print(f"    └─ Versión: {version}")
        else:
            print(f"    └─ Error: {version}")
            critical_issues += 1
        print()
    
    print("🔧 DEPENDENCIAS OPCIONALES:")
    print("-" * 30)
    for module, desc in optional_deps:
        success, version = check_import(module)
        status = "✅" if success else "⚠️ "
        print(f"{status} {module:<20} | {desc}")
        if success:
            print(f"    └─ Versión: {version}")
        print()
    
    print("⚠️  DEPENDENCIAS PROBLEMÁTICAS:")
    print("-" * 30)
    problematic_count = 0
    for module, desc in problematic_deps:
        success, version = check_import(module)
        if success:
            print(f"🟡 {module:<20} | {desc} (presente)")
            print(f"    └─ Versión: {version}")
            problematic_count += 1
        else:
            print(f"✅ {module:<20} | {desc} (ausente - BUENO)")
        print()
    
    # Verificar imports específicos del proyecto
    print("🏗️  MÓDULOS DEL PROYECTO:")
    print("-" * 30)
    
    project_modules = [
        ("app", "Módulo principal"),
        ("app.core.application", "Factory de aplicación"),
        ("app.services.gemini_service", "Servicio Gemini"),
    ]
    
    project_issues = 0
    for module, desc in project_modules:
        success, info = check_import(module)
        status = "✅" if success else "❌"
        print(f"{status} {module:<25} | {desc}")
        if not success:
            print(f"    └─ Error: {info}")
            project_issues += 1
        print()
    
    # Resumen final
    print("=" * 60)
    print("📊 RESUMEN:")
    print(f"   🔴 Dependencias críticas con problemas: {critical_issues}")
    print(f"   🟡 Dependencias problemáticas presentes: {problematic_count}")
    print(f"   ❌ Módulos del proyecto con problemas: {project_issues}")
    
    # Diagnóstico y recomendaciones
    if critical_issues > 0:
        print("\n❌ PROBLEMAS CRÍTICOS DETECTADOS:")
        print("   💡 Ejecutar: pip install -r requirements.txt")
        
    if problematic_count > 0:
        print("\n⚠️  DEPENDENCIAS PROBLEMÁTICAS DETECTADAS:")
        print("   💡 Estas pueden causar conflictos durante el shutdown")
        print("   💡 Considera usar: pip uninstall IPython astroid")
        
    if project_issues > 0:
        print("\n🔧 PROBLEMAS EN MÓDULOS DEL PROYECTO:")
        print("   💡 Verificar estructura de archivos")
        print("   💡 Verificar variables de entorno (.env)")
        
    if critical_issues == 0 and project_issues == 0:
        print("\n✅ DIAGNÓSTICO: El proyecto debería funcionar correctamente")
        print("   💡 Si hay problemas al cerrar con Ctrl+C, es normal")
        print("   💡 Usar el nuevo launcher: python launch_app.py")
    
    return critical_issues + project_issues


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)