"""
Tests unitarios para el servicio Gemini.
"""

import pytest
from unittest.mock import Mock, patch
from app.services.gemini_service import GeminiService


class TestGeminiService:
    """Tests para GeminiService."""

    def setup_method(self):
        """Configurar cada test."""
        self.api_key = "test_api_key_12345"

    @patch('app.services.gemini_service.genai')
    def test_init_with_valid_api_key(self, mock_genai):
        """Test inicialización con API key válida."""
        with patch('config.settings.Config.GEMINI_API_KEY', self.api_key):
            service = GeminiService()
            mock_genai.configure.assert_called_once_with(api_key=self.api_key)
            assert service.api_key == self.api_key

    def test_init_without_api_key(self):
        """Test inicialización sin API key."""
        with patch('config.settings.Config.GEMINI_API_KEY', None):
            with pytest.raises(ValueError, match="GEMINI_API_KEY no encontrada"):
                GeminiService()

    @patch('app.services.gemini_service.genai')
    def test_generate_response_success(self, mock_genai):
        """Test generación exitosa de respuesta."""
        # Mock del modelo y respuesta
        mock_response = Mock()
        mock_response.text = "Respuesta de prueba"
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        with patch('config.settings.Config.GEMINI_API_KEY', self.api_key):
            service = GeminiService()
            result = service.generate_response("Mensaje de prueba")

        assert result['success'] is True
        assert result['message'] == "Respuesta de prueba"
        assert result['cached'] is False
        assert 'response_time' in result
        assert result['model'] == 'gemini-1.5-flash'

    @patch('app.services.gemini_service.genai')
    def test_generate_response_error(self, mock_genai):
        """Test manejo de errores en generación."""
        # Mock del modelo que falla
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_genai.GenerativeModel.return_value = mock_model

        with patch('config.settings.Config.GEMINI_API_KEY', self.api_key):
            service = GeminiService()
            result = service.generate_response("Mensaje de prueba")

        assert result['success'] is False
        assert "Error temporal del servicio" in result['message']
        assert result['error_code'] == 'GEMINI_ERROR'

    @patch('app.services.gemini_service.genai')
    def test_validate_api_key_success(self, mock_genai):
        """Test validación exitosa de API key."""
        mock_response = Mock()
        mock_response.text = "Test response"
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        with patch('config.settings.Config.GEMINI_API_KEY', self.api_key):
            service = GeminiService()
            result = service.validate_api_key()

        assert result is True

    @patch('app.services.gemini_service.genai')
    def test_validate_api_key_failure(self, mock_genai):
        """Test fallo en validación de API key."""
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("Invalid API key")
        mock_genai.GenerativeModel.return_value = mock_model

        with patch('config.settings.Config.GEMINI_API_KEY', self.api_key):
            service = GeminiService()
            result = service.validate_api_key()

        assert result is False
