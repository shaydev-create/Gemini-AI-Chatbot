#!/usr/bin/env python3
"""
Script para formatear el código usando ruff.
Este script proporciona un punto de entrada de función para el CI/CD.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """
    Función principal para formatear el código con ruff.
    """
    try:
        # Obtener el directorio raíz del proyecto
        project_root = Path(__file__).parent.parent
        
        # Ejecutar ruff format
        result = subprocess.run(
            ["poetry", "run", "ruff", "format", "--check", "."],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        # Mostrar la salida
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        # Salir con el código de retorno de ruff
        sys.exit(result.returncode)
        
    except FileNotFoundError:
        print("Error: No se pudo encontrar poetry o ruff. Asegúrate de que estén instalados.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()