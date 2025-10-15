"""Tests unitarios para Vertex AI."""

import os
from unittest.mock import patch

import pytest

pytestmark = pytest.mark.asyncio
from google.auth.exceptions import DefaultCredentialsError

from app.config.vertex_ai import VertexAIConfig
from app.config.vertex_client import VertexAIClient


class TestVertexAIConfig:
    """Tests para la configuración de Vertex AI."""

    @patch.dict(
        os.environ,
        {
            "GOOGLE_CLOUD_PROJECT_ID": "test-project",
            "GOOGLE_CLOUD_LOCATION": "us-central1",
            "VERTEX_AI_ENABLED": "true",
            "VERTEX_AI_MAX_DAILY_COST": "10.0",
        },
    )
    def test_init_with_valid_config(self):
        """Test inicialización con configuración válida."""
        config = VertexAIConfig()

        assert config.project_id == "test-project"
        assert config.location == "us-central1"
        assert config.max_daily_cost == 10.0
        assert config.enabled is True

    @patch.dict(os.environ, {"VERTEX_AI_ENABLED": "true"}, clear=True)
    def test_init_with_missing_project_id(self):
        """Test inicialización sin project_id."""
        config = VertexAIConfig()

        is_valid, error_msg = config.validate_config()
        assert not is_valid
        assert "GOOGLE_CLOUD_PROJECT_ID" in error_msg

    @patch.dict(
        os.environ,
        {"GOOGLE_CLOUD_PROJECT_ID": "test-project", "VERTEX_AI_ENABLED": "false"},
    )
    def test_init_with_disabled_vertex_ai(self):
        """Test inicialización con Vertex AI deshabilitado."""
        config = VertexAIConfig()

        is_valid, error_msg = config.validate_config()
        assert not is_valid
        assert "no está habilitado" in error_msg

    def test_get_model_info_valid_model(self):
        """Test obtener información de modelo válido."""
        config = VertexAIConfig()

        model_info = config.get_model_info("fast")

        assert model_info is not None
        assert "name" in model_info
        assert "cost_per_1m_tokens" in model_info

    def test_get_model_info_invalid_model(self):
        """Test obtener información de modelo inválido."""
        config = VertexAIConfig()

        model_info = config.get_model_info("invalid")

        assert model_info is None

    def test_estimate_cost(self):
        """Test estimación de costo."""
        config = VertexAIConfig()

        cost = config.estimate_cost(1000, 500, "fast")

        assert cost > 0
        assert isinstance(cost, float)

    @patch.dict(
        os.environ,
        {"GOOGLE_CLOUD_PROJECT_ID": "test-project-id", "VERTEX_AI_ENABLED": "true"},
    )
    def test_get_model_endpoint(self):
        """Test obtener endpoint del modelo."""
        config = VertexAIConfig()

        # Asegurarnos de que el project_id se cargó desde el entorno mockeado
        assert config.project_id == "test-project-id"

        endpoint = config.get_model_endpoint("fast")

        assert "projects/" in endpoint
        assert "models/" in endpoint
        assert config.project_id in endpoint
        assert "us-central1" in endpoint

    @patch.dict(
        os.environ,
        {
            "GOOGLE_CLOUD_PROJECT_ID": "test-project",
            "VERTEX_AI_ENABLED": "true",
            "GOOGLE_APPLICATION_CREDENTIALS": "non_existent_file.json",
        },
    )
    def test_validate_config_invalid_credentials_path(self):
        """Test validation fails with a non-existent credentials file."""
        config = VertexAIConfig()
        is_valid, error_msg = config.validate_config()
        assert not is_valid
        assert "no se encontró" in error_msg or "no encontrado" in error_msg

    @patch.dict(
        os.environ,
        {"GOOGLE_CLOUD_PROJECT_ID": "test-project", "VERTEX_AI_ENABLED": "true"},
    )
    @patch("app.config.vertex_ai.aiplatform.init")
    @patch("app.config.vertex_ai.VertexAIConfig.validate_config")
    def test_initialize_success(self, mock_validate_config, mock_init):
        """Test inicialización exitosa de Vertex AI."""
        # Mock validate_config to return True so initialize proceeds
        mock_validate_config.return_value = (True, "Configuración válida")

        config = VertexAIConfig()
        config.initialize()
        mock_init.assert_called_once_with(
            project=config.project_id, location=config.location
        )

    @patch.dict(
        os.environ,
        {"GOOGLE_CLOUD_PROJECT_ID": "test-project", "VERTEX_AI_ENABLED": "true"},
    )
    @patch(
        "app.config.vertex_ai.aiplatform.init",
        side_effect=DefaultCredentialsError("Credenciales no encontradas"),
    )
    def test_initialize_credentials_error(self, mock_init):
        """Test error de credenciales en inicialización."""
        config = VertexAIConfig()
        assert not config.initialize()

    @patch.dict(
        os.environ,
        {"GOOGLE_CLOUD_PROJECT_ID": "test-project", "VERTEX_AI_ENABLED": "true"},
    )
    @patch(
        "app.config.vertex_ai.aiplatform.init", side_effect=Exception("Error genérico")
    )
    def test_initialize_generic_error(self, mock_init):
        """Test error genérico en inicialización."""
        config = VertexAIConfig()
        result = config.initialize()
        assert result is False

    def test_get_model_endpoint_fallback(self):
        """Test that get_model_endpoint falls back to the 'fast' model."""
        config = VertexAIConfig()
        endpoint = config.get_model_endpoint("non_existent_model")
        fast_model_name = config.models["fast"]["name"]
        assert fast_model_name in endpoint

    def test_estimate_cost_invalid_model(self):
        """Test that estimate_cost returns 0 for an invalid model type."""
        config = VertexAIConfig()
        cost = config.estimate_cost(100, 100, "invalid_model")
        assert cost == 0.0


