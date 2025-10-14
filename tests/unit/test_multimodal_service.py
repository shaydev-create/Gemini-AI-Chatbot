"""
Tests unitarios completos para el servicio multimodal.
"""

import asyncio
import unittest
from unittest.mock import MagicMock, mock_open, patch

from app.services.multimodal_service import MultimodalService


class TestMultimodalService(unittest.TestCase):
    def setUp(self):
        """Configurar cada test."""
        self.mock_client = MagicMock()
        self.mock_client.initialized = True
        self.service = MultimodalService(self.mock_client)
    
    def run_async(self, coro):
        """Ejecutar una corutina en el bucle de eventos."""
        return asyncio.run(coro)

    def test_init_success(self):
        """Test successful initialization of MultimodalService."""
        service = MultimodalService(self.mock_client)
        self.assertIsNotNone(service)
        self.assertEqual(service.client, self.mock_client)

    def test_init_failure_without_client(self):
        """Test initialization failure when no client is provided."""
        with self.assertRaises(ValueError) as context:
            MultimodalService(None)
        self.assertIn(
            "El VertexAIClient debe ser proporcionado y estar inicializado",
            str(context.exception),
        )

    def test_init_failure_with_uninitialized_client(self):
        """Test initialization failure when client is not initialized."""
        mock_client = MagicMock()
        mock_client.initialized = False

        with self.assertRaises(ValueError) as context:
            MultimodalService(mock_client)
        self.assertIn(
            "El VertexAIClient debe ser proporcionado y estar inicializado",
            str(context.exception),
        )

    def test_generate_response_text_only(self):
        """Test generating a response with only a text message (should fail)."""
        # Configurar un mock que debería NO ser llamado
        async def mock_generate_response(*args, **kwargs):
            self.fail("El cliente no debería ser llamado cuando no hay imágenes válidas")
        
        self.mock_client.generate_response = mock_generate_response
        
        response = self.run_async(self.service.generate_response("Hello", []))

        self.assertEqual(
            response,
            "Por favor, proporciona al menos una imagen válida para el análisis."
        )

    def test_generate_response_with_base64_image(self):
        """Test generating a response with a base64 encoded image."""
        async def mock_generate_response(*args, **kwargs):
            return {"response": "Image received."}
        
        self.mock_client.generate_response = mock_generate_response

        # A simple 1x1 red pixel gif
        base64_image = "data:image/gif;base64,R0lGODlhAQABAIABAP8AAP///yH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="
        response = self.run_async(self.service.generate_response("What is this?", [base64_image]))

        self.assertEqual(response, "Image received.")

    @patch("pathlib.Path.exists", return_value=True)
    def test_generate_response_with_image_path(self, mock_exists):
        """Test generating a response with an image file path."""
        async def mock_generate_response(*args, **kwargs):
            return {"response": "Image from path received."}
        
        self.mock_client.generate_response = mock_generate_response

        image_path = "test_image.png"
        response = self.run_async(self.service.generate_response("Analyze this image.", [image_path]))

        self.assertEqual(response, "Image from path received.")
        mock_exists.assert_called_once()

    @patch("pathlib.Path.exists", return_value=False)
    def test_generate_response_with_nonexistent_image_path(self, mock_exists):
        """Test generating a response with a non-existent image path."""
        image_path = "nonexistent.jpg"
        response = self.run_async(self.service.generate_response("Analyze this.", [image_path]))

        self.assertEqual(
            response,
            "Por favor, proporciona al menos una imagen válida para el análisis.",
        )
        mock_exists.assert_called_once()
        self.mock_client.generate_response.assert_not_called()

    def test_generate_response_api_error(self):
        """Test handling of a generic API error."""
        async def mock_generate_response(*args, **kwargs):
            raise Exception("Generic API Error")
        
        self.mock_client.generate_response = mock_generate_response

        response = self.run_async(self.service.generate_response(
            "What is this?",
            [
                "data:image/gif;base64,R0lGODlhAQABAIABAP8AAP///yH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="
            ],
        ))

        self.assertIn(
            "Lo siento, ha ocurrido un error al procesar tu solicitud de imágenes",
            response,
        )

    def test_generate_response_no_valid_images(self):
        """Test handling when no valid images are provided."""
        response = self.run_async(self.service.generate_response("Analyze this.", ["invalid_path.jpg"]))

        self.assertEqual(
            response,
            "Por favor, proporciona al menos una imagen válida para el análisis.",
        )
        self.mock_client.generate_response.assert_not_called()

    def test_generate_response_multiple_images(self):
        """Test generating a response with multiple images."""
        async def mock_generate_response(*args, **kwargs):
            return {"response": "Multiple images received."}
        
        self.mock_client.generate_response = mock_generate_response

        base64_image1 = "data:image/gif;base64,R0lGODlhAQABAIABAP8AAP///yH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="
        base64_image2 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
        response = self.run_async(self.service.generate_response(
            "Analyze these images.", [base64_image1, base64_image2]
        ))

        self.assertEqual(response, "Multiple images received.")

    def test_generate_response_with_different_model_type(self):
        """Test generating a response with different model type."""
        async def mock_generate_response(*args, **kwargs):
            return {"response": "Vision model response."}
        
        self.mock_client.generate_response = mock_generate_response

        base64_image = "data:image/gif;base64,R0lGODlhAQABAIABAP8AAP///yH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="
        response = self.run_async(self.service.generate_response(
            "Analyze this.", [base64_image], model_type="vision"
        ))

        self.assertEqual(response, "Vision model response.")

    def test_generate_response_mixed_valid_invalid_images(self):
        """Test generating a response with mix of valid and invalid images."""
        async def mock_generate_response(*args, **kwargs):
            return {"response": "Mixed images response."}
        
        self.mock_client.generate_response = mock_generate_response

        base64_image = "data:image/gif;base64,R0lGODlhAQABAIABAP8AAP///yH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="
        response = self.run_async(self.service.generate_response(
            "Analyze these.", ["invalid.jpg", base64_image, "another_invalid.png"]
        ))

        self.assertEqual(response, "Mixed images response.")

    @patch("app.services.multimodal_service.logger")
    def test_generate_response_logging_on_success(self, mock_logger):
        """Test that success is logged properly."""
        async def mock_generate_response(*args, **kwargs):
            return {"response": "Success response."}
        
        self.mock_client.generate_response = mock_generate_response

        base64_image = "data:image/gif;base64,R0lGODlhAQABAIABAP8AAP///yH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="
        self.run_async(self.service.generate_response("Test logging.", [base64_image]))

        mock_logger.info.assert_called()

    @patch("app.services.multimodal_service.logger")
    def test_generate_response_logging_on_error(self, mock_logger):
        """Test that errors are logged properly."""
        async def mock_generate_response(*args, **kwargs):
            raise Exception("Test error")
        
        self.mock_client.generate_response = mock_generate_response

        base64_image = "data:image/gif;base64,R0lGODlhAQABAIABAP8AAP///yH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="
        self.run_async(self.service.generate_response("Test error logging.", [base64_image]))

        mock_logger.exception.assert_called()

    def test_generate_response_empty_prompt(self):
        """Test generating a response with empty prompt."""
        async def mock_generate_response(*args, **kwargs):
            return {"response": "Empty prompt response."}
        
        self.mock_client.generate_response = mock_generate_response

        base64_image = "data:image/gif;base64,R0lGODlhAQABAIABAP8AAP///yH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="
        response = self.run_async(self.service.generate_response("", [base64_image]))

        self.assertEqual(response, "Empty prompt response.")


if __name__ == "__main__":
    unittest.main()
