#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📚 ORGANIZADOR DE DOCUMENTACIÓN - GEMINI AI CHATBOT
=================================================

Script para limpiar, organizar y actualizar la documentación del proyecto.
Elimina archivos obsoletos y mantiene solo lo esencial y actualizado.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


class DocumentationOrganizer:
    """Organizador inteligente de documentación."""
    
    def __init__(self, docs_path: Path):
        self.docs_path = docs_path
        self.backup_path = docs_path / "archive"
        self.essential_docs = []
        self.obsolete_docs = []
        self.keep_docs = []
        
    def analyze_documents(self) -> Dict[str, List[str]]:
        """Analiza y categoriza todos los documentos."""
        
        # DOCUMENTOS ESENCIALES - MANTENER
        essential = [
            "README.md",              # Documentación principal
            "USER_GUIDE.md",          # Guía de usuario
            "PROJECT_STRUCTURE.md",   # Estructura del proyecto
            "FINAL_SOLUTION.md",      # Solución final actualizada
            "CTRL_C_SOLUTION.md",     # Solución del problema Ctrl+C
            "CLEANUP_SUMMARY.md",     # Resumen de limpieza
            "SCRIPT_COMPARISON.md",   # Comparación de scripts
        ]
        
        # DOCUMENTOS ÚTILES - MANTENER PERO REVISAR
        useful = [
            "API_DOCUMENTATION.md",   # Documentación de API
            "PRIVACY_POLICY.md",      # Política de privacidad
            "CONTRIBUTING.md",        # Guía de contribución
            "LICENSE",                # Licencia
        ]
        
        # DOCUMENTOS OBSOLETOS - ARCHIVAR O ELIMINAR
        obsolete = [
            "API_MIGRATION_SPECIFIC.md",     # Info de migración específica
            "CHROME_AI_HACKATHON_PLAN.md",   # Plan de hackathon específico
            "CHROME_AI_SETUP.md",            # Setup específico obsoleto
            "CHROME_FLAGS_GUIDE.md",         # Guía de flags específica
            "CHROME_STORE_PRIVACY_SETUP.md", # Setup específico obsoleto
            "COMPREHENSIVE_ANALYSIS.md",      # Análisis que ya no aplica
            "DEPENDENCIAS_MAGIC.md",         # Info obsoleta de dependencias
            "FIXES_SUMMARY.md",              # Resumen de fixes pasados
            "HACKATHON_SUBMISSION.md",       # Submission específico
            "MANTENIMIENTO_CODIGO.md",       # Info de mantenimiento obsoleta
            "PYTHON_3_13_COMPATIBILIDAD.md", # Info específica de versión
            "PYTHON_COMPATIBILITY_GUIDE.md", # Guía ya no necesaria
            "SEGURIDAD_CREDENCIALES.md",     # Info de seguridad obsoleta
            "SYSTEM_ANALYSIS.md",            # Análisis del sistema obsoleto
            "SYSTEM_DOCUMENTATION.md",       # Documentación del sistema obsoleta
            "VERTEX_AI_MIGRATION_STEPS.md",  # Pasos de migración específicos
        ]
        
        # ARCHIVOS DE CONFIGURACIÓN - MANTENER
        config_files = [
            "_config.yml",            # Configuración de Jekyll
            "index.md",               # Página principal
        ]
        
        return {
            "essential": essential,
            "useful": useful,
            "obsolete": obsolete,
            "config": config_files
        }
    
    def create_backup_structure(self):
        """Crea la estructura de backup."""
        # Crear directorio de archivo
        self.backup_path.mkdir(exist_ok=True)
        
        # Crear subdirectorios
        (self.backup_path / "migration").mkdir(exist_ok=True)
        (self.backup_path / "hackathon").mkdir(exist_ok=True)
        (self.backup_path / "analysis").mkdir(exist_ok=True)
        (self.backup_path / "compatibility").mkdir(exist_ok=True)
    
    def move_to_archive(self, files: List[str], category: str):
        """Mueve archivos al archivo por categoría."""
        category_path = self.backup_path / category
        category_path.mkdir(exist_ok=True)
        
        moved_count = 0
        for filename in files:
            file_path = self.docs_path / filename
            if file_path.exists():
                try:
                    destination = category_path / filename
                    shutil.move(str(file_path), str(destination))
                    print(f"   📦 Archivado: {filename} → archive/{category}/")
                    moved_count += 1
                except Exception as e:
                    print(f"   ⚠️  Error moviendo {filename}: {e}")
        
        return moved_count
    
    def create_new_readme(self):
        """Crea un nuevo README.md actualizado."""
        readme_content = '''# 📚 DOCUMENTACIÓN - GEMINI AI CHATBOT

## 🎯 Documentación Esencial

### 🚀 Inicio Rápido
- **[USER_GUIDE.md](USER_GUIDE.md)** - Guía completa de usuario
- **[FINAL_SOLUTION.md](FINAL_SOLUTION.md)** - Solución definitiva del proyecto
- **[CTRL_C_SOLUTION.md](CTRL_C_SOLUTION.md)** - Solución del problema Ctrl+C

### 🏗️ Desarrollo
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Estructura del proyecto
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Documentación de la API
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Guía para contribuir

### 🧹 Mantenimiento
- **[CLEANUP_SUMMARY.md](CLEANUP_SUMMARY.md)** - Resumen de limpieza del proyecto
- **[SCRIPT_COMPARISON.md](SCRIPT_COMPARISON.md)** - Comparación de scripts de inicio

### 📋 Legal y Políticas
- **[PRIVACY_POLICY.md](PRIVACY_POLICY.md)** - Política de privacidad
- **[LICENSE](LICENSE)** - Licencia del proyecto

## 🗂️ Archivo de Documentación

La documentación obsoleta y específica de versiones anteriores se ha movido a `archive/`:

- `archive/migration/` - Documentos de migración específicos
- `archive/hackathon/` - Documentos relacionados con hackathons
- `archive/analysis/` - Análisis técnicos obsoletos
- `archive/compatibility/` - Guías de compatibilidad específicas

## ⚡ Comandos Rápidos

```bash
# Iniciar aplicación
python run.py

# Verificar dependencias
python check_dependencies.py

# Limpiar proyecto
python scripts/clean_project.py
```

---

**📅 Última actualización:** {current_date}
**🎯 Estado:** Documentación organizada y actualizada
'''
        
        readme_path = self.docs_path / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content.format(current_date=datetime.now().strftime("%Y-%m-%d")))
        
        print("   ✅ README.md actualizado")
    
    def organize_all(self):
        """Ejecuta la organización completa."""
        print("📚 INICIANDO ORGANIZACIÓN DE DOCUMENTACIÓN")
        print("=" * 60)
        
        # Analizar documentos
        categories = self.analyze_documents()
        
        # Mostrar análisis
        total_files = sum(len(files) for files in categories.values())
        print(f"📊 Análisis completado: {total_files} documentos encontrados")
        print(f"   ✅ Esenciales: {len(categories['essential'])}")
        print(f"   ⚡ Útiles: {len(categories['useful'])}")
        print(f"   📦 Obsoletos: {len(categories['obsolete'])}")
        print(f"   ⚙️  Configuración: {len(categories['config'])}")
        print()
        
        # Crear estructura de backup
        print("📁 Creando estructura de archivo...")
        self.create_backup_structure()
        
        # Mover documentos obsoletos por categoría
        print("\n📦 Archivando documentos obsoletos...")
        
        # Documentos de migración
        migration_docs = [doc for doc in categories['obsolete'] if 'migration' in doc.lower() or 'vertex' in doc.lower()]
        self.move_to_archive(migration_docs, "migration")
        
        # Documentos de hackathon
        hackathon_docs = [doc for doc in categories['obsolete'] if 'hackathon' in doc.lower() or 'chrome' in doc.lower()]
        self.move_to_archive(hackathon_docs, "hackathon")
        
        # Documentos de análisis
        analysis_docs = [doc for doc in categories['obsolete'] if 'analysis' in doc.lower() or 'system' in doc.lower() or 'comprehensive' in doc.lower()]
        self.move_to_archive(analysis_docs, "analysis")
        
        # Documentos de compatibilidad
        compat_docs = [doc for doc in categories['obsolete'] if 'python' in doc.lower() or 'compatibility' in doc.lower() or 'dependencias' in doc.lower()]
        self.move_to_archive(compat_docs, "compatibility")
        
        # Otros documentos obsoletos
        remaining_obsolete = [doc for doc in categories['obsolete'] 
                            if doc not in migration_docs + hackathon_docs + analysis_docs + compat_docs]
        if remaining_obsolete:
            self.move_to_archive(remaining_obsolete, "misc")
        
        # Crear nuevo README
        print("\n📝 Actualizando documentación principal...")
        self.create_new_readme()
        
        # Resumen final
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE ORGANIZACIÓN:")
        
        # Contar archivos actuales
        current_files = list(self.docs_path.glob("*.md")) + list(self.docs_path.glob("*.yml"))
        archived_files = list(self.backup_path.rglob("*.*"))
        
        print(f"   📚 Documentos actuales: {len(current_files)}")
        print(f"   📦 Documentos archivados: {len(archived_files)}")
        print(f"   🧹 Reducción: {len(archived_files)} archivos removidos")
        
        # Mostrar estructura final
        print("\n📁 ESTRUCTURA FINAL:")
        for file in sorted(current_files):
            if file.is_file():
                print(f"   📄 {file.name}")
        
        print(f"\n📦 Archivo creado en: archive/")
        print("✅ Organización completada exitosamente!")
        
        return len(current_files), len(archived_files)


def main():
    """Función principal."""
    docs_path = Path(__file__).parent.parent / "docs"
    
    print(f"📍 Directorio de documentación: {docs_path}")
    
    # Confirmar acción
    response = input("\n¿Deseas proceder con la organización de documentación? (s/N): ")
    if response.lower() not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Organización cancelada.")
        return
    
    organizer = DocumentationOrganizer(docs_path)
    current_count, archived_count = organizer.organize_all()
    
    print(f"\n🎉 ¡Documentación organizada exitosamente!")
    print(f"📚 {current_count} documentos esenciales mantenidos")
    print(f"📦 {archived_count} documentos archivados")


if __name__ == "__main__":
    main()