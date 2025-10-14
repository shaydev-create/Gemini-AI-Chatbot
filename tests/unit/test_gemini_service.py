"""
Tests unitarios completos para el servicio Gemini.
"""

import os
from unittest.mock import MagicMock, patch

import pytest
from app.services.gemini_service import GeminiService


class TestGeminiService:
    """Tests completos para GeminiService."""

    def setup_method(self):
        """Configurar cada test."""
        self.api_key = "test_api_key_12345"
        # Limpiar cualquier variable de entorno previa
        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]
        if "GOOGLE_API_KEY" in os.environ:
            del os.environ["GOOGLE_API_KEY"]

    @patch("app.services.gemini_service.genai")
    def test_initialization_with_valid_api_key(self, mock_genai):
        """Test inicialización con API key válida."""
        # Configurar variable de entorno
        os.environ["GEMINI_API_KEY"] = self.api_key

        # Inicializar el servicio (esto debería funcionar)
        service = GeminiService()

        mock_genai.configure.assert_called_once_with(api_key=self.api_key)
        mock_genai.GenerativeModel.assert_called_once()
        assert service.model is not None

    @patch("app.services.gemini_service.genai")
    def test_initialization_with_google_api_key(self, mock_genai):
        """Test inicialización con GOOGLE_API_KEY como alternativa."""
        # Configurar variable de entorno alternativa
        os.environ["GOOGLE_API_KEY"] = self.api_key

        # Inicializar el servicio (esto debería funcionar)
        service = GeminiService()

        mock_genai.configure.assert_called_once_with(api_key=self.api_key)
        mock_genai.GenerativeModel.assert_called_once()
        assert service.model is not None

    def test_initialization_without_api_key(self):
        """Test inicialización sin API key."""
        # Asegurarse de que no hay API key en el entorno
        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]
        if "GOOGLE_API_KEY" in os.environ:
            del os.environ["GOOGLE_API_KEY"]

        # Debería lanzar ValueError
        with pytest.raises(
            ValueError, match="GEMINI_API_KEY no encontrada en las variables de entorno"
        ):
            GeminiService()

    @patch("app.services.gemini_service.genai")
    @patch("app.services.gemini_service.logger")
    def test_generate_response_text_only(self, mock_logger, mock_genai):
        """Test generación de respuesta solo texto."""
        # Configurar mocks
        os.environ["GEMINI_API_KEY"] = self.api_key
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Respuesta de prueba"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        # Ejecutar
        service = GeminiService()
        result = service.generate_response(message="Hola", language="es")

        # Verificar
        mock_model.generate_content.assert_called_once()
        assert result == "Respuesta de prueba"
        mock_logger.info.assert_called()

    @patch("app.services.gemini_service.genai")
    @patch("app.services.gemini_service.logger")
    def test_generate_response_empty_message(self, mock_logger, mock_genai):
        """Test de mensaje vacío."""
        # Configurar mocks
        os.environ["GEMINI_API_KEY"] = self.api_key
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model

        # Ejecutar
        service = GeminiService()
        result = service.generate_response(message="", language="es")

        # Verificar
        assert result == "Por favor, proporciona un mensaje para procesar."
        mock_model.generate_content.assert_not_called()

    @patch("app.services.gemini_service.genai")
    @patch("app.services.gemini_service.logger")
    def test_generate_response_english_language(self, mock_logger, mock_genai):
        """Test de generación en inglés."""
        # Configurar mocks
        os.environ["GEMINI_API_KEY"] = self.api_key
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Test response"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        # Ejecutar
        service = GeminiService()
        result = service.generate_response(message="Hello", language="en")

        # Verificar
        call_args = mock_model.generate_content.call_args[0][0]
        assert "IMPORTANT: Please respond only in English" in call_args
        assert result == "Test response"

    @patch("app.services.gemini_service.genai")
    @patch("app.services.gemini_service.logger")
    def test_generate_response_api_error(self, mock_logger, mock_genai):
        """Test de error de API."""
        # Configurar mocks
        os.environ["GEMINI_API_KEY"] = self.api_key
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API error 429")
        mock_genai.GenerativeModel.return_value = mock_model

        # Ejecutar
        service = GeminiService()
        result = service.generate_response(message="Test error")

        # Verificar
        assert "Has excedido el límite" in result
        mock_logger.error.assert_called()

    @patch("app.services.gemini_service.genai")
    def test_validate_api_key_success(self, mock_genai):
        """Test de validación de API key exitosa."""
        # Configurar mocks
        os.environ["GEMINI_API_KEY"] = self.api_key
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        # Ejecutar
        service = GeminiService()
        result = service.validate_api_key()

        # Verificar
        assert result is True
        mock_model.generate_content.assert_called_once_with("Test")

    @patch("app.services.gemini_service.genai")
    @patch("app.services.gemini_service.logger")
    def test_validate_api_key_failure(self, mock_logger, mock_genai):
        """Test de validación de API key fallida."""
        # Configurar mocks
        os.environ["GEMINI_API_KEY"] = self.api_key
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("Invalid API key")
        mock_genai.GenerativeModel.return_value = mock_model

        # Ejecutar
        service = GeminiService()
        result = service.validate_api_key()

        # Verificar
        assert result is False
        mock_logger.error.assert_called()

    @patch("app.services.gemini_service.genai")
    @patch("app.services.gemini_service.logger")
    def test_generate_response_using_prompt_param(self, mock_logger, mock_genai):
        """Test usando parámetro prompt en lugar de message."""
        # Configurar mocks
        os.environ["GEMINI_API_KEY"] = self.api_key
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Respuesta desde prompt"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        # Ejecutar
        service = GeminiService()
        result = service.generate_response(prompt="Test prompt")

        # Verificar
        mock_model.generate_content.assert_called_once()
        assert result == "Respuesta desde prompt"

    @patch("app.services.gemini_service.genai")
    @patch("app.services.gemini_service.logger")
    def test_generate_response_quota_error(self, mock_logger, mock_genai):
        """Test de error de cuota específico."""
        # Configurar mocks
        os.environ["GEMINI_API_KEY"] = self.api_key
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("quota exceeded")
        mock_genai.GenerativeModel.return_value = mock_model

        # Ejecutar
        service = GeminiService()
        result = service.generate_response(message="Test quota")

        # Verificar
        assert "Has excedido el límite" in result

    @patch("app.services.gemini_service.genai")
    @patch("app.services.gemini_service.logger")
    def test_generate_response_invalid_api_key_error(self, mock_logger, mock_genai):
        """Test de error de API key inválida."""
        # Configurar mocks
        os.environ["GEMINI_API_KEY"] = self.api_key
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API_KEY_INVALID")
        mock_genai.GenerativeModel.return_value = mock_model

        # Ejecutar
        service = GeminiService()
        result = service.generate_response(message="Test invalid key")

        # Verificar
        assert "API key inválida" in result
