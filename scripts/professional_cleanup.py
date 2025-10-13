#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧹 SCRIPT DE LIMPIEZA PROFESIONAL
================================

Script para optimizar el proyecto para publicación profesional:
1. Detectar y eliminar código duplicado
2. Optimizar archivos CSS/JS 
3. Validar estructura del proyecto
4. Preparar para Chrome Web Store
5. Verificar cumplimiento de estándares

Autor: Gemini AI Assistant
Versión: 1.0.0
"""

import os
import sys
import shutil
import re
from pathlib import Path
from typing import List, Dict, Set
import hashlib


class ProfessionalCleanup:
    """Herramienta de limpieza profesional del proyecto."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.findings = []
        self.duplicates_found = 0
        self.files_cleaned = 0
        
    def log_finding(self, category: str, message: str, severity: str = "INFO"):
        """Registrar hallazgo del análisis."""
        self.findings.append({
            'category': category,
            'message': message,
            'severity': severity
        })
        print(f"[{severity}] {category}: {message}")
    
    def detect_duplicate_css_rules(self, file_path: Path) -> List[str]:
        """Detectar reglas CSS duplicadas."""
        duplicates = []
        if file_path.suffix in ['.css', '.html']:
            try:
                content = file_path.read_text(encoding='utf-8')
                # Extraer reglas CSS
                css_rules = re.findall(r'([^{]+\{[^}]+\})', content)
                seen_rules = set()
                
                for rule in css_rules:
                    rule_hash = hashlib.md5(rule.encode()).hexdigest()
                    if rule_hash in seen_rules:
                        duplicates.append(rule.strip())
                    seen_rules.add(rule_hash)
                        
            except Exception as e:
                self.log_finding("CSS_ERROR", f"Error leyendo {file_path}: {e}", "ERROR")
                
        return duplicates
    
    def detect_duplicate_js_functions(self, file_path: Path) -> List[str]:
        """Detectar funciones JavaScript duplicadas."""
        duplicates = []
        if file_path.suffix in ['.js', '.html']:
            try:
                content = file_path.read_text(encoding='utf-8')
                # Extraer funciones JS
                js_functions = re.findall(r'function\s+(\w+)\s*\([^)]*\)\s*\{', content)
                function_counts = {}
                
                for func in js_functions:
                    function_counts[func] = function_counts.get(func, 0) + 1
                    
                duplicates = [func for func, count in function_counts.items() if count > 1]
                        
            except Exception as e:
                self.log_finding("JS_ERROR", f"Error leyendo {file_path}: {e}", "ERROR")
                
        return duplicates
    
    def optimize_html_templates(self, file_path: Path):
        """Optimizar plantillas HTML."""
        try:
            content = file_path.read_text(encoding='utf-8')
            original_size = len(content)
            
            # Eliminar comentarios HTML innecesarios (pero no los importantes)
            content = re.sub(r'<!--\s*TODO:.*?-->', '', content)
            content = re.sub(r'<!--\s*DEBUG:.*?-->', '', content)
            
            # Eliminar espacios múltiples entre tags
            content = re.sub(r'>\s+<', '><', content)
            
            # Eliminar líneas vacías múltiples
            content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
            
            new_size = len(content)
            if new_size < original_size:
                file_path.write_text(content, encoding='utf-8')
                reduction = original_size - new_size
                self.log_finding("OPTIMIZATION", f"Optimizado {file_path.name}: -{reduction} bytes")
                self.files_cleaned += 1
                
        except Exception as e:
            self.log_finding("OPTIMIZATION_ERROR", f"Error optimizando {file_path}: {e}", "ERROR")
    
    def check_chrome_extension_compliance(self):
        """Verificar cumplimiento con políticas de Chrome Web Store."""
        manifest_path = self.project_root / "chrome_extension" / "manifest.json"
        
        if not manifest_path.exists():
            self.log_finding("CHROME_COMPLIANCE", "manifest.json no encontrado", "ERROR")
            return False
            
        try:
            import json
            manifest = json.loads(manifest_path.read_text())
            
            # Verificaciones obligatorias
            required_fields = ["name", "version", "description", "permissions", "manifest_version"]
            missing_fields = [field for field in required_fields if field not in manifest]
            
            if missing_fields:
                self.log_finding("CHROME_COMPLIANCE", f"Campos faltantes en manifest.json: {missing_fields}", "ERROR")
                return False
            
            # Verificar Manifest V3
            if manifest.get("manifest_version") != 3:
                self.log_finding("CHROME_COMPLIANCE", "Debe usar Manifest V3", "WARNING")
            
            # Verificar descrición no excede 132 caracteres
            if len(manifest.get("description", "")) > 132:
                self.log_finding("CHROME_COMPLIANCE", "Descripción excede 132 caracteres", "WARNING")
            
            # Verificar iconos
            if "icons" not in manifest:
                self.log_finding("CHROME_COMPLIANCE", "Falta especificar iconos", "WARNING")
            
            self.log_finding("CHROME_COMPLIANCE", "Extensión Chrome cumple requisitos básicos", "SUCCESS")
            return True
            
        except Exception as e:
            self.log_finding("CHROME_COMPLIANCE", f"Error validando manifest.json: {e}", "ERROR")
            return False
    
    def clean_unused_files(self):
        """Eliminar archivos innecesarios."""
        patterns_to_remove = [
            "**/__pycache__",
            "**/*.pyc",
            "**/.DS_Store",
            "**/Thumbs.db",
            "**/*.tmp",
            "**/*.temp"
        ]
        
        removed_count = 0
        for pattern in patterns_to_remove:
            for file_path in self.project_root.glob(pattern):
                try:
                    if file_path.is_file():
                        file_path.unlink()
                        removed_count += 1
                    elif file_path.is_dir():
                        shutil.rmtree(file_path)
                        removed_count += 1
                except Exception as e:
                    self.log_finding("CLEANUP_ERROR", f"Error eliminando {file_path}: {e}", "ERROR")
        
        if removed_count > 0:
            self.log_finding("CLEANUP", f"Eliminados {removed_count} archivos temporales", "SUCCESS")
    
    def validate_project_structure(self):
        """Validar estructura del proyecto."""
        required_dirs = ["app", "chrome_extension", "tests", "docs"]
        required_files = ["README.md", "pyproject.toml", "requirements.txt"]
        
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                self.log_finding("STRUCTURE", f"Directorio faltante: {dir_name}", "WARNING")
            else:
                self.log_finding("STRUCTURE", f"Directorio OK: {dir_name}", "SUCCESS")
        
        for file_name in required_files:
            file_path = self.project_root / file_name
            if not file_path.exists():
                self.log_finding("STRUCTURE", f"Archivo faltante: {file_name}", "WARNING")
            else:
                self.log_finding("STRUCTURE", f"Archivo OK: {file_name}", "SUCCESS")
    
    def run_analysis(self):
        """Ejecutar análisis completo."""
        print("🔍 INICIANDO ANÁLISIS PROFESIONAL DEL PROYECTO")
        print("=" * 50)
        
        # 1. Validar estructura
        print("\n📁 Validando estructura del proyecto...")
        self.validate_project_structure()
        
        # 2. Limpiar archivos innecesarios
        print("\n🧹 Limpiando archivos temporales...")
        self.clean_unused_files()
        
        # 3. Analizar duplicados
        print("\n🔍 Analizando código duplicado...")
        for file_path in self.project_root.rglob("*.html"):
            css_dups = self.detect_duplicate_css_rules(file_path)
            js_dups = self.detect_duplicate_js_functions(file_path)
            
            if css_dups:
                self.log_finding("DUPLICATE_CSS", f"{file_path.name}: {len(css_dups)} reglas CSS duplicadas", "WARNING")
                self.duplicates_found += len(css_dups)
                
            if js_dups:
                self.log_finding("DUPLICATE_JS", f"{file_path.name}: Funciones duplicadas: {js_dups}", "WARNING")
                self.duplicates_found += len(js_dups)
        
        # 4. Optimizar templates
        print("\n⚡ Optimizando plantillas HTML...")
        for html_file in self.project_root.rglob("*.html"):
            self.optimize_html_templates(html_file)
        
        # 5. Verificar compliance Chrome
        print("\n🌐 Verificando compliance Chrome Web Store...")
        self.check_chrome_extension_compliance()
        
        # Resumen final
        print("\n" + "=" * 50)
        print("📊 RESUMEN DEL ANÁLISIS")
        print(f"• Archivos optimizados: {self.files_cleaned}")
        print(f"• Duplicados encontrados: {self.duplicates_found}")
        print(f"• Total de hallazgos: {len(self.findings)}")
        
        # Conteo por severidad
        severity_counts = {}
        for finding in self.findings:
            sev = finding['severity']
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        for severity, count in severity_counts.items():
            print(f"• {severity}: {count}")
        
        return self.findings


def main():
    """Función principal."""
    project_root = Path(__file__).parent.parent
    
    cleanup = ProfessionalCleanup(str(project_root))
    findings = cleanup.run_analysis()
    
    # Determinar si el proyecto está listo
    errors = [f for f in findings if f['severity'] == 'ERROR']
    warnings = [f for f in findings if f['severity'] == 'WARNING']
    
    print("\n🎯 EVALUACIÓN FINAL")
    print("=" * 30)
    
    if len(errors) == 0:
        print("✅ PROYECTO LISTO PARA PRODUCCIÓN")
        if len(warnings) > 0:
            print(f"⚠️  Se encontraron {len(warnings)} advertencias menores")
    else:
        print(f"❌ REQUIERE CORRECCIONES: {len(errors)} errores críticos")
    
    return len(errors) == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)