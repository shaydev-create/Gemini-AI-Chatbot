#!/usr/bin/env python3
"""
Script para verificar y configurar Chrome Built-in AI automáticamente
"""

import os
import platform
import subprocess
import sys


class ChromeAISetup:
    def __init__(self):
        self.system = platform.system()
        self.chrome_paths = self.get_chrome_canary_paths()

    def get_chrome_canary_paths(self):
        """Obtiene las rutas típicas de Chrome Canary según el OS"""
        if self.system == "Windows":
            return [
                os.path.expanduser(r"~\AppData\Local\Google\Chrome SxS\Application\chrome.exe"),
                r"C:\Program Files\Google\Chrome SxS\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome SxS\Application\chrome.exe",
            ]
        elif self.system == "Darwin":  # macOS
            return ["/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary"]
        else:  # Linux
            return [
                "/usr/bin/google-chrome-unstable",
                "/opt/google/chrome-unstable/chrome",
            ]

    def find_chrome_canary(self):
        """Busca la instalación de Chrome Canary"""
        for path in self.chrome_paths:
            if os.path.exists(path):
                return path
        return None

    def check_server_running(self):
        """Verifica si el servidor Flask está ejecutándose"""
        try:
            import requests

            response = requests.get("http://127.0.0.1:5000", timeout=3)
            return response.status_code == 200
        except Exception:
            return False

    def launch_chrome_ai(self, chrome_path, url="http://127.0.0.1:5000"):
        """Lanza Chrome Canary con las flags de AI habilitadas"""

        # Flags necesarias para Chrome Built-in AI
        flags = [
            "--enable-features=AIAssistantAPI,PromptAPIForGeminiNano,SummarizationAPIForGeminiNano,RewriterAPIForGeminiNano,ComposerAPIForGeminiNano,TranslationAPI",
            "--disable-features=OptimizationGuidePushNotifications",
            "--enable-ai-assistant-api",
            "--user-data-dir=" + os.path.join(os.path.expanduser("~"), ".chrome-ai-profile"),
            "--no-first-run",
            "--disable-default-apps",
        ]

        cmd = [chrome_path] + flags + [url]

        print("🚀 Iniciando Chrome Canary con Chrome Built-in AI...")
        print(f"📍 URL: {url}")
        print(f"⚙️  Flags: {' '.join(flags)}")

        try:
            subprocess.Popen(cmd)
            return True
        except Exception as e:
            print(f"❌ Error al iniciar Chrome: {e}")
            return False

    def setup_chrome_ai(self):
        """Configuración completa de Chrome Built-in AI"""
        print("🤖 Chrome Built-in AI Setup")
        print("=" * 50)

        # 1. Verificar Chrome Canary
        chrome_path = self.find_chrome_canary()
        if not chrome_path:
            print("❌ Chrome Canary no encontrado")
            print("📥 Descarga desde: https://www.google.com/chrome/canary/")
            return False

        print(f"✅ Chrome Canary encontrado: {chrome_path}")

        # 2. Verificar servidor Flask
        if not self.check_server_running():
            print("⚠️  Servidor Flask no está ejecutándose")
            print("💡 Ejecuta primero: python run_development.py")

            # Intentar iniciar el servidor
            answer = input("¿Quieres que inicie el servidor automáticamente? (y/n): ")
            if answer.lower() == "y":
                self.start_flask_server()
        else:
            print("✅ Servidor Flask ejecutándose en http://127.0.0.1:5000")

        # 3. Lanzar Chrome Canary
        success = self.launch_chrome_ai(chrome_path)

        if success:
            print("\n🎉 ¡Chrome Built-in AI configurado!")
            print("📋 Qué esperar:")
            print("   • La primera vez descargará modelos AI (~100MB)")
            print("   • Busca el botón 'Chrome AI' en la aplicación")
            print("   • Prueba el modo 'Local' para AI privado")
            print("\n💡 Consejos:")
            print("   • Mantén Chrome Canary actualizado")
            print("   • Las APIs están en desarrollo (pueden cambiar)")
            return True
        else:
            return False

    def start_flask_server(self):
        """Intenta iniciar el servidor Flask"""
        try:
            print("🔧 Iniciando servidor Flask...")
            subprocess.Popen(
                [sys.executable, "run_development.py"],
                cwd=os.path.dirname(os.path.abspath(__file__)),
            )
            print("✅ Servidor Flask iniciado")
        except Exception as e:
            print(f"❌ Error al iniciar servidor: {e}")


def main():
    setup = ChromeAISetup()
    setup.setup_chrome_ai()


if __name__ == "__main__":
    main()
