#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧹 MANTENIMIENTO DIARIO - GEMINI AI CHATBOT
==========================================

Script para ejecutar mantenimiento diario del proyecto:
limpieza, formateo, testing básico y verificaciones.
"""

import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple


def run_command_with_timeout(command: List[str], description: str, timeout: int = 300) -> Tuple[bool, str]:
    """Ejecuta un comando con timeout."""
    try:
        print(f"🔄 {description}...")
        start_time = time.time()

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,  # No lanzar excepción en error
        )

        elapsed = time.time() - start_time

        if result.returncode == 0:
            print(f"   ✅ {description} completado ({elapsed:.1f}s)")
            return True, result.stdout
        else:
            print(f"   ⚠️  {description} terminó con código {result.returncode} ({elapsed:.1f}s)")
            return False, result.stderr

    except subprocess.TimeoutExpired:
        print(f"   ⏰ {description} cancelado por timeout ({timeout}s)")
        return False, f"Timeout después de {timeout}s"
    except Exception as e:
        print(f"   ❌ Error en {description}: {e}")
        return False, str(e)


def check_project_health() -> dict:
    """Verifica la salud general del proyecto."""
    project_root = Path(__file__).parent.parent

    health_status = {
        "files_count": 0,
        "project_size_mb": 0,
        "python_files": 0,
        "test_files": 0,
    }

    try:
        # Contar archivos
        all_files = list(project_root.rglob("*"))
        health_status["files_count"] = len([f for f in all_files if f.is_file()])

        # Calcular tamaño
        total_size = sum(f.stat().st_size for f in all_files if f.is_file())
        health_status["project_size_mb"] = round(total_size / 1024 / 1024, 2)

        # Contar archivos Python
        health_status["python_files"] = len(list(project_root.rglob("*.py")))

        # Contar archivos de test
        health_status["test_files"] = len(list(project_root.rglob("test_*.py")))

    except Exception as e:
        print(f"⚠️  Error verificando salud del proyecto: {e}")

    return health_status


def main():
    """Función principal de mantenimiento diario."""
    print("🌅 MANTENIMIENTO DIARIO - GEMINI AI CHATBOT")
    print("=" * 50)
    print(f"📅 Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Verificar salud inicial
    initial_health = check_project_health()
    print(f"📊 Estado inicial: {initial_health['files_count']} archivos, {initial_health['project_size_mb']} MB")

    project_root = Path(__file__).parent.parent
    os_command = "python" if sys.platform == "win32" else "python3"

    # Tareas de mantenimiento diario (más rápidas)
    daily_tasks = [
        # 1. Limpieza rápida
        (
            [os_command, "scripts/clean_project.py"],
            "Limpieza de cache y temporales",
            60,
        ),
        # 2. Formateo de código
        ([os_command, "-m", "ruff", "format", "."], "Formateo de código", 30),
        # 3. Corrección básica de linting
        (
            [os_command, "-m", "ruff", "check", ".", "--fix"],
            "Corrección de linting",
            45,
        ),
        # 4. Verificación rápida de imports
        (
            [os_command, "-c", "import app; print('✅ Imports principales OK')"],
            "Verificación de imports",
            15,
        ),
        # 5. Test básico de sintaxis
        (
            [os_command, "-m", "py_compile", "app/__init__.py"],
            "Verificación de sintaxis",
            10,
        ),
    ]

    results = []
    successful_tasks = 0

    # Cambiar al directorio del proyecto
    import os

    original_cwd = Path.cwd()
    try:
        os.chdir(project_root)

        # Ejecutar tareas diarias
        for command, description, timeout in daily_tasks:
            success, output = run_command_with_timeout(command, description, timeout)
            results.append((description, success, output))
            if success:
                successful_tasks += 1

    finally:
        os.chdir(original_cwd)

    # Verificar salud final
    final_health = check_project_health()
    space_saved = initial_health["project_size_mb"] - final_health["project_size_mb"]

    # Resumen final
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE MANTENIMIENTO DIARIO:")
    print(f"   ✅ Tareas completadas: {successful_tasks}/{len(daily_tasks)}")
    print(f"   📈 Tasa de éxito: {(successful_tasks / len(daily_tasks) * 100):.1f}%")
    print(f"   🗂️  Archivos finales: {final_health['files_count']}")
    print(f"   💾 Tamaño final: {final_health['project_size_mb']} MB")

    if space_saved > 0:
        print(f"   🧹 Espacio liberado: {space_saved:.2f} MB")

    # Mostrar problemas encontrados
    failed_tasks = [(desc, output) for desc, success, output in results if not success]
    if failed_tasks:
        print(f"\n⚠️  PROBLEMAS DETECTADOS ({len(failed_tasks)}):")
        for desc, output in failed_tasks[:3]:  # Solo mostrar los primeros 3
            print(f"   • {desc}")

    # Estado final y recomendaciones
    if successful_tasks == len(daily_tasks):
        print("\n🎉 ¡MANTENIMIENTO DIARIO COMPLETADO!")
        print("💡 Proyecto en estado óptimo.")
    elif successful_tasks >= len(daily_tasks) * 0.8:
        print("\n✅ Mantenimiento diario completado con advertencias menores.")
        print("💡 Considerar ejecutar mantenimiento completo pronto.")
    else:
        print("\n⚠️  Mantenimiento diario completado con problemas.")
        print("💡 Se recomienda ejecutar mantenimiento completo AHORA.")

    return 0 if successful_tasks >= len(daily_tasks) * 0.8 else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Mantenimiento cancelado por usuario.")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Error inesperado durante mantenimiento: {e}")
        sys.exit(1)
