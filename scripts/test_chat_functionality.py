#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de pruebas automatizadas para verificar todas las funcionalidades del chat
antes del lanzamiento en Chrome Web Store.

Autor: Gemini AI Chatbot Team
Fecha: 2025-01-15
"""

import json
import os
import sys
import time
from datetime import datetime

import requests

# Configuración
BASE_URL = "https://localhost:5000"
API_URL = f"{BASE_URL}/api/chat/send"

# Colores para output


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_header(text):
    """Imprime un header colorido"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 60}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text.center(60)}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 60}{Colors.END}\n")


def print_success(text):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_error(text):
    """Imprime mensaje de error"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_warning(text):
    """Imprime mensaje de advertencia"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def print_info(text):
    """Imprime mensaje informativo"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")


def test_server_connection():
    """Prueba la conexión al servidor"""
    print_header("PRUEBA 1: CONEXIÓN AL SERVIDOR")

    try:
        # Deshabilitar verificación SSL para desarrollo
        import urllib3

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        response = requests.get(BASE_URL, verify=False, timeout=10)
        if response.status_code == 200:
            print_success(f"Servidor accesible en {BASE_URL}")
            print_info(f"Código de estado: {response.status_code}")
            return True
        else:
            print_error(f"Servidor respondió con código: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("No se pudo conectar al servidor")
        print_warning("Asegúrate de que el servidor esté ejecutándose")
        return False
    except Exception as e:
        print_error(f"Error inesperado: {str(e)}")
        return False


def test_chat_api():
    """Prueba la API del chat"""
    print_header("PRUEBA 2: API DEL CHAT")

    test_messages = [
        "Hola, ¿cómo estás?",
        "¿Cuál es tu nombre?",
        "Explícame qué es la inteligencia artificial",
        "¿Puedes ayudarme con matemáticas?",
        "Cuéntame un chiste",
    ]

    success_count = 0
    total_tests = len(test_messages)

    for i, message in enumerate(test_messages, 1):
        print_info(f"Prueba {i}/{total_tests}: Enviando mensaje...")
        print(f"   📝 Mensaje: '{message}'")

        try:
            # Deshabilitar verificación SSL para desarrollo
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            payload = {"message": message}
            headers = {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
            }

            start_time = time.time()
            response = requests.post(
                API_URL, json=payload, headers=headers, verify=False, timeout=30
            )
            response_time = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print_success(
                        f"Respuesta recibida en {
                            response_time:.2f}s"
                    )
                    print(
                        f"   🤖 Respuesta: '{
                            data.get(
                                'message',
                                'Sin mensaje')[
                                :100]}...'"
                    )
                    success_count += 1
                else:
                    print_error(
                        f"API respondió con error: {
                            data.get(
                                'message',
                                'Error desconocido')}"
                    )
            else:
                print_error(f"Error HTTP: {response.status_code}")

        except requests.exceptions.Timeout:
            print_error("Timeout - La respuesta tardó más de 30 segundos")
        except Exception as e:
            print_error(f"Error en la prueba: {str(e)}")

        # Pausa entre pruebas
        if i < total_tests:
            time.sleep(1)

    print(f"\n{Colors.BOLD}Resultado de pruebas de API:{Colors.END}")
    print(f"   ✅ Exitosas: {success_count}/{total_tests}")
    print(f"   ❌ Fallidas: {total_tests - success_count}/{total_tests}")

    if success_count == total_tests:
        return True
    else:
        print_error(f"{success_count}/{total_tests} pruebas de API pasaron")
        return False


def test_chat_page():
    """Prueba la página del chat"""
    print_header("PRUEBA 3: PÁGINA DEL CHAT")

    try:
        # Deshabilitar verificación SSL para desarrollo
        import urllib3

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        chat_url = f"{BASE_URL}/chat"
        response = requests.get(chat_url, verify=False, timeout=10)

        if response.status_code == 200:
            content = response.text

            # Verificar elementos esenciales
            essential_elements = [
                'id="messages"',
                'id="messageInput"',
                'id="sendButton"',
                'id="typing"',
                'class="action-btn"',
                "sendMessage()",
                "addMessage",
                "showTyping",
                "hideTyping",
            ]

            missing_elements = []
            for element in essential_elements:
                if element not in content:
                    missing_elements.append(element)

            if not missing_elements:
                print_success("Página del chat cargada correctamente")
                print_success("Todos los elementos esenciales están presentes")

                # Verificar funcionalidades específicas
                functionalities = [
                    (
                        "Función sendMessage",
                        "function sendMessage" in content
                        or "async function sendMessage" in content,
                    ),
                    ("Botones de acción", "action-btn" in content),
                    ("Indicador de escritura", "typing-indicator" in content),
                    ("Contador de caracteres", "char-counter" in content),
                    ("Carga de archivos", "fileInput" in content),
                    ("Síntesis de voz", "speechSynthesis" in content),
                    ("Drag and drop", "dragover" in content),
                    ("Atajos de teclado", "keydown" in content),
                ]

                for func_name, is_present in functionalities:
                    if is_present:
                        print_success(f"{func_name}: Implementada")
                    else:
                        print_warning(f"{func_name}: No detectada")

                return True
            else:
                print_error("Elementos faltantes en la página del chat:")
                for element in missing_elements:
                    print(f"   ❌ {element}")
                return False

        else:
            print_error(f"No se pudo cargar la página del chat: {response.status_code}")
            return False

    except Exception as e:
        print_error(f"Error al probar la página del chat: {str(e)}")
        return False


def test_file_structure():
    """Verifica la estructura de archivos necesaria"""
    print_header("PRUEBA 4: ESTRUCTURA DE ARCHIVOS")

    required_files = [
        "app.py",
        "templates/chat.html",
        "templates/index.html",
        "static/css/style.css",
        "static/images/icon.png",
        "gemini-ai-chatbot-chrome-20250715_145314.zip",
        "chrome_store_assets/screenshots/screenshot_1_main.png",
        "chrome_store_assets/screenshots/screenshot_2_features.png",
        "chrome_store_assets/screenshots/promo_tile.png",
        "chrome_store_assets/icons/icon_128.png",
        "docs/privacy_policy.html",
        "docs/terms_of_service.html",
        "docs/EXECUTIVE_SUMMARY.md",
        "docs/VERTEX_AI_MIGRATION_STEPS.md",
        "docs/LAUNCH_STEP_BY_STEP.md",
    ]

    missing_files = []
    present_files = []

    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    for file_path in required_files:
        full_path = os.path.join(base_path, file_path)
        if os.path.exists(full_path):
            present_files.append(file_path)
            print_success(f"Archivo presente: {file_path}")
        else:
            missing_files.append(file_path)
            print_error(f"Archivo faltante: {file_path}")

    print(f"\n{Colors.BOLD}Resultado de verificación de archivos:{Colors.END}")
    print(f"   ✅ Presentes: {len(present_files)}/{len(required_files)}")
    print(f"   ❌ Faltantes: {len(missing_files)}/{len(required_files)}")

    if len(missing_files) == 0:
        return True
    else:
        print_error(f"Archivos faltantes: {missing_files}")
        return False


def test_chrome_extension_package():
    """Verifica el paquete de la extensión de Chrome"""
    print_header("PRUEBA 5: PAQUETE DE EXTENSIÓN DE CHROME")

    try:
        import zipfile

        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        zip_path = os.path.join(
            base_path, "gemini-ai-chatbot-chrome-20250715_145314.zip"
        )

        if not os.path.exists(zip_path):
            print_error("Archivo ZIP de la extensión no encontrado")
            return False

        with zipfile.ZipFile(zip_path, "r") as zip_file:
            files_in_zip = zip_file.namelist()

            required_extension_files = [
                "manifest.json",
                "index.html",
                "background.js",
                "content.js",
                "popup.html",
                "popup.js",
                "icons/icon_16.png",
                "icons/icon_48.png",
                "icons/icon_128.png",
            ]

            missing_in_zip = []
            for file_name in required_extension_files:
                if file_name not in files_in_zip:
                    missing_in_zip.append(file_name)
                else:
                    print_success(f"Archivo en ZIP: {file_name}")

            if missing_in_zip:
                print_error("Archivos faltantes en el ZIP:")
                for file_name in missing_in_zip:
                    print(f"   ❌ {file_name}")
                return False
            else:
                print_success("Paquete de extensión completo")

                # Verificar manifest.json
                try:
                    manifest_content = zip_file.read("manifest.json").decode("utf-8")
                    manifest_data = json.loads(manifest_content)

                    print_info(
                        f"Nombre: {manifest_data.get('name', 'No especificado')}"
                    )
                    print_info(
                        f"Versión: {manifest_data.get('version', 'No especificada')}"
                    )
                    print_info(
                        f"Descripción: {manifest_data.get('description', 'No especificada')[:50]}..."
                    )

                except Exception as e:
                    print_warning(f"No se pudo leer manifest.json: {str(e)}")

                return True

    except Exception as e:
        print_error(f"Error al verificar el paquete ZIP: {str(e)}")
        return False


def generate_test_report(results):
    """Genera un reporte de las pruebas"""
    print_header("REPORTE FINAL DE PRUEBAS")

    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)

    print(f"{Colors.BOLD}Resumen de Pruebas:{Colors.END}")
    print(f"   📊 Total de pruebas: {total_tests}")
    print(f"   ✅ Pruebas exitosas: {passed_tests}")
    print(f"   ❌ Pruebas fallidas: {total_tests - passed_tests}")
    print(f"   📈 Porcentaje de éxito: {(passed_tests / total_tests) * 100:.1f}%")

    print(f"\n{Colors.BOLD}Detalle por prueba:{Colors.END}")
    for test_name, result in results.items():
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        color = Colors.GREEN if result else Colors.RED
        print(f"   {color}{status}{Colors.END} - {test_name}")

    # Recomendaciones
    print(f"\n{Colors.BOLD}Recomendaciones:{Colors.END}")

    if passed_tests == total_tests:
        print_success(
            "🎉 ¡Todas las pruebas pasaron! El sistema está listo para el lanzamiento."
        )
        print_info("✅ Puedes proceder con la publicación en Chrome Web Store")
        print_info("✅ Todas las funcionalidades están operativas")
        print_info("✅ La estructura de archivos es correcta")
    elif passed_tests >= total_tests * 0.8:
        print_warning(
            "⚠️ La mayoría de pruebas pasaron, pero hay algunos problemas menores"
        )
        print_info("🔧 Revisa los errores reportados antes del lanzamiento")
        print_info("📋 Considera hacer pruebas manuales adicionales")
    else:
        print_error("❌ Múltiples pruebas fallaron - NO recomendado para lanzamiento")
        print_warning("🛠️ Corrige los errores críticos antes de proceder")
        print_warning("🔍 Realiza una revisión completa del sistema")

    # Guardar reporte
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"test_report_{timestamp}.txt"

    try:
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("REPORTE DE PRUEBAS - GEMINI AI CHATBOT\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'=' * 50}\n\n")
            f.write(f"Total de pruebas: {total_tests}\n")
            f.write(f"Pruebas exitosas: {passed_tests}\n")
            f.write(f"Pruebas fallidas: {total_tests - passed_tests}\n")
            f.write(
                f"Porcentaje de éxito: {(passed_tests / total_tests) * 100:.1f}%\n\n"
            )

            f.write("DETALLE POR PRUEBA:\n")
            for test_name, result in results.items():
                status = "PASÓ" if result else "FALLÓ"
                f.write(f"- {test_name}: {status}\n")

        print_info(f"📄 Reporte guardado en: {report_file}")

    except Exception as e:
        print_warning(f"No se pudo guardar el reporte: {str(e)}")


def main():
    """Función principal"""
    print_header("🤖 GEMINI AI CHATBOT - PRUEBAS PRE-LANZAMIENTO")
    print_info(
        f"Iniciando pruebas en: {
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    # Ejecutar todas las pruebas
    results = {}

    results["Conexión al Servidor"] = test_server_connection()
    results["API del Chat"] = test_chat_api()
    results["Página del Chat"] = test_chat_page()
    results["Estructura de Archivos"] = test_file_structure()
    results["Paquete de Extensión"] = test_chrome_extension_package()

    # Generar reporte final
    generate_test_report(results)

    # Código de salida
    all_passed = all(results.values())
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
