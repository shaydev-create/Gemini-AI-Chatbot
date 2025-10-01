"""Configuración para Google Cloud Vertex AI."""

import os
import logging
from typing import Dict, Optional
from google.cloud import aiplatform
from google.auth import default
from google.auth.exceptions import DefaultCredentialsError

logger = logging.getLogger(__name__)


class VertexAIConfig:
    """Configuración centralizada para Vertex AI."""

    def __init__(self):
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
        self.location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        self.credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.enabled = os.getenv("VERTEX_AI_ENABLED", "False").lower() == "true"
        self.max_daily_cost = float(os.getenv("VERTEX_AI_MAX_DAILY_COST", "50.0"))

        # Modelos disponibles con sus características
        self.models = {
            "fast": {
                "name": "gemini-1.5-flash",
                "description": "Rápido y económico para tareas simples",
                "cost_per_1m_tokens": 0.50,
                "max_tokens": 32000,
                "recommended_for": ["chat", "qa", "simple_tasks"],
            },
            "pro": {
                "name": "gemini-1.5-pro",
                "description": "Avanzado para tareas complejas",
                "cost_per_1m_tokens": 3.50,
                "max_tokens": 128000,
                "recommended_for": ["analysis", "complex_reasoning", "code_generation"],
            },
            "basic": {
                "name": "gemini-1.0-pro",
                "description": "Básico y estable",
                "cost_per_1m_tokens": 0.25,
                "max_tokens": 30720,
                "recommended_for": ["basic_chat", "simple_qa"],
            },
        }

        # Límites de uso
        self.limits = {
            "requests_per_minute": 1000,
            "requests_per_day": 50000,
            "max_tokens_per_request": 32000,
            "max_daily_cost": self.max_daily_cost,
            "timeout_seconds": 30,
        }

        # Configuración de fallback
        self.fallback_config = {
            "enabled": True,
            "max_retries": 3,
            "retry_delay": 1.0,
            "use_gemini_api": True,
        }

    def validate_config(self) -> tuple[bool, str]:
        """Validar configuración de Vertex AI.

        Returns:
            tuple: (is_valid, error_message)
        """
        if not self.enabled:
            return False, "Vertex AI no está habilitado"

        if not self.project_id:
            return False, "GOOGLE_CLOUD_PROJECT_ID no está configurado"

        if self.credentials_path and not os.path.exists(self.credentials_path):
            return (
                False,
                f"Archivo de credenciales no encontrado: {
                self.credentials_path}",
            )

        return True, "Configuración válida"

    def initialize(self) -> bool:
        """Inicializar Vertex AI.

        Returns:
            bool: True si la inicialización fue exitosa
        """
        try:
            # Validar configuración
            is_valid, error_msg = self.validate_config()
            if not is_valid:
                logger.warning(f"⚠️ Vertex AI: {error_msg}")
                return False

            # Configurar credenciales si están especificadas
            if self.credentials_path and os.path.exists(self.credentials_path):
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.credentials_path

            # Inicializar Vertex AI
            aiplatform.init(project=self.project_id, location=self.location)

            # Verificar credenciales
            credentials, project = default()
            if project != self.project_id:
                logger.warning(
                    f"⚠️ Proyecto en credenciales ({project}) difiere del configurado ({
                        self.project_id})"
                )

            logger.info(
                f"✅ Vertex AI inicializado - Proyecto: {self.project_id}, Región: {self.location}"
            )
            return True

        except DefaultCredentialsError as e:
            logger.error(f"❌ Error de credenciales Vertex AI: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error inicializando Vertex AI: {e}")
            return False

    def get_model_info(self, model_type: str = "fast") -> Optional[Dict]:
        """Obtener información del modelo.

        Args:
            model_type: Tipo de modelo ('fast', 'pro', 'basic')

        Returns:
            Dict con información del modelo o None si no existe
        """
        return self.models.get(model_type)

    def get_model_endpoint(self, model_type: str = "fast") -> str:
        """Obtener endpoint del modelo.

        Args:
            model_type: Tipo de modelo

        Returns:
            str: Endpoint del modelo
        """
        model_info = self.get_model_info(model_type)
        if not model_info:
            model_info = self.models["fast"]  # Fallback

        model_name = model_info["name"]
        return f"projects/{self.project_id}/locations/{self.location}/publishers/google/models/{model_name}"

    def estimate_cost(
        self, input_tokens: int, output_tokens: int, model_type: str = "fast"
    ) -> float:
        """Estimar costo de una solicitud.

        Args:
            input_tokens: Tokens de entrada
            output_tokens: Tokens de salida
            model_type: Tipo de modelo

        Returns:
            float: Costo estimado en USD
        """
        model_info = self.get_model_info(model_type)
        if not model_info:
            return 0.0

        total_tokens = input_tokens + output_tokens
        cost_per_million = model_info["cost_per_1m_tokens"]
        return (total_tokens / 1_000_000) * cost_per_million


# Instancia global de configuración
vertex_config = VertexAIConfig()
