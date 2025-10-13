#!/usr/bin/env python3
"""
Módulo para ejecutar tests usando pytest.
Proporciona una función main() para el punto de entrada del script.
"""

import subprocess
import sys


def main():
    """
    Función principal para ejecutar tests con pytest.
    Esta función es requerida por el formato de script module:function.
    """
    try:
        # Ejecutar pytest con los argumentos por defecto
        result = subprocess.run(
            ["pytest"],
            capture_output=False,  # Permitir que pytest muestre su salida directamente
            text=True
        )
        
        # Salir con el código de retorno de pytest
        return result.returncode
        
    except FileNotFoundError:
        print("Error: No se pudo encontrar pytest. Asegúrate de que esté instalado.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error inesperado: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())