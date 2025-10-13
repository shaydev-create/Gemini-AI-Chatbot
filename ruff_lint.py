#!/usr/bin/env python3
"""
Módulo de linting de código usando ruff.
Proporciona una función main() para el punto de entrada del script.
"""

import subprocess
import sys


def main():
    """
    Función principal para hacer linting del código con ruff.
    Esta función es requerida por el formato de script module:function.
    """
    try:
        # Ejecutar ruff check
        # Forward any CLI args (e.g., --fix, --unsafe-fixes)
        result = subprocess.run(
            ["ruff", "check", "."] + sys.argv[1:], capture_output=True, text=True
        )

        # Mostrar la salida
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        # Salir con el código de retorno de ruff
        return result.returncode

    except FileNotFoundError:
        print(
            "Error: No se pudo encontrar ruff. Asegúrate de que esté instalado.",
            file=sys.stderr,
        )
        return 1
    except Exception as e:
        print(f"Error inesperado: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
