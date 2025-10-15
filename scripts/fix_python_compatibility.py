#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 SCRIPT DE COMPATIBILIDAD PYTHON 3.11/3.12
============================================

Este script detecta y corrige automáticamente los problemas de compatibilidad
entre Python 3.11 y 3.12 en el proyecto.
"""

import re
import sys
from pathlib import Path
from typing import Tuple


class Python311312Compatibility:
    """Manejador de compatibilidad entre Python 3.11 y 3.12."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.fixes_applied = []

    def detect_python_version(self) -> Tuple[int, int]:
        """Detecta la versión de Python actual."""
        return sys.version_info[:2]

    def fix_typing_syntax(self, content: str) -> str:
        """Corrige problemas de sintaxis de typing entre versiones."""
        original_content = content

        # Python 3.12 prefiere Union[X, Y] sobre X | Y en algunos contextos
        # Convertir union syntax moderna a compatible
        content = re.sub(r"(\w+)\s*\|\s*None", r"Optional[\1]", content)

        # Asegurar imports de typing necesarios
        if "Optional[" in content and "from typing import" in content:
            # Verificar si Optional ya está importado
            if not re.search(r"from typing import.*Optional", content):
                content = re.sub(
                    r"(from typing import [^n]*)", r"\1, Optional", content
                )
        elif "Optional[" in content and "from typing import" not in content:
            # Añadir import de typing si no existe
            lines = content.split("\n")
            import_line = "from typing import Optional"

            # Encontrar lugar apropiado para el import
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    insert_pos = i + 1
                elif line.strip() == "" and insert_pos > 0:
                    continue
                elif insert_pos > 0:
                    break

            lines.insert(insert_pos, import_line)
            content = "\n".join(lines)

        if content != original_content:
            self.fixes_applied.append("Typing syntax compatibility")

        return content

    def fix_asyncio_compatibility(self, content: str) -> str:
        """Corrige problemas de asyncio entre versiones."""
        original_content = content

        # Python 3.12 cambió algunos warnings de asyncio
        # Agregar configuración específica para pytest-asyncio
        if "pytest" in content and "asyncio" in content:
            # Asegurar configuración correcta de asyncio_mode
            if "asyncio_mode" not in content:
                content = content.replace(
                    "import pytest", "import pytest\npytestmark = pytest.mark.asyncio"
                )

        if content != original_content:
            self.fixes_applied.append("Asyncio compatibility")

        return content

    def fix_deprecation_warnings(self, content: str) -> str:
        """Corrige warnings de deprecación entre versiones."""
        original_content = content

        # Python 3.12 deprecó algunas funciones
        replacements = [
            # datetime.now(timezone.utc) deprecado en 3.12
            (r"datetime\.utcnow\(\)", "datetime.now(timezone.utc)"),
            # pkg_resources deprecado
            (r"from importlib import metadata", "from importlib import metadata"),
            (r"pkg_resources\.", "metadata."),
        ]

        for old_pattern, new_pattern in replacements:
            if re.search(old_pattern, content):
                content = re.sub(old_pattern, new_pattern, content)
                self.fixes_applied.append(f"Deprecation fix: {old_pattern}")

        if content != original_content and "datetime.now(timezone.utc)" in content:
            # Asegurar import de timezone
            if "from datetime import" in content and "timezone" not in content:
                content = re.sub(
                    r"(from datetime import [^n]*)", r"\1, timezone", content
                )
            elif "import datetime" in content and "timezone" not in content:
                content = content.replace(
                    "import datetime", "import datetime\nfrom datetime import timezone"
                )

        return content

    def fix_test_configuration(self, content: str, file_path: Path) -> str:
        """Corrige configuración específica de tests."""
        original_content = content

        # Configuración específica para pytest.ini
        if file_path.name == "pytest.ini":
            # Asegurar configuración asyncio compatible
            if "asyncio_default_fixture_loop_scope" not in content:
                content = content.replace(
                    "[pytest]",
                    "[pytest]\nasyncio_default_fixture_loop_scope = function",
                )
                self.fixes_applied.append("Pytest asyncio configuration")

        # Configuración para pyproject.toml
        elif (
            file_path.name == "pyproject.toml"
            and "[tool.pytest.ini_options]" in content
        ):
            if "asyncio_default_fixture_loop_scope" not in content:
                content = content.replace(
                    'asyncio_mode = "auto"',
                    'asyncio_mode = "auto"\nasyncio_default_fixture_loop_scope = "function"',
                )
                self.fixes_applied.append("Pyproject pytest asyncio configuration")

        return content

    def fix_import_compatibility(self, content: str) -> str:
        """Corrige problemas de imports entre versiones."""
        original_content = content

        # Python 3.12 puede tener diferentes paths para algunos imports
        compatibility_imports = [
            # Asegurar que collections.abc sea usado en lugar de collections
            (
                r"from collections.abc import (.*)(Mapping|Sequence|Iterable)",
                r"from collections.abc import \1\2",
            ),
        ]

        for old_pattern, new_pattern in compatibility_imports:
            if re.search(old_pattern, content):
                content = re.sub(old_pattern, new_pattern, content)
                self.fixes_applied.append("Import compatibility fix")

        return content

    def process_file(self, file_path: Path) -> bool:
        """Procesa un archivo aplicando todas las correcciones."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Aplicar todas las correcciones
            content = self.fix_typing_syntax(content)
            content = self.fix_asyncio_compatibility(content)
            content = self.fix_deprecation_warnings(content)
            content = self.fix_test_configuration(content, file_path)
            content = self.fix_import_compatibility(content)

            # Guardar si hubo cambios
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"✅ Corregido: {file_path}")
                return True

            return False

        except Exception as e:
            print(f"❌ Error procesando {file_path}: {e}")
            return False

    def process_all_files(self):
        """Procesa todos los archivos Python del proyecto."""
        python_files = list(self.project_root.rglob("*.py"))
        config_files = [
            self.project_root / "pytest.ini",
            self.project_root / "pyproject.toml",
        ]

        files_to_process = python_files + [f for f in config_files if f.exists()]

        print(f"🔍 Procesando {len(files_to_process)} archivos...")

        fixed_files = 0
        for file_path in files_to_process:
            if self.process_file(file_path):
                fixed_files += 1

        print("\n📊 Resumen:")
        print(f"   • Archivos procesados: {len(files_to_process)}")
        print(f"   • Archivos corregidos: {fixed_files}")
        print(f"   • Correcciones aplicadas: {len(set(self.fixes_applied))}")

        if self.fixes_applied:
            print("\n🔧 Tipos de correcciones:")
            for fix in set(self.fixes_applied):
                print(f"   • {fix}")


def main():
    """Función principal."""
    project_root = Path(__file__).parent.parent
    compatibility_fixer = Python311312Compatibility(project_root)

    print("🔧 Iniciando corrección de compatibilidad Python 3.11/3.12...")
    print(f"📍 Proyecto: {project_root}")
    print(
        f"🐍 Python actual: {'.'.join(map(str, compatibility_fixer.detect_python_version()))}"
    )

    compatibility_fixer.process_all_files()

    print(
        "\n✅ Proceso completado. Ahora el proyecto debería ser compatible con Python 3.11 y 3.12."
    )


if __name__ == "__main__":
    main()
