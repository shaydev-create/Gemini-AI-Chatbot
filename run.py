#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 GEMINI AI CHATBOT - LAUNCHER PRINCIPAL
========================================

Script principal simplificado que llama al launcher mejorado.
Este es el comando más fácil de recordar para iniciar la aplicación.

USO:
    python run.py
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Ejecuta el launcher mejorado."""
    print("🚀 GEMINI AI CHATBOT")
    print("Iniciando con launcher mejorado...")
    print()

    # Ejecutar el launcher mejorado
    launcher_path = Path(__file__).parent / "launch_app.py"

    try:
        # Ejecutar el launcher mejorado directamente
        subprocess.run([sys.executable, str(launcher_path)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar el launcher: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Aplicación detenida por el usuario")
        sys.exit(0)


if __name__ == "__main__":
    main()
