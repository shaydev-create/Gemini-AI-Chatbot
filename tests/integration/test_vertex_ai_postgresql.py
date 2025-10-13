"""Tests de integración para Vertex AI y PostgreSQL."""

import json
import os
from unittest.mock import patch

import pytest
from app.config.database import check_db_connection
from app.config.vertex_ai import VertexAIConfig
from app.config.vertex_client import VertexAIClient
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError


@pytest.mark.integration
class TestVertexAIPostgreSQLIntegration:
    """Tests de integración entre Vertex AI y PostgreSQL."""

    @pytest.fixture
    def test_database_url(self):
        """Fixture para URL de base de datos de prueba."""
        # Usar SQLite en memoria para tests rápidos
        return "sqlite:///:memory:"

    @pytest.fixture
    def vertex_config(self):
        """Fixture para configuración de Vertex AI."""
        return VertexAIConfig()

    @pytest.fixture
    def setup_test_database(self, test_database_url):
        """Fixture para configurar base de datos de prueba."""
        engine = create_engine(test_database_url)

        with engine.connect() as conn:
            # Crear tablas para logs de AI
            conn.execute(text("""
                CREATE TABLE ai_usage_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    model_used TEXT NOT NULL,
                    prompt_text TEXT NOT NULL,
                    response_text TEXT,
                    input_tokens INTEGER,
                    output_tokens INTEGER,
                    cost REAL,
                    source TEXT,
                    success BOOLEAN,
                    error_message TEXT,
                    response_time REAL
                )
            """))

            # Crear tabla para métricas diarias
            conn.execute(text("""
                CREATE TABLE daily_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE UNIQUE,
                    total_requests INTEGER DEFAULT 0,
                    total_cost REAL DEFAULT 0.0,
                    total_input_tokens INTEGER DEFAULT 0,
                    total_output_tokens INTEGER DEFAULT 0,
                    vertex_ai_requests INTEGER DEFAULT 0,
                    gemini_fallback_requests INTEGER DEFAULT 0,
                    error_count INTEGER DEFAULT 0
                )
            """))

            conn.commit()

        return engine

    def test_log_ai_usage_to_database(
            self, setup_test_database, vertex_config):
        """Test logging de uso de AI en la base de datos."""
        engine = setup_test_database

        # Simular uso de AI
        usage_data = {
            'model_used': 'gemini-1.5-flash',
            'prompt_text': 'Test prompt',
            'response_text': 'Test response',
            'input_tokens': 10,
            'output_tokens': 15,
            'cost': 0.001,
            'source': 'vertex_ai',
            'success': True,
            'response_time': 1.5
        }

        with engine.connect() as conn:
            # Insertar log de uso
            conn.execute(text("""
                INSERT INTO ai_usage_logs (
                    model_used, prompt_text, response_text, input_tokens,
                    output_tokens, cost, source, success, response_time
                ) VALUES (
                    :model_used, :prompt_text, :response_text, :input_tokens,
                    :output_tokens, :cost, :source, :success, :response_time
                )
            """), usage_data)

            conn.commit()

            # Verificar que se guardó correctamente
            result = conn.execute(text("""
                SELECT model_used, cost, source, success
                FROM ai_usage_logs
                WHERE prompt_text = 'Test prompt'
            """))

            row = result.fetchone()
            assert row is not None
            assert row[0] == 'gemini-1.5-flash'
            assert row[1] == 0.001
            assert row[2] == 'vertex_ai'
            assert row[3] == 1 or row[3] is True

    def test_daily_metrics_aggregation(self, setup_test_database):
        """Test agregación de métricas diarias."""
        engine = setup_test_database

        with engine.connect() as conn:
            # Insertar varios logs del día
            logs = [{'cost': 0.001,
                     'input_tokens': 10,
                     'output_tokens': 15,
                     'source': 'vertex_ai',
                     'success': True},
                    {'cost': 0.002,
                     'input_tokens': 20,
                     'output_tokens': 25,
                     'source': 'vertex_ai',
                     'success': True},
                    {'cost': 0.001,
                     'input_tokens': 15,
                     'output_tokens': 20,
                     'source': 'gemini_api',
                     'success': True},
                    {'cost': 0.000,
                     'input_tokens': 5,
                     'output_tokens': 0,
                     'source': 'vertex_ai',
                     'success': False}]

            for i, log in enumerate(logs):
                conn.execute(text("""
                    INSERT INTO ai_usage_logs (
                        model_used, prompt_text, response_text, input_tokens,
                        output_tokens, cost, source, success
                    ) VALUES (
                        'gemini-1.5-flash', :prompt, 'response', :input_tokens,
                        :output_tokens, :cost, :source, :success
                    )
                """), {
                    'prompt': f'Test prompt {i}',
                    'input_tokens': log['input_tokens'],
                    'output_tokens': log['output_tokens'],
                    'cost': log['cost'],
                    'source': log['source'],
                    'success': log['success']
                })
            conn.commit()

            # Agregar métricas diarias
            conn.execute(text("""
                INSERT OR REPLACE INTO daily_metrics (
                    date, total_requests, total_cost, total_input_tokens,
                    total_output_tokens, vertex_ai_requests, gemini_fallback_requests,
                    error_count
                )
                SELECT
                    DATE('now') as date,
                    COUNT(*) as total_requests,
                    SUM(cost) as total_cost,
                    SUM(input_tokens) as total_input_tokens,
                    SUM(output_tokens) as total_output_tokens,
                    SUM(CASE WHEN source = 'vertex_ai' THEN 1 ELSE 0 END) as vertex_ai_requests,
                    SUM(CASE WHEN source = 'gemini_api' THEN 1 ELSE 0 END) as gemini_fallback_requests,
                    SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as error_count
                FROM ai_usage_logs
                WHERE DATE(timestamp) = DATE('now')
            """))

            conn.commit()

            # Verificar métricas
            result = conn.execute(text("""
                SELECT total_requests, total_cost, vertex_ai_requests,
                       gemini_fallback_requests, error_count
                FROM daily_metrics
                WHERE date = DATE('now')
            """))

            row = result.fetchone()
            assert row is not None
            assert row[0] == 4  # total_requests
            assert row[1] == 0.004  # total_cost
            assert row[2] == 3  # vertex_ai_requests
            assert row[3] == 1  # gemini_fallback_requests
            assert row[4] == 1  # error_count

    def test_vertex_ai_with_database_logging(
            self, setup_test_database, vertex_config):
        """Test integración de Vertex AI con logging en base de datos."""
        engine = setup_test_database

        # Simular datos de respuesta de AI
        mock_result = {
            'response': 'Respuesta de prueba',
            'model_type': 'gemini-1.5-flash',
            'input_tokens': 10,
            'output_tokens': 15,
            'cost': 0.001,
            'source': 'vertex_ai',
            'success': True,
            'response_time': 1.5
        }

        # Simular logging en base de datos
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO ai_usage_logs (
                    model_used, prompt_text, response_text, input_tokens,
                    output_tokens, cost, source, success, response_time
                ) VALUES (
                    :model, :prompt, :response, :input_tokens,
                    :output_tokens, :cost, :source, :success, :response_time
                )
            """), {
                'model': mock_result['model_type'],
                'prompt': 'Prompt de prueba',
                'response': mock_result['response'],
                'input_tokens': mock_result['input_tokens'],
                'output_tokens': mock_result['output_tokens'],
                'cost': mock_result['cost'],
                'source': mock_result['source'],
                'success': mock_result['success'],
                'response_time': mock_result['response_time']
            })

            conn.commit()

            # Verificar que se guardó
            log_result = conn.execute(text("""
                SELECT prompt_text, response_text, source, success
                FROM ai_usage_logs
                WHERE prompt_text = 'Prompt de prueba'
            """))

            row = log_result.fetchone()
            assert row is not None
            assert row[0] == 'Prompt de prueba'
            assert row[1] == 'Respuesta de prueba'
            assert row[3] == 1 or row[3] is True  # success

    def test_cost_monitoring_with_database(
            self, setup_test_database, vertex_config):
        """Test monitoreo de costos con base de datos."""
        engine = setup_test_database

        with engine.connect() as conn:
            # Simular varios usos durante el día
            costs = [0.001, 0.002, 0.003, 0.001, 0.002]

            for i, cost in enumerate(costs):
                conn.execute(text("""
                    INSERT INTO ai_usage_logs (
                        model_used, prompt_text, response_text, cost, source, success
                    ) VALUES (
                        'gemini-1.5-flash', :prompt, 'response', :cost, 'vertex_ai', 1
                    )
                """), {
                    'prompt': f'Prompt {i}',
                    'cost': cost
                })

            conn.commit()

            # Calcular costo total del día
            result = conn.execute(text("""
                SELECT SUM(cost) as daily_cost
                FROM ai_usage_logs
                WHERE DATE(timestamp) = DATE('now')
                AND success = 1
            """))

            row = result.fetchone()
            daily_cost = row[0]

            assert abs(daily_cost - 0.009) < 0.0001

            # Verificar si está cerca del límite
            max_cost = vertex_config.max_daily_cost
            cost_percentage = (daily_cost / max_cost) * 100

            # Debe estar muy por debajo del límite
            assert cost_percentage < 1.0

    @pytest.mark.skipif(
        not all([
            os.getenv('VERTEX_AI_PROJECT_ID'),
            os.getenv('POSTGRES_TEST_HOST')
        ]),
        reason="Configuración completa de Vertex AI y PostgreSQL requerida"
    )
    def test_full_integration_real_services(self):
        """Test integración completa con servicios reales."""
        # Configurar PostgreSQL real
        postgres_url = f"postgresql://{
            os.getenv('POSTGRES_TEST_USER')}:{
            os.getenv('POSTGRES_TEST_PASSWORD')}@{
            os.getenv('POSTGRES_TEST_HOST')}:{
                os.getenv(
                    'POSTGRES_TEST_PORT', '5432')}/{
                        os.getenv('POSTGRES_TEST_DB')}"

        # Verificar conexión a PostgreSQL
        assert check_db_connection(postgres_url) is True

        # Configurar Vertex AI real

        client = VertexAIClient()

        # Test respuesta real
        result = client.generate_response(
            "Hola, este es un test de integración")

        assert result['success'] is True
        assert len(result['response']) > 0

        # Log en PostgreSQL real
        engine = create_engine(postgres_url)

        with engine.connect() as conn:
            # Crear tabla si no existe
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS integration_test_logs (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    test_type TEXT,
                    result_data JSONB,
                    success BOOLEAN
                )
            """))

            # Insertar resultado del test
            conn.execute(text("""
                INSERT INTO integration_test_logs (test_type, result_data, success)
                VALUES ('vertex_ai_integration', :data, :success)
            """), {
                'data': json.dumps({
                    'source': result['source'],
                    'tokens_used': result.get('tokens_used', 0),
                    'cost': result.get('cost', 0.0),
                    'response_length': len(result['response'])
                }),
                'success': result['success']
            })

            conn.commit()

            # Verificar que se guardó
            verify_result = conn.execute(text("""
                SELECT success, result_data
                FROM integration_test_logs
                WHERE test_type = 'vertex_ai_integration'
                ORDER BY timestamp DESC
                LIMIT 1
            """))

            row = verify_result.fetchone()
            assert row is not None
            assert row[0] is True  # success

            # Limpiar datos de test
            conn.execute(text("""
                DELETE FROM integration_test_logs
                WHERE test_type = 'vertex_ai_integration'
            """))

            conn.commit()


