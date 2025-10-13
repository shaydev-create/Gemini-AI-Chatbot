#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the VertexAIClient.
"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Set environment variables for testing
os.environ['GOOGLE_API_KEY'] = 'test-api-key'
os.environ['VERTEX_AI_PROJECT_ID'] = 'test-project'
os.environ['VERTEX_AI_LOCATION'] = 'test-location'


class TestVertexAIClient:
    """Test suite for the VertexAIClient."""

    def setup_method(self):
        """Set up the test environment."""
        # Mock the configuration and external libraries
        self.patcher_vertex_config = patch('app.config.vertex_client.vertex_config')
        self.mock_vertex_config = self.patcher_vertex_config.start()

        # Set default mock values for limits
        self.mock_vertex_config.limits = {
            "max_daily_cost": 100.0,
            "max_tokens_per_request": 2000
        }
        self.mock_vertex_config.estimate_cost.return_value = 0.01

        self.patcher_vertex_ai = patch('app.config.vertex_client.VERTEX_AI_AVAILABLE', True)
        self.mock_vertex_ai_available = self.patcher_vertex_ai.start()

        self.patcher_gemini_api = patch('app.config.vertex_client.GEMINI_API_AVAILABLE', True)
        self.mock_gemini_api_available = self.patcher_gemini_api.start()

        self.patcher_vertexai_init = patch('app.config.vertex_client.vertexai.init')
        self.mock_vertexai_init = self.patcher_vertexai_init.start()

        self.patcher_generative_model = patch('app.config.vertex_client.GenerativeModel')
        self.mock_generative_model = self.patcher_generative_model.start()

        self.patcher_genai_configure = patch('app.config.vertex_client.genai.configure')
        self.mock_genai_configure = self.patcher_genai_configure.start()

        self.patcher_genai_model = patch('app.config.vertex_client.genai.GenerativeModel')
        self.mock_genai_model = self.patcher_genai_model.start()

        # Must import the client *after* patching the availability flags
        from app.config.vertex_client import VertexAIClient
        self.client = VertexAIClient()
        # Ensure the client uses the mocked config
        self.client.config = self.mock_vertex_config


    def teardown_method(self):
        """Clean up the test environment."""
        self.patcher_vertex_config.stop()
        self.patcher_vertex_ai.stop()
        self.patcher_gemini_api.stop()
        self.patcher_vertexai_init.stop()
        self.patcher_generative_model.stop()
        self.patcher_genai_configure.stop()
        self.patcher_genai_model.stop()

    def test_initialization_state(self):
        """Test the initial state of the client."""
        assert not self.client.initialized
        assert not self.client.fallback_active
        assert not self.client.is_healthy
        assert self.client.gemini_client is None
    async def test_initialize_vertex_ai_success(self):
        """Test successful initialization of Vertex AI."""
        self.mock_vertex_config.enabled = True
        self.mock_vertex_config.initialize.return_value = True
        self.mock_vertex_config.models = {'fast': {'name': 'gemini-1.0-pro'}}

        result = await self.client.initialize()

        assert result
        assert self.client.initialized
        assert not self.client.fallback_active
        assert self.client.is_healthy
        self.mock_vertexai_init.assert_called_once()
        self.mock_generative_model.assert_called_once_with('gemini-1.0-pro')

    @pytest.mark.asyncio
    async def test_initialize_fallback_success(self):
        """Test successful initialization of Gemini API as fallback."""
        self.mock_vertex_config.enabled = False  # Disable Vertex AI

        result = await self.client.initialize()

        assert result
        assert not self.client.initialized
        assert self.client.fallback_active
        assert self.client.is_healthy
        self.mock_genai_configure.assert_called_once()
        assert self.client.gemini_client is not None

    @pytest.mark.asyncio
    async def test_initialize_no_clients_available(self):
        """Test initialization when no clients are available."""
        with patch('app.config.vertex_client.VERTEX_AI_AVAILABLE', False), \
             patch('app.config.vertex_client.GEMINI_API_AVAILABLE', False):

            from app.config.vertex_client import VertexAIClient
            client = VertexAIClient()
            result = await client.initialize()

            assert not result
            assert not client.is_healthy

    @pytest.mark.asyncio
    async def test_initialize_vertex_ai_fails_but_fallback_succeeds(self):
        """Test that fallback is used if Vertex AI initialization fails."""
        self.mock_vertex_config.enabled = True
        self.mock_vertex_config.initialize.side_effect = Exception("Vertex AI Error")

        result = await self.client.initialize()

        assert result
        assert not self.client.initialized
        assert self.client.fallback_active
        assert self.client.is_healthy
        self.mock_genai_configure.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_no_gemini_api_key(self):
        """Test initialization when Gemini API key is missing."""
        self.mock_vertex_config.enabled = False
        with patch.dict(os.environ, {'GOOGLE_API_KEY': '', 'GEMINI_API_KEY': ''}):
            from app.config.vertex_client import VertexAIClient
            client = VertexAIClient()
            # We need to re-patch the availability for this specific client instance
            with patch('app.config.vertex_client.GEMINI_API_AVAILABLE', True):
                result = await client.initialize()

                assert not result
                assert not client.is_healthy
                # Fallback is not activated because initialization fails
                assert not client.fallback_active
                assert client.gemini_client is None

    @pytest.mark.asyncio
    async def test_initialize_no_models_loaded(self):
        """Test initialization fails if no Vertex AI models can be loaded."""
        self.mock_vertex_config.enabled = True
        self.mock_vertex_config.initialize.return_value = True
        self.mock_vertex_config.models = {'fast': {'name': 'bad-model'}}
        self.mock_generative_model.side_effect = Exception("Model not found")

        with patch('app.config.vertex_client.GEMINI_API_AVAILABLE', False):
            result = await self.client.initialize()
            assert not result
            assert not self.client.initialized
            assert not self.client.is_healthy

    @patch('time.time')
    def test_reset_daily_limits(self, mock_time):
        """Test that daily limits are reset after 24 hours."""
        self.client.daily_cost = 10.0
        self.client.request_count = 100
        mock_time.return_value = 1700000000.0
        self.client.last_reset = mock_time.return_value - 86401

        self.client._reset_daily_limits()

        assert self.client.daily_cost == 0.0
        assert self.client.request_count == 0
        assert self.client.last_reset == mock_time.return_value

    def test_update_metrics(self):
        """Test that usage metrics are updated correctly."""
        initial_requests = self.client.request_count
        initial_cost = self.client.daily_cost
        initial_errors = self.client.error_count

        self.client._update_metrics(10, 20, 0.001, 0.5, True)
        assert self.client.request_count == initial_requests + 1
        assert self.client.daily_cost == initial_cost + 0.001
        assert len(self.client.usage_history) == 1

        self.client._update_metrics(0, 0, 0, 0.1, False)
        assert self.client.error_count == initial_errors + 1
        assert len(self.client.usage_history) == 2
        assert not self.client.usage_history[-1]['success']

    def test_get_usage_stats(self):
        """Test retrieval of usage statistics."""
        self.client._update_metrics(10, 20, 0.001, 0.5, True)
        stats = self.client.get_usage_stats()

        assert stats['daily_stats']['requests'] == 1
        assert stats['daily_stats']['cost'] == 0.001
        assert stats['daily_stats']['success_rate'] == 100.0
        assert stats['recent_requests'] == 1
        assert abs(stats['avg_response_time'] - 0.5) < 1e-9

    @pytest.mark.asyncio
    async def test_generate_response_with_vertex_ai(self):
        """Test generating a response using Vertex AI."""
        self.client.initialized = True
        self.client.is_healthy = True
        self.client.fallback_active = False

        self.client._generate_with_vertex_ai = AsyncMock(return_value={
            "response": "Vertex response", "input_tokens": 10, "output_tokens": 20,
            "cost": 0.01, "response_time": 0.5,
        })

        result = await self.client.generate_response("test prompt")

        assert result["response"] == "Vertex response"
        self.client._generate_with_vertex_ai.assert_called_once()
        assert self.client.request_count == 1
        assert abs(self.client.daily_cost - 0.01) < 1e-9

    @pytest.mark.asyncio
    async def test_generate_response_fallback_to_gemini(self):
        """Test that the client falls back to Gemini API on Vertex AI failure."""
        self.client.initialized = True
        self.client.is_healthy = True
        self.client.fallback_active = False

        self.client._generate_with_vertex_ai = AsyncMock(side_effect=Exception("Vertex failed"))

        self.client.gemini_client = MagicMock()
        self.client._generate_with_gemini_api = AsyncMock(return_value={
            "response": "Gemini fallback response", "input_tokens": 10, "output_tokens": 25,
            "cost": 0.0, "response_time": 0.8,
        })

        result = await self.client.generate_response("test prompt")

        assert result["response"] == "Gemini fallback response"
        assert self.client.fallback_active
        self.client._generate_with_vertex_ai.assert_called_once()
        self.client._generate_with_gemini_api.assert_called_once()
        assert self.client.request_count == 1
        assert self.client.error_count == 0

    @pytest.mark.asyncio
    async def test_generate_response_rejected_by_limits(self):
        """Test that generate_response raises an exception if limits are exceeded."""
        self.client.is_healthy = True
        self.client.fallback_active = True
        self.mock_vertex_config.limits["max_tokens_per_request"] = 50

        with pytest.raises(Exception, match="Solicitud rechazada:"):
            await self.client.generate_response("test a long prompt that exceeds the token limit")

    @pytest.mark.asyncio
    async def test_generate_response_cost_limit_triggers_fallback(self):
        """Test that exceeding cost limit triggers fallback to Gemini API."""
        self.client.is_healthy = True
        self.client.initialized = True
        self.client.fallback_active = False

        # Mock the gemini_client and its async method
        self.client.gemini_client = AsyncMock()
        self.client.gemini_client.generate_content_async = AsyncMock(return_value=MagicMock(text="fallback response"))

        self.mock_vertex_config.estimate_cost.return_value = 10
        self.client.daily_cost = 95

        await self.client.generate_response("test")

        # Ensure the fallback was called
        self.client.gemini_client.generate_content_async.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_response_vertex_fails_triggers_fallback(self):
        """Test that a failure in Vertex AI triggers fallback to Gemini API."""
        self.client.is_healthy = True
        self.client.initialized = True
        self.client.fallback_active = False

        # Mock the gemini_client and its async method
        self.client.gemini_client = AsyncMock()
        self.client.gemini_client.generate_content_async = AsyncMock(return_value=MagicMock(text="fallback response"))

        with patch.object(self.client, '_generate_with_vertex_ai', side_effect=Exception("Vertex Error")):
            await self.client.generate_response("test")

            assert self.client.fallback_active
            self.client.gemini_client.generate_content_async.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_response_all_clients_fail(self):
        """Test that an exception is raised if all clients fail."""
        await self.client.initialize() # Initialize to set fallback
        self.client.is_healthy = True
        self.client.initialized = False
        self.client.gemini_client = AsyncMock()
        self.client.gemini_client.generate_content_async.side_effect = Exception("Gemini Error")

        with pytest.raises(Exception, match="Todos los clientes fallaron"):
            await self.client.generate_response("test")

        assert self.client.error_count == 1

    @patch('time.time')
    @pytest.mark.asyncio
    async def test_health_check_cached(self, mock_time):
        """Test that health check uses cache within the interval."""
        mock_time.return_value = 1700000000.0
        self.client.last_health_check = mock_time.return_value - 100
        self.client.is_healthy = True

        result = await self.client.health_check()

        assert result['status'] == 'cached'
        assert result['healthy']

    @patch('time.time')
    @pytest.mark.asyncio
    async def test_health_check_runs_and_succeeds(self, mock_time):
        """Test a successful health check run for both services."""
        mock_time.return_value = 1700000000.0
        self.client.last_health_check = mock_time.return_value - 301
        self.client.initialized = True
        self.client.gemini_client = True
        self.mock_vertex_config.models = {'basic': {'name': 'test-model'}}

        with patch.object(self.client, '_generate_with_vertex_ai', new_callable=AsyncMock), \
             patch.object(self.client, '_generate_with_gemini_api', new_callable=AsyncMock):

            result = await self.client.health_check()

            assert result['vertex_ai']['available']
            assert result['gemini_api']['available']
            assert result['overall_healthy']
            assert self.client.is_healthy

    @patch('time.time')
    @pytest.mark.asyncio
    async def test_health_check_one_service_fails(self, mock_time):
        """Test health check when one service fails but the other succeeds."""
        mock_time.return_value = 1700000000.0
        self.client.last_health_check = mock_time.return_value - 301
        self.client.initialized = True
        self.client.gemini_client = True
        self.mock_vertex_config.models = {'basic': {'name': 'test-model'}}

        with patch.object(self.client, '_generate_with_vertex_ai', side_effect=Exception("Vertex Down")), \
             patch.object(self.client, '_generate_with_gemini_api', new_callable=AsyncMock):

            result = await self.client.health_check()

            assert not result['vertex_ai']['available']
            assert result['vertex_ai']['error'] is not None
            assert result['gemini_api']['available']
            assert result['overall_healthy']
            assert self.client.is_healthy
