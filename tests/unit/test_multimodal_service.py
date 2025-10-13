import base64
import os
import unittest
from unittest.mock import MagicMock, mock_open, patch

from app.config.settings import Config
from app.services.multimodal_service import MultimodalService


class TestMultimodalService(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test."""
        # Clear the singleton instance before each test
        global _multimodal_service_instance
        _multimodal_service_instance = None

    @patch("app.services.multimodal_service.genai")
    def test_init_success(self, mock_genai):
        """Test successful initialization of MultimodalService."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            Config.GEMINI_API_KEY = "test-key"
            service = MultimodalService()
            self.assertIsNotNone(service)
            mock_genai.configure.assert_called_once_with(api_key="test-key")
            mock_genai.GenerativeModel.assert_called_once()

    def test_init_no_api_key(self):
        """Test initialization failure when GEMINI_API_KEY is not set."""
        with patch.dict(os.environ, {}, clear=True):
            Config.GEMINI_API_KEY = None
            with self.assertRaises(ValueError) as context:
                MultimodalService()
            self.assertIn("GEMINI_API_KEY no encontrada", str(context.exception))

    @patch("app.services.multimodal_service.genai")
    def test_generate_response_text_only(self, mock_genai):
        """Test generating a response with only a text message."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            Config.GEMINI_API_KEY = "test-key"

            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_model.generate_content.return_value.text = "Hello, world!"

            service = MultimodalService()
            response = service.generate_response("Hello")

            self.assertTrue(response["success"])
            self.assertEqual(response["message"], "Hello, world!")
            mock_model.generate_content.assert_called_once()
            call_args = mock_model.generate_content.call_args[0][0]
            self.assertEqual(len(call_args), 1)
            self.assertEqual(call_args[0], {"text": "Hello"})

    @patch("app.services.multimodal_service.genai")
    def test_generate_response_with_base64_image(self, mock_genai):
        """Test generating a response with a base64 encoded image."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            Config.GEMINI_API_KEY = "test-key"

            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_model.generate_content.return_value.text = "Image received."

            service = MultimodalService()
            # A simple 1x1 red pixel gif
            base64_image = "data:image/gif;base64,R0lGODlhAQABAIABAP8AAP///yH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="
            response = service.generate_response("What is this?", images=[base64_image])

            self.assertTrue(response["success"])
            self.assertEqual(response["message"], "Image received.")
            mock_model.generate_content.assert_called_once()
            call_args = mock_model.generate_content.call_args[0][0]
            self.assertEqual(len(call_args), 2)
            self.assertEqual(call_args[0], {"text": "What is this?"})
            self.assertIn("inline_data", call_args[1])
            self.assertEqual(
                call_args[1]["inline_data"]["mime_type"], "image/jpeg"
            )  # Default mime type for base64

    @patch("app.services.multimodal_service.os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data=b"imagedata")
    @patch("app.services.multimodal_service.genai")
    def test_generate_response_with_image_path(
        self, mock_genai, mock_file, mock_exists
    ):
        """Test generating a response with an image file path."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            Config.GEMINI_API_KEY = "test-key"

            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_model.generate_content.return_value.text = "Image from path received."

            service = MultimodalService()
            image_path = "test_image.png"
            response = service.generate_response(
                "Analyze this image.", images=[image_path]
            )

            self.assertTrue(response["success"])
            self.assertEqual(response["message"], "Image from path received.")
            mock_exists.assert_called_once_with(image_path)
            mock_file.assert_called_once_with(image_path, "rb")
            mock_model.generate_content.assert_called_once()
            call_args = mock_model.generate_content.call_args[0][0]
            self.assertEqual(len(call_args), 2)
            self.assertEqual(call_args[1]["inline_data"]["mime_type"], "image/png")
            self.assertEqual(
                base64.b64decode(call_args[1]["inline_data"]["data"]), b"imagedata"
            )

    @patch("app.services.multimodal_service.os.path.exists", return_value=False)
    @patch("app.services.multimodal_service.genai")
    def test_generate_response_with_nonexistent_image_path(
        self, mock_genai, mock_exists
    ):
        """Test generating a response with a non-existent image path."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            Config.GEMINI_API_KEY = "test-key"

            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_model.generate_content.return_value.text = "No image found."

            service = MultimodalService()
            image_path = "nonexistent.jpg"
            response = service.generate_response("Analyze this.", images=[image_path])

            self.assertTrue(response["success"])
            self.assertEqual(response["message"], "No image found.")
            mock_exists.assert_called_once_with(image_path)
            # Check that only the text part was sent
            call_args = mock_model.generate_content.call_args[0][0]
            self.assertEqual(len(call_args), 1)
            self.assertEqual(call_args[0], {"text": "Analyze this."})

    @patch("app.services.multimodal_service.genai")
    def test_generate_response_api_error(self, mock_genai):
        """Test handling of a generic API error."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            Config.GEMINI_API_KEY = "test-key"

            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_model.generate_content.side_effect = Exception("Generic API Error")

            service = MultimodalService()
            response = service.generate_response("Hello")

            self.assertFalse(response["success"])
            self.assertEqual(response["error_code"], "GEMINI_MULTIMODAL_ERROR")
            self.assertIn("Error temporal del servicio multimodal", response["message"])

    @patch("app.services.multimodal_service.genai")
    def test_generate_response_quota_error(self, mock_genai):
        """Test handling of a quota exceeded error."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            Config.GEMINI_API_KEY = "test-key"

            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_model.generate_content.side_effect = Exception("429 ResourceExhausted")

            service = MultimodalService()
            response = service.generate_response("Hello")

            self.assertFalse(response["success"])
            self.assertEqual(response["error_code"], "QUOTA_EXCEEDED")
            self.assertIn("Has excedido el límite de la API", response["message"])

    @patch("app.services.multimodal_service.genai")
    def test_get_multimodal_service_singleton(self, mock_genai):
        """Test that get_multimodal_service returns a singleton instance."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            Config.GEMINI_API_KEY = "test-key"

            # To properly test the singleton, we need to reset the global instance
            # in the original module, not a copy.
            with patch(
                "app.services.multimodal_service._multimodal_service_instance", None
            ):
                service1 = MultimodalService()
                service2 = MultimodalService()
                self.assertIs(service1, service2)
                # Check that MultimodalService was only instantiated once
                mock_genai.GenerativeModel.assert_called_once()


if __name__ == "__main__":
    unittest.main()
