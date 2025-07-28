#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧹 LIMPIEZA DE ENTORNOS DE GITHUB - GEMINI AI CHATBOT

Este script genera una guía para limpiar entornos duplicados en GitHub.
Identifica y sugiere la eliminación de entornos redundantes basándose en patrones comunes.
"""

import os
import sys
from pathlib import Path
import json
import argparse

# Constantes
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# Entornos a mantener (principales)
KEEP_ENVIRONMENTS = [
    "Producción - gemini-chatbot-2025-final",
    "Producción - gemini-ai-chatbot"
]

# Patrones de entornos duplicados o de prueba
DUPLICATE_PATTERNS = [
    "Producción - gemini-ai-chatbot-c",
    "Producción - gemini-ai-chatbot-j",
    "Producción - gemini-ai-chatbot-h",
    "Producción - gemini-ai-chatbot-x",
    "Producción - my-gemini-chatbot",
    "Producción - gemini-chatbot-2025"
]

def print_banner():
    """Mostrar banner del script"""
    print("🧹 LIMPIEZA DE ENTORNOS DE GITHUB - GEMINI AI CHATBOT")
    print("=" * 60)
    print()

def generate_cleanup_guide():
    """Generar guía para limpiar entornos de GitHub"""
    print("📋 GUÍA PARA LIMPIAR ENTORNOS DE GITHUB")
    print()
    
    print("Entornos a MANTENER:")
    for env in KEEP_ENVIRONMENTS:
        print(f"  ✅ {env}")
    print()
    
    print("Entornos a ELIMINAR:")
    for env in DUPLICATE_PATTERNS:
        print(f"  ❌ {env}")
    print()
    
    print("Pasos para eliminar entornos en GitHub:")
    print("  1. Accede a tu repositorio en GitHub")
    print("  2. Ve a 'Settings' > 'Environments'")
    print("  3. Para cada entorno que desees eliminar:")
    print("     a. Haz clic en el entorno")
    print("     b. Desplázate hasta la parte inferior")
    print("     c. Haz clic en 'Delete environment'")
    print("     d. Confirma la eliminación")
    print()
    
    print("Consideraciones importantes:")
    print("  - Asegúrate de NO eliminar los entornos principales")
    print("  - Verifica que no haya workflows activos usando los entornos antes de eliminarlos")
    print("  - Considera hacer una copia de seguridad de las variables de entorno si son importantes")
    print()

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Limpieza de entornos de GitHub")
    args = parser.parse_args()
    
    print_banner()
    generate_cleanup_guide()
    
    print("✅ Guía de limpieza generada correctamente")

if __name__ == "__main__":
    main()