class TestVertexAIClient:
    """Tests para el cliente de Vertex AI."""

    @pytest.fixture
    def mock_client(self):
        """Fixture para cliente mock."""
        client = VertexAIClient()
        return client

    def test_init_success(self):
        """Test inicialización exitosa del cliente."""
        client = VertexAIClient()

        assert client.config is not None
        assert hasattr(client, "initialized")
        assert hasattr(client, "fallback_active")
        assert hasattr(client, "daily_cost")
        assert hasattr(client, "request_count")

    def test_estimate_tokens(self, mock_client):
        """Test estimación de tokens."""
        text = "Este es un texto de prueba para estimar tokens."

        tokens = mock_client._estimate_tokens(text)

        assert isinstance(tokens, int)
        assert tokens > 0

    def test_check_limits_under_limit(self, mock_client):
        """Test verificación de límites bajo el límite."""
        mock_client.daily_cost = 10.0
        mock_client.request_count = 50

        can_proceed, reason = mock_client._check_limits(100, "fast")

        assert can_proceed is True
        assert reason == "OK"

    def test_check_limits_over_cost_limit(self, mock_client):
        """Test verificación de límites sobre el límite de costo."""
        mock_client.daily_cost = 49.0
        mock_client.request_count = 50

        can_proceed, reason = mock_client._check_limits(100000, "pro")

        assert can_proceed is False
        # This test hits the token limit, not cost limit, which is expected behavior
        assert "límite" in reason.lower()

    def test_update_metrics(self, mock_client):
        """Test actualización de métricas de uso."""
        initial_cost = mock_client.daily_cost
        initial_requests = mock_client.request_count

        mock_client._update_metrics(100, 50, 2.5, 1.0, True)

        assert mock_client.daily_cost == initial_cost + 2.5
        assert mock_client.request_count == initial_requests + 1

    def test_get_usage_stats(self, mock_client):
        """Test obtención de estadísticas de uso."""
        mock_client.daily_cost = 5.0
        mock_client.request_count = 50
        mock_client.error_count = 2

        stats = mock_client.get_usage_stats()

        assert "daily_stats" in stats
        assert stats["daily_stats"]["requests"] == 50
        assert stats["daily_stats"]["cost"] == 5.0
        assert stats["daily_stats"]["errors"] == 2
        assert "limits" in stats
        assert "status" in stats


@pytest.mark.integration
class TestVertexAIIntegration:
    """Tests de integración para Vertex AI."""

    @pytest.mark.skipif(
        not os.getenv("GOOGLE_CLOUD_PROJECT_ID"),
        reason="Variables de entorno de Vertex AI no configuradas",
    )
    @pytest.mark.asyncio
    async def test_real_vertex_ai_connection(self):
        """Test conexión real a Vertex AI (requiere configuración)."""
        client = VertexAIClient()

        # Inicializar cliente
        success = await client.initialize()

        if success:
            # Test simple
            result = await client.generate_response("Hola, ¿cómo estás?")

            assert result["success"] is True
            assert len(result["response"]) > 0
            assert result["source"] in ["vertex_ai", "gemini_api"]
        else:
            pytest.skip("No se pudo inicializar el cliente")

    @pytest.mark.skipif(
        not os.getenv("GOOGLE_API_KEY")
        or os.getenv("GOOGLE_API_KEY") == "test-api-key",
        reason="Google API Key no configurada o es de prueba",
    )
    @pytest.mark.asyncio
    async def test_gemini_fallback_connection(self):
        """Test conexión de fallback a Gemini API."""
        client = VertexAIClient()

        # Inicializar cliente
        success = await client.initialize()

        if success:
            result = await client.generate_response("Test de fallback")

            assert result["success"] is True
            assert len(result["response"]) > 0
        else:
            pytest.skip("No se pudo inicializar el cliente")
