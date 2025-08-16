"""
Servicio para integración con Google Gemini AI.
"""

import time
import logging
from typing import Dict, Any
import google.generativeai as genai
from config.settings import Config

logger = logging.getLogger(__name__)


class GeminiService:
    """Servicio para manejar la comunicación con Google Gemini AI."""

    def __init__(self):
        """Inicializar el servicio Gemini."""
        self.api_key = Config.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY no encontrada en las variables de entorno")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def generate_response(self, message: str) -> Dict[str, Any]:
        """
        Generar respuesta usando Gemini AI.

        Args:
            message: Mensaje del usuario

        Returns:
            Dict con la respuesta y metadatos
        """
        start_time = time.time()

        try:
            response = self.model.generate_content(
                message,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7, max_output_tokens=2048, top_p=0.8, top_k=40
                ),
            )

            response_text = response.text
            response_time = time.time() - start_time

            logger.info(f"Respuesta generada en {response_time:.2f}s")

            return {
                "success": True,
                "message": response_text,
                "cached": False,
                "response_time": response_time,
                "model": "gemini-1.5-flash",
            }

        except Exception as e:
            logger.error(f"Error de Gemini: {e}")

            # Manejo específico de errores
            error_message = "Error temporal del servicio. Intenta de nuevo."
            error_code = "GEMINI_ERROR"

            if (
                "429" in str(e)
                or "quota" in str(e).lower()
                or "ResourceExhausted" in str(e)
            ):
                error_message = "Has excedido el límite de la API de Gemini. Verifica tu cuota en Google AI Studio."
                error_code = "QUOTA_EXCEEDED"
            elif "API_KEY_INVALID" in str(e) or "invalid" in str(e).lower():
                error_message = "API key inválida. Verifica tu configuración."
                error_code = "INVALID_API_KEY"
            elif "PERMISSION_DENIED" in str(e):
                error_message = (
                    "Permisos denegados. Verifica tu API key y configuración."
                )
                error_code = "PERMISSION_DENIED"

            return {
                "success": False,
                "message": error_message,
                "error_code": error_code,
                "details": str(e) if Config.DEBUG else None,
            }

    def validate_api_key(self) -> bool:
        """
        Validar que la API key funciona correctamente.

        Returns:
            bool: True si la API key es válida
        """
        try:
            test_response = self.model.generate_content("Test")
            return True
        except Exception as e:
            logger.error(f"API key inválida: {e}")
            return False
