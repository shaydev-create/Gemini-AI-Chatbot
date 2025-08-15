"""
Tests end-to-end para flujos de usuario.
"""

import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

@pytest.fixture
def driver():
    """Configurar driver de Selenium."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ejecutar sin interfaz gráfica
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

@pytest.fixture
def base_url():
    """URL base de la aplicación."""
    return "http://localhost:5000"

class TestUserFlows:
    """Tests de flujos completos de usuario."""
    
    def test_homepage_loads(self, driver, base_url):
        """Test que la página principal carga correctamente."""
        driver.get(base_url)
        
        # Verificar título
        assert "Gemini AI Chatbot" in driver.title
        
        # Verificar elementos principales
        assert driver.find_element(By.TAG_NAME, "h1")
        assert driver.find_element(By.TAG_NAME, "main")
    
    def test_navigation_to_chat(self, driver, base_url):
        """Test navegación a la página de chat."""
        driver.get(base_url)
        
        # Buscar y hacer clic en enlace al chat
        chat_link = driver.find_element(By.LINK_TEXT, "Chat")
        chat_link.click()
        
        # Verificar que estamos en la página de chat
        WebDriverWait(driver, 10).until(
            EC.url_contains("/chat")
        )
        
        assert "/chat" in driver.current_url
    
    def test_chat_interface_elements(self, driver, base_url):
        """Test elementos de la interfaz de chat."""
        driver.get(f"{base_url}/chat")
        
        # Verificar elementos del chat
        message_input = driver.find_element(By.ID, "messageInput")
        send_button = driver.find_element(By.ID, "sendButton")
        chat_container = driver.find_element(By.ID, "chatContainer")
        
        assert message_input.is_displayed()
        assert send_button.is_displayed()
        assert chat_container.is_displayed()
    
    def test_send_message_flow(self, driver, base_url):
        """Test flujo completo de envío de mensaje."""
        driver.get(f"{base_url}/chat")
        
        # Encontrar elementos
        message_input = driver.find_element(By.ID, "messageInput")
        send_button = driver.find_element(By.ID, "sendButton")
        
        # Escribir mensaje
        test_message = "Hola, este es un mensaje de prueba"
        message_input.send_keys(test_message)
        
        # Enviar mensaje
        send_button.click()
        
        # Esperar respuesta (puede fallar si no hay API key)
        time.sleep(2)
        
        # Verificar que el input se limpió
        assert message_input.get_attribute("value") == ""
    
    def test_responsive_design(self, driver, base_url):
        """Test diseño responsivo."""
        driver.get(base_url)
        
        # Test desktop
        driver.set_window_size(1920, 1080)
        time.sleep(1)
        
        # Test tablet
        driver.set_window_size(768, 1024)
        time.sleep(1)
        
        # Test mobile
        driver.set_window_size(375, 667)
        time.sleep(1)
        
        # Verificar que la página sigue siendo funcional
        assert driver.find_element(By.TAG_NAME, "main").is_displayed()
    
    def test_error_handling(self, driver, base_url):
        """Test manejo de errores."""
        # Test página inexistente
        driver.get(f"{base_url}/nonexistent-page")
        
        # Debería mostrar error 404 o redirigir
        assert "404" in driver.page_source or driver.current_url == base_url
    
    def test_manifest_and_pwa(self, driver, base_url):
        """Test funcionalidad PWA."""
        driver.get(base_url)
        
        # Verificar que el manifest está presente
        manifest_link = driver.find_element(
            By.CSS_SELECTOR, 
            'link[rel="manifest"]'
        )
        assert manifest_link.get_attribute("href")
        
        # Verificar service worker
        service_worker_script = driver.find_elements(
            By.CSS_SELECTOR,
            'script[src*="sw.js"]'
        )
        # Puede o no estar presente dependiendo de la implementación
    
    def test_accessibility_basics(self, driver, base_url):
        """Test básicos de accesibilidad."""
        driver.get(base_url)
        
        # Verificar que hay elementos con alt text para imágenes
        images = driver.find_elements(By.TAG_NAME, "img")
        for img in images:
            alt_text = img.get_attribute("alt")
            assert alt_text is not None  # Puede estar vacío pero debe existir
        
        # Verificar estructura de headings
        h1_elements = driver.find_elements(By.TAG_NAME, "h1")
        assert len(h1_elements) >= 1  # Debe haber al menos un H1
        
        # Verificar que los botones tienen texto o aria-label
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for button in buttons:
            text = button.text
            aria_label = button.get_attribute("aria-label")
            assert text or aria_label  # Debe tener uno de los dos

@pytest.mark.slow
class TestPerformance:
    """Tests de rendimiento básicos."""
    
    def test_page_load_time(self, driver, base_url):
        """Test tiempo de carga de página."""
        start_time = time.time()
        driver.get(base_url)
        
        # Esperar a que la página esté completamente cargada
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        load_time = time.time() - start_time
        assert load_time < 5.0  # Debe cargar en menos de 5 segundos
    
    def test_multiple_requests(self, driver, base_url):
        """Test múltiples requests rápidas."""
        driver.get(f"{base_url}/chat")
        
        # Simular múltiples envíos rápidos
        message_input = driver.find_element(By.ID, "messageInput")
        send_button = driver.find_element(By.ID, "sendButton")
        
        for i in range(5):
            message_input.clear()
            message_input.send_keys(f"Mensaje {i}")
            send_button.click()
            time.sleep(0.5)  # Pequeña pausa entre requests
        
        # La aplicación debe seguir funcionando
        assert message_input.is_enabled()
        assert send_button.is_enabled()