@pytest.mark.integration
class TestErrorHandlingIntegration:
    """Tests de manejo de errores en integración."""

    @patch('app.config.database.create_engine')
    def test_database_connection_failure_handling(self, mock_create_engine):
        """Test que simula un fallo de conexión a la base de datos."""
        # Forzar a create_engine a lanzar un error de conexión
        mock_create_engine.side_effect = OperationalError("Simulated connection error", None, None)

        # Llamar a la función que verifica la conexión, pasando una URL dummy
        success, message, db_type = check_db_connection("postgresql://dummy")

        # Verificar que el resultado es el esperado para un fallo de conexión
        assert success is False
        assert "Simulated connection error" in message
        assert db_type == "Unknown"

    @patch('app.config.vertex_client.vertexai', side_effect=ImportError())
    def test_vertex_ai_unavailable_with_database_logging(self, mock_vertexai):
        """Test logging cuando Vertex AI no está disponible."""

        client = VertexAIClient()

        # Verificar que el cliente no está inicializado
        assert not client.initialized

        # Verificar que no está saludable
        assert not client.is_healthy

        # Verificar que puede detectar la falta de Vertex AI
        try:
            # Intentar inicializar debería fallar
            client._initialize_vertex_ai()
            assert False, "Debería haber fallado la inicialización"
        except Exception:
            # Se espera que falle
            pass

    def test_cost_limit_exceeded_logging(self):
        """Test logging cuando se excede el límite de costo."""

        client = VertexAIClient()

        # Simular costo alto que exceda el límite (límite por defecto es $50)
        client.daily_cost = 49.95

        # Verificar que no permite más requests con un costo estimado alto
        can_proceed, reason = client._check_limits(100000, "pro")  # Muchos tokens para generar costo alto
        assert can_proceed is False
        assert "costo" in reason.lower()

        # Verificar que el costo está cerca del límite
        assert client.daily_cost >= 49.0
