"""
Tests unitarios para el servicio Gemini.
"""

from unittest.mock import Mock, patch

from app.services.gemini_service import GeminiService


class TestGeminiService:
    """Tests para GeminiService."""

    def setup_method(self):
        """Configurar cada test."""
        self.api_key = "test_api_key_12345"
        # Reiniciar el servicio antes de cada test
        GeminiService().model = None

    @patch("app.services.GeminiService().Config")
    @patch("app.services.GeminiService().genai")
    def test_init_app_with_valid_api_key(self, mock_genai, mock_config):
        """Test inicialización con API key válida."""
        # Configuramos el mock para que devuelva la API key
        mock_config.GEMINI_API_KEY = self.api_key
        mock_config.SAFETY_SETTINGS = {}
        mock_config.GENERATION_CONFIG = {}

        mock_app = Mock()  # El mock de la app ya no necesita el diccionario de config

        # Usamos el objeto singleton importado
        GeminiService().init_app(mock_app)

        mock_genai.configure.assert_called_once_with(api_key=self.api_key)
        mock_genai.GenerativeModel.assert_called_once()
        assert GeminiService().model is not None

    @patch("app.services.GeminiService().Config")
    @patch("app.services.GeminiService().genai")
    def test_init_app_without_api_key(self, mock_genai, mock_config):
        """Test inicialización sin API key."""
        # Configuramos el mock para que no devuelva API key
        mock_config.GEMINI_API_KEY = None

        mock_app = Mock()

        GeminiService().init_app(mock_app)

        mock_genai.configure.assert_not_called()
        assert GeminiService().model is None
