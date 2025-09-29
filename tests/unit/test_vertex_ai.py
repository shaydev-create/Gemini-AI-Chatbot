"""Tests unitarios para Vertex AI."""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from src.config.vertex_ai import VertexAIConfig
from src.config.vertex_client import VertexAIClient


class TestVertexAIConfig:
    """Tests para la configuración de Vertex AI."""
    
    @patch.dict(os.environ, {'GOOGLE_CLOUD_PROJECT_ID': 'test-project', 'GOOGLE_CLOUD_LOCATION': 'us-central1', 'VERTEX_AI_ENABLED': 'true', 'VERTEX_AI_MAX_DAILY_COST': '10.0'})`n    def test_init_with_valid_config(self):
        """Test inicialización con configuración válida."""
        config = VertexAIConfig()
        
        assert config.project_id == "test-project"
        assert config.location == "us-central1"
        assert config.model == "gemini-1.5-pro"
        assert config.max_daily_cost == 10.0
        assert config.enabled is True
    
    def test_init_with_invalid_project_id(self):
        """Test inicialización con project_id inválido."""
        with pytest.raises(ValueError, match="Project ID no puede estar vacío"):
            VertexAIConfig()
    
    def test_init_with_invalid_location(self):
        """Test inicialización con location inválida."""
        with pytest.raises(ValueError, match="Location no puede estar vacía"):
            VertexAIConfig()
    
    def test_get_model_info_valid_model(self):
        """Test obtener información de modelo válido."""
        config = VertexAIConfig()
        
        model_info = config.get_model_info("gemini-1.5-pro")
        
        assert model_info is not None
        assert model_info["type"] == "pro"
        assert "input_cost_per_1k" in model_info
        assert "output_cost_per_1k" in model_info
    
    def test_get_model_info_invalid_model(self):
        """Test obtener información de modelo inválido."""
        config = VertexAIConfig()
        
        model_info = config.get_model_info("modelo-inexistente")
        assert model_info is None
    
    def test_estimate_cost(self):
        """Test estimación de costos."""
        config = VertexAIConfig()
        
        cost = config.estimate_cost("gemini-1.5-flash", 1000, 500)
        assert isinstance(cost, float)
        assert cost > 0
    
    def test_get_endpoint_url(self):
        """Test obtener URL del endpoint."""
        config = VertexAIConfig()
        
        url = config.get_endpoint_url("gemini-1.5-pro")
        expected = "https://us-central1-aiplatform.googleapis.com/v1/projects/test-project/locations/us-central1/publishers/google/models/gemini-1.5-pro:generateContent"
        assert url == expected


class TestVertexAIClient:
    """Tests para el cliente de Vertex AI."""
    
    @pytest.fixture
    def mock_config(self):
        """Fixture para configuración mock."""
        return VertexAIConfig()
    
    @pytest.fixture
    def mock_client(self, mock_config):
        """Fixture para cliente mock."""
        with patch('src.config.vertex_client.vertexai') as mock_vertexai:
            client = VertexAIClient(mock_config)
            return client
    
    def test_init_success(self, mock_config):
        """Test inicialización exitosa del cliente."""
        with patch('src.config.vertex_client.vertexai') as mock_vertexai:
            client = VertexAIClient(mock_config)
            
            assert client.config == mock_config
            assert client.vertex_available is True
            mock_vertexai.init.assert_called_once()
    
    def test_init_vertex_unavailable(self, mock_config):
        """Test inicialización cuando Vertex AI no está disponible."""
        with patch('src.config.vertex_client.vertexai', side_effect=ImportError()):
            client = VertexAIClient(mock_config)
            
            assert client.vertex_available is False
            assert client.model is None
    
    @patch('src.config.vertex_client.genai')
    def test_init_gemini_fallback(self, mock_genai, mock_config):
        """Test inicialización del fallback de Gemini."""
        with patch('src.config.vertex_client.vertexai', side_effect=ImportError()):
            with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test-key'}):
                client = VertexAIClient(mock_config)
                
                mock_genai.configure.assert_called_once_with(api_key='test-key')
    
    def test_estimate_tokens(self, mock_client):
        """Test estimación de tokens."""
        text = "Este es un texto de prueba para estimar tokens."
        
        input_tokens, output_tokens = mock_client._estimate_tokens(text)
        
        assert isinstance(input_tokens, int)
        assert isinstance(output_tokens, int)
        assert input_tokens > 0
        assert output_tokens > 0
    
    def test_check_daily_limits_under_limit(self, mock_client):
        """Test verificación de límites diarios bajo el límite."""
        mock_client.daily_cost = 5.0
        mock_client.daily_requests = 50
        
        result = mock_client._check_daily_limits(2.0)
        assert result is True
    
    def test_check_daily_limits_over_cost_limit(self, mock_client):
        """Test verificación de límites diarios sobre el límite de costo."""
        mock_client.daily_cost = 9.0
        mock_client.daily_requests = 50
        
        result = mock_client._check_daily_limits(2.0)
        assert result is False
    
    def test_check_daily_limits_over_request_limit(self, mock_client):
        """Test verificación de límites diarios sobre el límite de requests."""
        mock_client.daily_cost = 5.0
        mock_client.daily_requests = 1000
        
        result = mock_client._check_daily_limits(1.0)
        assert result is False
    
    def test_update_usage_metrics(self, mock_client):
        """Test actualización de métricas de uso."""
        initial_cost = mock_client.daily_cost
        initial_requests = mock_client.daily_requests
        
        mock_client._update_usage_metrics(2.5, 100, 50)
        
        assert mock_client.daily_cost == initial_cost + 2.5
        assert mock_client.daily_requests == initial_requests + 1
        assert mock_client.total_input_tokens == 100
        assert mock_client.total_output_tokens == 50
    
    @patch('src.config.vertex_client.requests.post')
    def test_generate_response_vertex_success(self, mock_post, mock_client):
        """Test generación de respuesta exitosa con Vertex AI."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{'text': 'Respuesta de prueba'}]
                }
            }],
            'usageMetadata': {
                'promptTokenCount': 10,
                'candidatesTokenCount': 5
            }
        }
        mock_post.return_value = mock_response
        
        # Mock auth
        with patch('src.config.vertex_client.default') as mock_auth:
            mock_credentials = Mock()
            mock_auth.return_value = (mock_credentials, "test-project")
            
            result = mock_client.generate_response("Test prompt")
            
            assert result['success'] is True
            assert result['response'] == 'Respuesta de prueba'
            assert result['source'] == 'vertex_ai'
            assert result['tokens_used'] == 15
    
    @patch('src.config.vertex_client.genai')
    def test_generate_response_gemini_fallback(self, mock_genai, mock_client):
        """Test fallback a Gemini API."""
        # Simular fallo de Vertex AI
        mock_client.vertex_available = False
        
        # Mock Gemini response
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "Respuesta de Gemini"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        result = mock_client.generate_response("Test prompt")
        
        assert result['success'] is True
        assert result['response'] == 'Respuesta de Gemini'
        assert result['source'] == 'gemini_api'
    
    def test_get_health_status_healthy(self, mock_client):
        """Test estado de salud cuando todo está bien."""
        mock_client.vertex_available = True
        mock_client.daily_cost = 5.0
        mock_client.daily_requests = 50
        
        status = mock_client.get_health_status()
        
        assert status['vertex_ai_available'] is True
        assert status['gemini_fallback_available'] is True
        assert status['daily_cost_status'] == 'OK'
        assert status['daily_requests_status'] == 'OK'
        assert status['overall_status'] == 'healthy'
    
    def test_get_health_status_cost_warning(self, mock_client):
        """Test estado de salud con advertencia de costo."""
        mock_client.vertex_available = True
        mock_client.daily_cost = 8.5  # 85% del límite
        mock_client.daily_requests = 50
        
        status = mock_client.get_health_status()
        
        assert status['daily_cost_status'] == 'WARNING'
        assert status['overall_status'] == 'warning'
    
    def test_get_health_status_requests_critical(self, mock_client):
        """Test estado de salud con requests críticos."""
        mock_client.vertex_available = True
        mock_client.daily_cost = 5.0
        mock_client.daily_requests = 950  # 95% del límite
        
        status = mock_client.get_health_status()
        
        assert status['daily_requests_status'] == 'CRITICAL'
        assert status['overall_status'] == 'critical'


@pytest.mark.integration
class TestVertexAIIntegration:
    """Tests de integración para Vertex AI."""
    
    @pytest.mark.skipif(
        not os.getenv('VERTEX_AI_PROJECT_ID'),
        reason="Variables de entorno de Vertex AI no configuradas"
    )
    def test_real_vertex_ai_connection(self):
        """Test conexión real a Vertex AI (requiere configuración)."""
        config = VertexAIConfig()
        )
        
        client = VertexAIClient(config)
        
        # Test simple
        result = client.generate_response("Hola, ¿cómo estás?")
        
        assert result['success'] is True
        assert len(result['response']) > 0
        assert result['source'] in ['vertex_ai', 'gemini_api']
    
    @pytest.mark.skipif(
        not os.getenv('GOOGLE_API_KEY'),
        reason="Google API Key no configurada"
    )
    def test_gemini_fallback_connection(self):
        """Test conexión de fallback a Gemini API."""
        config = VertexAIConfig()
        
        # Forzar uso de fallback
        with patch('src.config.vertex_client.vertexai', side_effect=ImportError()):
            client = VertexAIClient(config)
            
            result = client.generate_response("Test de fallback")
            
            assert result['success'] is True
            assert result['source'] == 'gemini_api'
            assert len(result['response']) > 0

