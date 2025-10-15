#!/usr/bin/env python3
"""
Script optimizado para ejecutar tests de manera eficiente.
Diseñado para reducir el tiempo de ejecución en CI/CD.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description=""):
    """Ejecuta un comando y maneja errores."""
    print(f"🔄 {description}")
    print(f"Ejecutando: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True, cwd=Path(__file__).parent
        )
        print(f"✅ {description} - Completado")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Error")
        print(f"Código de salida: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Ejecutar tests optimizados")
    parser.add_argument(
        "--fast", action="store_true", help="Ejecutar solo tests rápidos"
    )
    parser.add_argument(
        "--unit", action="store_true", help="Ejecutar solo tests unitarios"
    )
    parser.add_argument(
        "--integration", action="store_true", help="Ejecutar solo tests de integración"
    )
    parser.add_argument(
        "--coverage", action="store_true", help="Generar reporte de cobertura"
    )
    parser.add_argument(
        "--parallel", action="store_true", help="Ejecutar tests en paralelo"
    )
    parser.add_argument(
        "--maxfail", type=int, default=3, help="Máximo número de fallos antes de parar"
    )

    args = parser.parse_args()

    # Configurar variables de entorno
    os.environ["APP_ENV"] = "testing"
    os.environ["PYTHONPATH"] = str(Path(__file__).parent)

    # Construir comando pytest
    cmd = ["poetry", "run", "pytest"]

    # Configurar marcadores
    markers = []
    if args.fast:
        markers.append("not slow")
    if args.unit:
        markers.append("unit")
    if args.integration:
        markers.append("integration")

    if markers:
        cmd.extend(["-m", " and ".join(markers)])

    # Configurar opciones
    cmd.extend(
        [
            f"--maxfail={args.maxfail}",
            "-x",  # Parar en el primer fallo
            "--tb=short",  # Traceback corto
            "--disable-warnings",  # Deshabilitar warnings
            "-q",  # Modo silencioso
        ]
    )

    if args.parallel:
        cmd.extend(["-n", "auto"])  # Requiere pytest-xdist

    if args.coverage:
        cmd.extend(
            [
                "--cov=app",
                "--cov-report=term-missing:skip-covered",
                "--cov-report=xml",
            ]
        )

    # Ejecutar tests
    result = run_command(cmd, "Ejecutando tests")

    if result is None:
        print("❌ Los tests fallaron")
        sys.exit(1)
    else:
        print("✅ Todos los tests pasaron")
        sys.exit(0)


if __name__ == "__main__":
    main()
