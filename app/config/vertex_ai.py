"""Configuración para Google Cloud Vertex AI."""

import logging
import os
from typing import Any, Dict, Optional

from google.auth import credentials, default
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import aiplatform

logger=logging.getLogger(__name__)


class VertexAIConfig:
    """
    Configuración centralizada y robusta para Google Cloud Vertex AI.

    Gestiona las credenciales, modelos, límites y la inicialización del servicio,
    cargando la configuración desde variables de entorno.
    """

    def __init__(self) -> None:
        """Inicializa la configuración cargando valores desde el entorno."""
        self.project_id: Optional[str] = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
        self.location: Optional[str] = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        self.credentials_path: Optional[str] = os.getenv(
            "GOOGLE_APPLICATION_CREDENTIALS"
        )
        self.enabled: bool = os.getenv("VERTEX_AI_ENABLED", "False").lower() == "true"
        self.max_daily_cost: float = float(
            os.getenv("VERTEX_AI_MAX_DAILY_COST", "50.0")
        )

        # Catálogo de modelos disponibles con sus características y costos.
        self.models: Dict[str, Dict[str, Any]] = {
            "fast": {
                "name": "gemini-flash-latest",
                "description": "Rápido y económico para tareas de alta frecuencia y escala.",
                "cost_per_1m_tokens": 0.50,
                "max_tokens": 8192,  # Límite de tokens de salida
                "recommended_for": ["chat", "resumen", "clasificación"],
            },
            "pro": {
                "name": "gemini-flash-latest",
                "description": "Modelo avanzado para tareas complejas y razonamiento profundo.",
                "cost_per_1m_tokens": 3.50,
                "max_tokens": 8192,
                "recommended_for": [
                    "análisis de datos",
                    "razonamiento complejo",
                    "generación de código",
                ],
            },
            "basic": {
                "name": "gemini-flash-latest",
                "description": "Modelo base, rápido y económico para tareas generales.",
                "cost_per_1m_tokens": 0.25,
                "max_tokens": 2048,
                "recommended_for": ["chat básico", "preguntas y respuestas simples"],
            },
        }

        # Límites de uso para proteger contra picos de tráfico y costos inesperados.
        self.limits: Dict[str, int | float] = {
            "requests_per_minute": 1000,
            "requests_per_day": 50000,
            "max_tokens_per_request": 8192,
            "max_daily_cost": self.max_daily_cost,
            "timeout_seconds": 60,
        }

        # Configuración de fallback para usar la API de Gemini directamente si Vertex AI falla.
        self.fallback_config: Dict[str, bool | int | float] = {
            "enabled": True,
            "max_retries": 3,
            "retry_delay": 1.5,  # Segundos
            "use_gemini_api": True,
        }

    def validate_config(self) -> tuple[bool, str]:
        """
        Valida que la configuración esencial para Vertex AI esté presente y sea correcta.

        Returns:
            Una tupla (es_valido, mensaje_error).
        """
        if not self.enabled:
            return False, "Vertex AI no está habilitado (VERTEX_AI_ENABLED=False)"

        if not self.project_id:
            return (
                False,
                "El ID del proyecto de Google Cloud no está configurado (GOOGLE_CLOUD_PROJECT_ID)",
            )

        if self.credentials_path and not os.path.exists(self.credentials_path):
            return (
                False,
                f"El archivo de credenciales no se encontró en la ruta: {self.credentials_path}",
            )

        return True, "Configuración de Vertex AI válida."

    def initialize(self) -> bool:
        """
        Inicializa la conexión con Vertex AI y verifica las credenciales.

        Establece el entorno para que la biblioteca de Google Cloud pueda autenticarse
        y comunicarse con los servicios de Vertex AI.

        Returns:
            True si la inicialización fue exitosa, False en caso contrario.
        """
        is_valid, message = self.validate_config()
        if not is_valid:
            logger.warning("⚠️  Inicialización de Vertex AI omitida: %s", message)
            return False

        try:
            # Configurar las credenciales si se especifica una ruta de archivo.
            creds: Optional[credentials.Credentials] = None
            if self.credentials_path and os.path.exists(self.credentials_path):
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.credentials_path
                logger.info("🔑 Usando credenciales desde: %s", self.credentials_path)

            # Inicializar la plataforma de IA de Vertex.
            aiplatform.init(project=self.project_id, location=self.location)

            # Verificar que las credenciales por defecto sean válidas y correspondan al proyecto.
            creds, detected_project = default()
            if detected_project and detected_project != self.project_id:
                logger.warning(
                    "⚠️ El proyecto en las credenciales (%s) no coincide con el configurado (%s).",
                    detected_project,
                    self.project_id,
                )

            logger.info(
                "✅ Vertex AI inicializado con éxito. Proyecto: %s, Región: %s",
                self.project_id,
                self.location,
            )
            return True

        except DefaultCredentialsError:
            logger.exception(
                "❌ Error de credenciales por defecto. Asegúrese de que 'gcloud auth application-default login' "
                "se haya ejecutado o que GOOGLE_APPLICATION_CREDENTIALS esté bien configurado."
            )
            return False
        except Exception:
            logger.exception("❌ Error inesperado al inicializar Vertex AI.")
            return False

    def get_model_info(self, model_type: str = "fast") -> Optional[Dict[str, Any]]:
        """
        Obtiene la información de configuración para un tipo de modelo específico.

        Args:
            model_type: El tipo de modelo ('fast', 'pro', 'basic').

        Returns:
            Un diccionario con la información del modelo o None si no se encuentra.
        """
        return self.models.get(model_type)

    def get_model_endpoint(self, model_type: str = "fast") -> Any:
        """
        Construye el nombre completo del endpoint para un modelo de Vertex AI.

        Args:
            model_type: El tipo de modelo.

        Returns:
            El nombre del endpoint del modelo.
        """
        model_info=self.get_model_info(model_type) or self.models["fast"]
        model_name=model_info["name"]
        return f"projects/{self.project_id}/locations/{self.location}/publishers/google/models/{model_name}"

    def estimate_cost(
        self, input_tokens: int, output_tokens: int, model_type: str = "fast"
    ) -> float:
        """
        Estima el costo de una solicitud a un modelo basado en el número de tokens.

        Args:
            input_tokens: Número de tokens de entrada.
            output_tokens: Número de tokens de salida.
            model_type: El tipo de modelo utilizado.

        Returns:
            El costo estimado en USD.
        """
        model_info=self.get_model_info(model_type)
        if not model_info:
            logger.warning(
                "No se pudo estimar el costo: modelo '%s' no encontrado.", model_type
            )
            return 0.0

        total_tokens=input_tokens + output_tokens
        cost_per_million=model_info["cost_per_1m_tokens"]
        return (total_tokens / 1_000_000) * cost_per_million


# Instancia global para ser importada y utilizada en toda la aplicación.
vertex_config=VertexAIConfig()