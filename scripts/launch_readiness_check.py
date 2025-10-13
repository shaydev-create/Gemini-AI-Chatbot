#!/usr/bin/env python3
"""
🚀 SCRIPT DE VERIFICACIÓN PRE-LANZAMIENTO
Gemini AI Chatbot - Chrome Web Store Launch

Este script verifica que todos los componentes estén listos para el lanzamiento.
"""

import json
import sys
from datetime import datetime
from pathlib import Path


class LaunchReadinessChecker:
    """Verificador de preparación para lanzamiento"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = []
        self.total_checks = 0
        self.passed_checks = 0

    def log_result(self, test_name, passed, message, details=None):
        """Registrar resultado de prueba"""
        self.total_checks += 1
        if passed:
            self.passed_checks += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"

        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'details': details or [],
            'timestamp': datetime.now().isoformat()
        }

        self.results.append(result)
        print(f"{status} | {test_name}: {message}")

        if details:
            for detail in details:
                print(f"      └─ {detail}")

    def check_file_structure(self):
        """Verificar estructura de archivos"""
        print("\n🔍 Verificando estructura de archivos...")

        # Archivos principales requeridos
        required_files = [
            'app.py',
            'requirements.txt',
            'README.md',
            'app/static/css/style.css',
            'app/static/js/main.js',
            'app/templates/index.html',
            'src/__init__.py',
            'core/__init__.py'
        ]

        missing_files = []
        existing_files = []

        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                existing_files.append(file_path)
            else:
                missing_files.append(file_path)

        if not missing_files:
            self.log_result(
                "Estructura de Archivos",
                True,
                f"Todos los archivos principales están presentes ({
                    len(existing_files)}/{
                    len(required_files)})",
                existing_files)
        else:
            self.log_result(
                "Estructura de Archivos",
                False,
                f"Faltan {len(missing_files)} archivos principales",
                [f"FALTANTE: {f}" for f in missing_files]
            )

    def check_chrome_extension(self):
        """Verificar extensión de Chrome"""
        print("\n🔍 Verificando extensión de Chrome...")

        chrome_dir = self.project_root / 'chrome_extension'

        if not chrome_dir.exists():
            self.log_result(
                "Extensión Chrome - Directorio",
                False,
                "Directorio chrome_extension no existe"
            )
            return

        # Archivos requeridos para la extensión
        required_extension_files = [
            'manifest.json',
            'popup.html',
            'popup.js',
            'background.js',
            'content.js',
            'index.html',
            'icons/icon_16.png',
            'icons/icon_48.png',
            'icons/icon_128.png'
        ]

        missing_ext_files = []
        existing_ext_files = []

        for file_path in required_extension_files:
            full_path = chrome_dir / file_path
            if full_path.exists():
                existing_ext_files.append(file_path)
            else:
                missing_ext_files.append(file_path)

        if not missing_ext_files:
            self.log_result(
                "Extensión Chrome - Archivos",
                True,
                f"Todos los archivos de extensión están presentes ({
                    len(existing_ext_files)}/{
                    len(required_extension_files)})")
        else:
            self.log_result(
                "Extensión Chrome - Archivos",
                False,
                f"Faltan {len(missing_ext_files)} archivos de extensión",
                [f"FALTANTE: {f}" for f in missing_ext_files]
            )

        # Verificar manifest.json
        manifest_path = chrome_dir / 'manifest.json'
        if manifest_path.exists():
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)

                required_manifest_fields = [
                    'name', 'version', 'manifest_version', 'permissions', 'action']
                missing_fields = [
                    field for field in required_manifest_fields if field not in manifest]

                if not missing_fields:
                    self.log_result(
                        "Extensión Chrome - Manifest",
                        True,
                        f"Manifest válido - {manifest.get('name')} v{manifest.get('version')}"
                    )
                else:
                    self.log_result(
                        "Extensión Chrome - Manifest",
                        False,
                        f"Manifest incompleto - faltan campos: {', '.join(missing_fields)}"
                    )

            except json.JSONDecodeError as e:
                self.log_result(
                    "Extensión Chrome - Manifest",
                    False,
                    f"Manifest JSON inválido: {str(e)}"
                )

        # Verificar paquete ZIP
        zip_files = list(self.project_root.glob(
            'gemini-ai-chatbot-chrome-*.zip'))
        if zip_files:
            latest_zip = max(zip_files, key=lambda x: x.stat().st_mtime)
            zip_size = latest_zip.stat().st_size

            self.log_result(
                "Extensión Chrome - Paquete",
                True,
                f"Paquete ZIP disponible: {
                    latest_zip.name} ({
                    zip_size:,        } bytes)")
        else:
            self.log_result(
                "Extensión Chrome - Paquete",
                False,
                "No se encontró paquete ZIP de la extensión"
            )

    def check_server_configuration(self):
        """Verificar configuración del servidor"""
        print("\n🔍 Verificando configuración del servidor...")

        app_py = self.project_root / 'app.py'
        if app_py.exists():
            try:
                with open(app_py, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Verificar configuraciones importantes
                checks = [
                    ('SSL/HTTPS', 'ssl_context' in content or 'https' in content.lower()),
                    ('Debug Mode', 'debug=False' in content or 'DEBUG = False' in content),
                    ('Puerto 5000', 'port=5000' in content or '5000' in content),
                    ('Host Configuration', 'host=' in content)
                ]

                passed_configs = []
                failed_configs = []

                for check_name, condition in checks:
                    if condition:
                        passed_configs.append(check_name)
                    else:
                        failed_configs.append(check_name)

                if len(passed_configs) >= 3:  # Al menos 3 de 4 configuraciones
                    self.log_result(
                        "Configuración Servidor",
                        True,
                        f"Configuración adecuada ({len(passed_configs)}/4)",
                        passed_configs
                    )
                else:
                    self.log_result(
                        "Configuración Servidor",
                        False,
                        f"Configuración incompleta ({len(passed_configs)}/4)",
                        failed_configs
                    )

            except Exception as e:
                self.log_result(
                    "Configuración Servidor",
                    False,
                    f"Error leyendo app.py: {str(e)}"
                )
        else:
            self.log_result(
                "Configuración Servidor",
                False,
                "Archivo app.py no encontrado"
            )

    def check_static_assets(self):
        """Verificar assets estáticos"""
        print("\n🔍 Verificando assets estáticos...")

        static_dir = self.project_root / 'app' / 'static'

        if not static_dir.exists():
            self.log_result(
                "Assets Estáticos",
                False,
                "Directorio static no existe"
            )
            return

        # Verificar subdirectorios y archivos importantes
        important_assets = [
            'css/style.css',
            'js/main.js',
            'images/icon.svg',
            'images/icon.png'
        ]

        existing_assets = []
        missing_assets = []

        for asset in important_assets:
            asset_path = static_dir / asset
            if asset_path.exists():
                size = asset_path.stat().st_size
                existing_assets.append(f"{asset} ({size:,} bytes)")
            else:
                missing_assets.append(asset)

        if len(existing_assets) >= len(important_assets) * \
                0.75:  # Al menos 75% de assets
            self.log_result(
                "Assets Estáticos",
                True,
                f"Assets principales disponibles ({len(existing_assets)}/{len(important_assets)})",
                existing_assets
            )
        else:
            self.log_result(
                "Assets Estáticos",
                False,
                f"Faltan assets importantes ({len(missing_assets)} faltantes)",
                missing_assets
            )

    def check_documentation(self):
        """Verificar documentación"""
        print("\n🔍 Verificando documentación...")

        docs = [
            ('README.md', 'Documentación principal'),
            ('docs/INSTALLATION.md', 'Guía de instalación'),
            ('docs/API_DOCUMENTATION.md', 'Documentación API'),
            ('docs/USER_GUIDE.md', 'Guía de usuario')
        ]

        existing_docs = []
        missing_docs = []

        for doc_path, description in docs:
            full_path = self.project_root / doc_path
            if full_path.exists():
                size = full_path.stat().st_size
                existing_docs.append(f"{description} ({size:,} bytes)")
            else:
                missing_docs.append(f"{description} ({doc_path})")

        if len(existing_docs) >= 2:  # Al menos 2 documentos importantes
            self.log_result(
                "Documentación",
                True,
                f"Documentación disponible ({len(existing_docs)}/{len(docs)})",
                existing_docs
            )
        else:
            self.log_result(
                "Documentación",
                False,
                f"Documentación insuficiente ({len(existing_docs)}/{len(docs)})",
                missing_docs
            )

    def check_security_features(self):
        """Verificar características de seguridad"""
        print("\n🔍 Verificando características de seguridad...")

        security_files = [
            ('src/auth.py', 'Sistema de autenticación'),
            ('src/security.py', 'Módulo de seguridad'),
            ('core/security_manager.py', 'Gestor de seguridad')
        ]

        security_features = []

        for file_path, description in security_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                security_features.append(description)

        # Verificar requirements.txt para dependencias de seguridad
        req_file = self.project_root / 'requirements.txt'
        security_deps = []

        if req_file.exists():
            with open(req_file, 'r') as f:
                content = f.read().lower()

            security_packages = [
                'flask-jwt-extended',
                'bcrypt',
                'cryptography',
                'flask-limiter']
            for package in security_packages:
                if package in content:
                    security_deps.append(package)

        total_security_features = len(security_features) + len(security_deps)

        if total_security_features >= 4:
            self.log_result(
                "Características Seguridad",
                True,
                f"Características de seguridad implementadas ({total_security_features})",
                security_features + [f"Dependencia: {dep}" for dep in security_deps]
            )
        else:
            self.log_result(
                "Características Seguridad",
                False,
                f"Características de seguridad insuficientes ({total_security_features})")

    def generate_report(self):
        """Generar reporte final"""
        print("\n" + "=" * 80)
        print("🚀 REPORTE DE PREPARACIÓN PARA LANZAMIENTO")
        print("=" * 80)

        success_rate = (self.passed_checks / self.total_checks) * \
            100 if self.total_checks > 0 else 0

        print("\n📊 RESUMEN GENERAL:")
        print(f"   ✅ Pruebas exitosas: {self.passed_checks}")
        print(
            f"   ❌ Pruebas fallidas: {
                self.total_checks -
                self.passed_checks}")
        print(f"   📈 Tasa de éxito: {success_rate:.1f}%")

        # Determinar estado de preparación
        if success_rate >= 90:
            status = "🟢 LISTO PARA LANZAMIENTO"
            recommendation = "El sistema está listo para ser lanzado en Chrome Web Store."
        elif success_rate >= 75:
            status = "🟡 CASI LISTO"
            recommendation = "Corrige los problemas menores antes del lanzamiento."
        else:
            status = "🔴 NO LISTO"
            recommendation = "Se requieren correcciones importantes antes del lanzamiento."

        print(f"\n🎯 ESTADO: {status}")
        print(f"💡 RECOMENDACIÓN: {recommendation}")

        # Detalles de pruebas fallidas
        failed_tests = [r for r in self.results if "❌" in r['status']]
        if failed_tests:
            print(f"\n❌ PRUEBAS FALLIDAS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['message']}")

        # Guardar reporte
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.project_root / \
            f"launch_readiness_report_{timestamp}.json"

        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_checks': self.total_checks,
                'passed_checks': self.passed_checks,
                'success_rate': success_rate,
                'status': status,
                'recommendation': recommendation
            },
            'results': self.results
        }

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        print(f"\n📄 Reporte guardado en: {report_file.name}")

        return success_rate >= 75

    def run_all_checks(self):
        """Ejecutar todas las verificaciones"""
        print("🚀 INICIANDO VERIFICACIÓN DE PREPARACIÓN PARA LANZAMIENTO")
        print("=" * 80)

        # Ejecutar todas las verificaciones
        self.check_file_structure()
        self.check_chrome_extension()
        self.check_server_configuration()
        self.check_static_assets()
        self.check_documentation()
        self.check_security_features()

        # Generar reporte final
        return self.generate_report()


def main():
    """Función principal"""
    checker = LaunchReadinessChecker()

    try:
        ready_for_launch = checker.run_all_checks()

        if ready_for_launch:
            print("\n🎉 ¡FELICITACIONES! El sistema está listo para el lanzamiento.")
            print("\n📋 PRÓXIMOS PASOS:")
            print("   1. Sube la extensión a Chrome Web Store Developer Dashboard")
            print(
                "   2. Completa la información de la tienda (descripción, capturas, etc.)")
            print("   3. Configura el servidor de producción")
            print("   4. Realiza pruebas finales en el entorno de producción")
            print("   5. Publica la extensión")

            return True
        else:
            print("\n⚠️  Se requieren correcciones antes del lanzamiento.")
            print("   Revisa el reporte detallado y corrige los problemas identificados.")

            return False

    except Exception as e:
        print(f"\n❌ Error durante la verificación: {str(e)}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
