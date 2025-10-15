#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧹 SCRIPT DE LIMPIEZA COMPLETA DEL PROYECTO
=========================================

Este script elimina todos los archivos temporales, cache, y archivos
no necesarios del proyecto para dejarlo limpio y optimizado.
"""

import shutil
import sys
from pathlib import Path


class ProjectCleaner:
    """Limpiador completo del proyecto."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.removed_files = []
        self.removed_dirs = []
        self.total_size_saved = 0

    def get_size(self, path: Path) -> int:
        """Obtiene el tamaño de un archivo o directorio."""
        try:
            if path.is_file():
                return path.stat().st_size
            elif path.is_dir():
                return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
        except (OSError, PermissionError):
            pass
        return 0

    def remove_cache_directories(self):
        """Elimina directorios de cache."""
        cache_dirs = [
            "__pycache__",
            ".pytest_cache",
            ".ruff_cache",
            ".mypy_cache",
            ".coverage",
            "htmlcov",
            ".venv",
            "venv",
            "env",
            "node_modules",
            ".tox",
            "build",
            "dist",
            "*.egg-info",
        ]

        print("🗑️  Eliminando directorios de cache...")

        for cache_pattern in cache_dirs:
            if "*" in cache_pattern:
                # Buscar patrones con wildcards
                for path in self.project_root.rglob(cache_pattern):
                    if path.is_dir():
                        size = self.get_size(path)
                        try:
                            shutil.rmtree(path)
                            self.removed_dirs.append(str(path))
                            self.total_size_saved += size
                            print(f"   ✅ Eliminado: {path}")
                        except (OSError, PermissionError) as e:
                            print(f"   ⚠️  No se pudo eliminar {path}: {e}")
            else:
                # Buscar directorios exactos
                for path in self.project_root.rglob(cache_pattern):
                    if path.is_dir() and path.name == cache_pattern:
                        size = self.get_size(path)
                        try:
                            shutil.rmtree(path)
                            self.removed_dirs.append(str(path))
                            self.total_size_saved += size
                            print(f"   ✅ Eliminado: {path}")
                        except (OSError, PermissionError) as e:
                            print(f"   ⚠️  No se pudo eliminar {path}: {e}")

    def remove_temporary_files(self):
        """Elimina archivos temporales."""
        temp_patterns = [
            "*.pyc",
            "*.pyo",
            "*.pyd",
            "*.so",
            "*.egg",
            "*.tmp",
            "*.temp",
            "*.log",
            "*.bak",
            "*.swp",
            "*.swo",
            "*~",
            ".DS_Store",
            "Thumbs.db",
            "desktop.ini",
            "*.coverage",
            ".coverage.*",
            "coverage.xml",
            "*.prof",
            "*.lprof",
        ]

        print("\n🗑️  Eliminando archivos temporales...")

        for pattern in temp_patterns:
            for path in self.project_root.rglob(pattern):
                if path.is_file():
                    size = self.get_size(path)
                    try:
                        path.unlink()
                        self.removed_files.append(str(path))
                        self.total_size_saved += size
                        print(f"   ✅ Eliminado: {path}")
                    except (OSError, PermissionError) as e:
                        print(f"   ⚠️  No se pudo eliminar {path}: {e}")

    def remove_ide_files(self):
        """Elimina archivos de IDEs y editores."""
        ide_patterns = [
            ".vscode/settings.json",
            ".idea",
            "*.sublime-*",
            ".atom",
            ".eclipse",
            ".project",
            ".pydevproject",
        ]

        print("\n🗑️  Eliminando archivos de IDEs innecesarios...")

        for pattern in ide_patterns:
            if "*" in pattern:
                for path in self.project_root.rglob(pattern):
                    size = self.get_size(path)
                    try:
                        if path.is_file():
                            path.unlink()
                            self.removed_files.append(str(path))
                        elif path.is_dir():
                            shutil.rmtree(path)
                            self.removed_dirs.append(str(path))
                        self.total_size_saved += size
                        print(f"   ✅ Eliminado: {path}")
                    except (OSError, PermissionError) as e:
                        print(f"   ⚠️  No se pudo eliminar {path}: {e}")
            else:
                path = self.project_root / pattern
                if path.exists():
                    size = self.get_size(path)
                    try:
                        if path.is_file():
                            path.unlink()
                            self.removed_files.append(str(path))
                        elif path.is_dir():
                            shutil.rmtree(path)
                            self.removed_dirs.append(str(path))
                        self.total_size_saved += size
                        print(f"   ✅ Eliminado: {path}")
                    except (OSError, PermissionError) as e:
                        print(f"   ⚠️  No se pudo eliminar {path}: {e}")

    def remove_duplicate_files(self):
        """Elimina archivos duplicados comunes."""
        duplicates = [
            # Archivos de backup automático
            "*.orig",
            "*.rej",
            "*_backup*",
            "*_old*",
            "*_copy*",
            # Archivos de git temporales
            "*.patch",
            "*.diff",
        ]

        print("\n🗑️  Eliminando archivos duplicados y backups...")

        for pattern in duplicates:
            for path in self.project_root.rglob(pattern):
                if path.is_file():
                    size = self.get_size(path)
                    try:
                        path.unlink()
                        self.removed_files.append(str(path))
                        self.total_size_saved += size
                        print(f"   ✅ Eliminado: {path}")
                    except (OSError, PermissionError) as e:
                        print(f"   ⚠️  No se pudo eliminar {path}: {e}")

    def remove_test_artifacts(self):
        """Elimina artefactos de testing."""
        test_artifacts = [
            "reports/*.html",
            "reports/*.json",
            "reports/*.xml",
            ".pytest_cache",
            "test-results",
            "test_results",
            "junit.xml",
            "test-output",
        ]

        print("\n🗑️  Eliminando artefactos de testing...")

        for pattern in test_artifacts:
            for path in self.project_root.rglob(pattern):
                if path.is_file():
                    size = self.get_size(path)
                    try:
                        path.unlink()
                        self.removed_files.append(str(path))
                        self.total_size_saved += size
                        print(f"   ✅ Eliminado: {path}")
                    except (OSError, PermissionError) as e:
                        print(f"   ⚠️  No se pudo eliminar {path}: {e}")
                elif path.is_dir():
                    size = self.get_size(path)
                    try:
                        shutil.rmtree(path)
                        self.removed_dirs.append(str(path))
                        self.total_size_saved += size
                        print(f"   ✅ Eliminado: {path}")
                    except (OSError, PermissionError) as e:
                        print(f"   ⚠️  No se pudo eliminar {path}: {e}")

    def clean_empty_directories(self):
        """Elimina directorios vacíos."""
        print("\n🗑️  Eliminando directorios vacíos...")

        # Iterar desde los directorios más profundos hacia arriba
        for path in sorted(
            self.project_root.rglob("*"), key=lambda p: len(p.parts), reverse=True
        ):
            if path.is_dir() and path != self.project_root:
                try:
                    # Verificar si está vacío
                    if not any(path.iterdir()):
                        path.rmdir()
                        self.removed_dirs.append(str(path))
                        print(f"   ✅ Eliminado directorio vacío: {path}")
                except (OSError, PermissionError):
                    # No pasa nada si no se puede eliminar
                    pass

    def format_size(self, size_bytes: int) -> str:
        """Formatea el tamaño en bytes a una representación legible."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def clean_all(self):
        """Ejecuta todas las operaciones de limpieza."""
        print("🧹 INICIANDO LIMPIEZA COMPLETA DEL PROYECTO")
        print("=" * 50)

        self.remove_cache_directories()
        self.remove_temporary_files()
        self.remove_ide_files()
        self.remove_duplicate_files()
        self.remove_test_artifacts()
        self.clean_empty_directories()

        # Resumen final
        print("\n" + "=" * 50)
        print("📊 RESUMEN DE LIMPIEZA:")
        print(f"   🗂️  Archivos eliminados: {len(self.removed_files)}")
        print(f"   📁 Directorios eliminados: {len(self.removed_dirs)}")
        print(f"   💾 Espacio liberado: {self.format_size(self.total_size_saved)}")

        if self.removed_files or self.removed_dirs:
            print("\n✅ ¡Proyecto limpiado exitosamente!")
        else:
            print("\n✨ ¡El proyecto ya estaba limpio!")

        return len(self.removed_files) + len(self.removed_dirs)


def main():
    """Función principal."""
    project_root = Path(__file__).parent.parent

    print(f"📍 Proyecto: {project_root}")
    print(f"🐍 Python: {sys.version.split()[0]}")

    # Confirmar antes de proceder
    response = input("\n¿Deseas continuar con la limpieza completa? (s/N): ")
    if response.lower() not in ["s", "si", "sí", "y", "yes"]:
        print("❌ Limpieza cancelada.")
        return

    cleaner = ProjectCleaner(project_root)
    items_removed = cleaner.clean_all()

    if items_removed > 0:
        print(f"\n🎉 Limpieza completada. {items_removed} elementos eliminados.")
    else:
        print("\n✨ No había nada que limpiar.")


if __name__ == "__main__":
    main()
