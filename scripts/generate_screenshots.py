#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📸 AUTOMATED SCREENSHOT GENERATOR
================================

Creates high-quality screenshots for Chrome Web Store submission.
Uses Selenium WebDriver to capture different states of the extension.
"""

import time
from pathlib import Path

import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class ScreenshotGenerator:
    """Automated screenshot generator for Chrome extension."""

    def __init__(self, extension_path: str, output_dir: str = "chrome_extension/screenshots"):
        self.extension_path = Path(extension_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.driver = None

    def setup_chrome_driver(self):
        """Setup Chrome driver with extension loaded."""
        chrome_options = Options()

        # Load the extension
        chrome_options.add_argument(f"--load-extension={self.extension_path}")
        chrome_options.add_argument("--disable-extensions-except=" + str(self.extension_path))
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")

        # Set window size for consistent screenshots
        chrome_options.add_argument("--window-size=1280,800")

        # Optional: Run headless (comment out to see browser)
        # chrome_options.add_argument("--headless")

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_window_size(1280, 800)
            return True
        except Exception as e:
            print(f"❌ Failed to setup Chrome driver: {e}")
            print("💡 Make sure Chrome and ChromeDriver are installed")
            return False

    def wait_for_server(self, url: str = "http://localhost:5000", timeout: int = 30):
        """Wait for the Flask server to be ready."""
        print(f"⏳ Waiting for server at {url}...")

        for _ in range(timeout):
            try:
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    print("✅ Server is ready!")
                    return True
            except requests.exceptions.RequestException:
                pass

            time.sleep(1)

        print(f"❌ Server not responding after {timeout} seconds")
        return False

    def take_screenshot(self, filename: str, description: str = ""):
        """Take a screenshot and save it."""
        if not self.driver:
            print("❌ Chrome driver not initialized")
            return False

        try:
            # Wait a moment for page to load
            time.sleep(2)

            # Take screenshot
            screenshot_path = self.output_dir / f"{filename}.png"
            success = self.driver.save_screenshot(str(screenshot_path))

            if success:
                # Resize to Chrome Web Store requirements (1280x800)
                self.resize_screenshot(screenshot_path, (1280, 800))
                print(f"📸 Screenshot saved: {filename}.png")
                if description:
                    print(f"   Description: {description}")
                return True
            else:
                print(f"❌ Failed to save screenshot: {filename}")
                return False

        except Exception as e:
            print(f"❌ Error taking screenshot {filename}: {e}")
            return False

    def resize_screenshot(self, image_path: Path, target_size: tuple):
        """Resize screenshot to target dimensions."""
        try:
            with Image.open(image_path) as img:
                # Resize maintaining aspect ratio
                img_resized = img.resize(target_size, Image.Resampling.LANCZOS)
                img_resized.save(image_path, "PNG", quality=95)
        except Exception as e:
            print(f"⚠️ Could not resize {image_path}: {e}")

    def capture_main_interface(self):
        """Capture the main chat interface."""
        print("\n📸 Capturing main interface...")

        # Navigate to the main application
        self.driver.get("http://localhost:5000")

        # Wait for the page to load
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Take screenshot
        self.take_screenshot("01_main_interface", "Main chat interface with futuristic neural background")

    def capture_chat_functionality(self):
        """Capture chat in action."""
        print("\n📸 Capturing chat functionality...")

        # Navigate to chat page
        self.driver.get("http://localhost:5000/chat")

        # Wait for chat to load
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "messageInput")))

        # Simulate typing a message
        try:
            message_input = self.driver.find_element(By.ID, "messageInput")
            message_input.click()
            message_input.send_keys("Hello! Can you help me with document analysis?")
            time.sleep(1)

            self.take_screenshot("02_chat_interaction", "User typing a message in the chat interface")

            # Simulate sending the message (if send button exists)
            try:
                send_button = self.driver.find_element(By.ID, "sendButton")
                send_button.click()
                time.sleep(3)  # Wait for response

                self.take_screenshot(
                    "03_chat_response",
                    "AI response with formatted text and neural animations",
                )
            except Exception:
                print("⚠️ Send button not found, skipping response screenshot")

        except Exception as e:
            print(f"⚠️ Could not interact with chat: {e}")

    def capture_voice_controls(self):
        """Capture voice control features."""
        print("\n📸 Capturing voice controls...")

        # Go to chat page if not already there
        if "chat" not in self.driver.current_url:
            self.driver.get("http://localhost:5000/chat")
            time.sleep(2)

        try:
            # Look for voice control button
            voice_buttons = self.driver.find_elements(By.CSS_SELECTOR, "[title*='voice'], [title*='Voice'], .action-btn")

            if voice_buttons:
                # Highlight voice controls (add temporary styling)
                self.driver.execute_script("""
                    const voiceButtons = document.querySelectorAll('.action-btn');
                    voiceButtons.forEach(btn => {
                        if (btn.textContent.includes('Voz') || btn.textContent.includes('Voice')) {
                            btn.style.border = '3px solid #00ff88';
                            btn.style.boxShadow = '0 0 15px rgba(0,255,136,0.6)';
                        }
                    });
                """)

                time.sleep(1)

                self.take_screenshot(
                    "04_voice_controls",
                    "Voice control interface with play/pause functionality",
                )

        except Exception as e:
            print(f"⚠️ Could not capture voice controls: {e}")

    def capture_file_upload(self):
        """Capture file upload functionality."""
        print("\n📸 Capturing file upload...")

        try:
            # Highlight file upload button
            self.driver.execute_script("""
                const fileButtons = document.querySelectorAll('.action-btn');
                fileButtons.forEach(btn => {
                    if (btn.textContent.includes('Archivo') || btn.textContent.includes('File')) {
                        btn.style.border = '3px solid #ff6b9d';
                        btn.style.boxShadow = '0 0 15px rgba(255,107,157,0.6)';
                    }
                });
            """)

            time.sleep(1)

            self.take_screenshot("05_file_upload", "Document upload interface for AI analysis")

        except Exception as e:
            print(f"⚠️ Could not capture file upload: {e}")

    def capture_responsive_design(self):
        """Capture responsive design at different screen sizes."""
        print("\n📸 Capturing responsive design...")

        # Mobile view
        self.driver.set_window_size(375, 667)  # iPhone size
        time.sleep(2)

        self.take_screenshot("06_mobile_responsive", "Mobile responsive design on smartphone")

        # Tablet view
        self.driver.set_window_size(768, 1024)  # iPad size
        time.sleep(2)

        self.take_screenshot("07_tablet_responsive", "Tablet responsive design on iPad")

        # Restore desktop size
        self.driver.set_window_size(1280, 800)
        time.sleep(1)

    def capture_extension_popup(self):
        """Capture the Chrome extension popup."""
        print("\n📸 Capturing extension popup...")

        try:
            # Get extension ID (this would need to be determined dynamically)
            # For now, we'll try to access the extension through chrome://extensions
            self.driver.get("chrome://extensions/")
            time.sleep(2)

            self.take_screenshot("08_extension_popup", "Chrome extension popup interface")

        except Exception as e:
            print(f"⚠️ Could not capture extension popup: {e}")

    def generate_all_screenshots(self):
        """Generate all required screenshots."""
        print("🚀 Starting automated screenshot generation...")

        # Check if server is running
        if not self.wait_for_server():
            print("❌ Flask server is not running. Please start it first.")
            return False

        # Setup Chrome driver
        if not self.setup_chrome_driver():
            return False

        try:
            # Generate screenshots
            self.capture_main_interface()
            self.capture_chat_functionality()
            self.capture_voice_controls()
            self.capture_file_upload()
            self.capture_responsive_design()
            self.capture_extension_popup()

            print("\n✅ All screenshots generated successfully!")
            print(f"📁 Screenshots saved to: {self.output_dir}")

            # List generated files
            screenshots = list(self.output_dir.glob("*.png"))
            print(f"\n📸 Generated {len(screenshots)} screenshots:")
            for screenshot in sorted(screenshots):
                print(f"   • {screenshot.name}")

            return True

        except Exception as e:
            print(f"❌ Error during screenshot generation: {e}")
            return False

        finally:
            if self.driver:
                self.driver.quit()


def main():
    """Main function."""
    project_root = Path(__file__).parent.parent
    extension_path = project_root / "chrome_extension"
    output_dir = project_root / "chrome_extension" / "screenshots"

    generator = ScreenshotGenerator(str(extension_path), str(output_dir))
    success = generator.generate_all_screenshots()

    if success:
        print("\n🎉 Screenshot generation completed!")
        print("\nNext steps:")
        print("1. ✅ Review generated screenshots")
        print("2. 🎨 Edit/enhance screenshots if needed")
        print("3. 📤 Upload to Chrome Web Store listing")
        print("4. 🚀 Submit extension for review")
    else:
        print("\n❌ Screenshot generation failed")
        print("💡 Make sure:")
        print("   • Flask server is running (python run_development.py)")
        print("   • Chrome and ChromeDriver are installed")
        print("   • Extension files are valid")

    return 0 if success else 1


if __name__ == "__main__":
    # Note: This script requires selenium and PIL
    # Install with: pip install selenium pillow

    try:
        exit(main())
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("💡 Install required packages:")
        print("   pip install selenium pillow")
        exit(1)
