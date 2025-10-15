"""
Servicio para integración con Google Gemini AI.
VERSIÓN RESTAURADA - Esta era la que funcionaba antes de la limpieza.
ACTUALIZADA CON SOPORTE MULTIMODAL PARA ANÁLISIS DE IMÁGENES.
"""

import logging
import os
import time
from typing import Any, Optional

import google.generativeai as genai

logger = logging.getLogger(__name__)


class GeminiService:
    """Servicio para manejar la comunicación con Google Gemini AI."""

    def __init__(self) -> None:
        """Inicializar el servicio Gemini - VERSIÓN ORIGINAL RESTAURADA."""
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY no encontrada en las variables de entorno")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash-001")
        logger.info("✅ Servicio Gemini ORIGINAL restaurado y configurado")

    def generate_response(
        self,
        message: Optional[str] = None,
        session_id: Optional[str] = None,
        user_id: Optional[int] = None,
        prompt: Optional[str] = None,
        image_data: Optional[str] = None,
        language: str = "es",
    ) -> str:
        """
        Generar respuesta usando Gemini AI - MÉTODO ORIGINAL RESTAURADO CON SOPORTE MULTIMODAL.

        Args:
            message: Mensaje del usuario (compatibilidad con versión nueva)
            session_id: Ignorado por compatibilidad
            user_id: Ignorado por compatibilidad
            prompt: Alias para message por compatibilidad
            image_data: Data URL de imagen en base64 (nuevo)

        Returns:
            String con la respuesta generada
        """
        # Compatibilidad con ambas interfaces
        text_to_process = prompt or message

        if not text_to_process:
            return "Por favor, proporciona un mensaje para procesar."

        # Preparar instrucciones de idioma
        language_instruction: str = ""
        if language == "en":
            language_instruction = "IMPORTANT: Please respond only in English. "
        elif language == "es":
            language_instruction = (
                "IMPORTANTE: Por favor responde únicamente en español. "
            )

        # Agregar instrucciones de idioma al prompt
        text_to_process = language_instruction + text_to_process

        start_time = time.time()

        try:
            # Prepare content for multimodal if image is provided
            if image_data:
                # Handle base64 image data
                import base64
                import io

                from PIL import Image

                # Extract base64 data from data URL
                if "," in image_data:
                    header, base64_data = image_data.split(",", 1)
                else:
                    base64_data = image_data

                # Decode base64 image
                image_bytes = base64.b64decode(base64_data)
                image = Image.open(io.BytesIO(image_bytes))

                # Create multimodal content
                content: list[Any] = [text_to_process, image]
                logger.info(
                    f"🖼️ Processing multimodal request with image and text: {text_to_process[:100]}..."
                )
            else:
                content = text_to_process
                logger.info(
                    f"💬 Processing text-only request: {text_to_process[:100]}..."
                )

            response = self.model.generate_content(
                content,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7, max_output_tokens=2048, top_p=0.8, top_k=40
                ),
            )

            response_text = response.text
            response_time = time.time() - start_time

            logger.info(f"✅ Respuesta generada en {response_time:.2f}s")
            return response_text

        except Exception as e:
            logger.error(f"❌ Error de Gemini: {e}")

            # Manejo específico de errores
            if "429" in str(e) or "quota" in str(e).lower():
                return "Has excedido el límite de la API de Gemini. Verifica tu cuota en Google AI Studio."
            elif "API_KEY_INVALID" in str(e) or "invalid" in str(e).lower():
                return "API key inválida. Verifica tu configuración."
            elif "PERMISSION_DENIED" in str(e):
                return "Permisos denegados. Verifica tu API key y configuración."
            else:
                return "Error temporal del servicio. Intenta de nuevo."

    def validate_api_key(self) -> bool:
        """
        Validar que la API key funciona correctamente.

        Returns:
            bool: True si la API key es válida
        """
        try:
            self.model.generate_content("Test")
            return True
        except Exception as e:
            logger.error(f"API key inválida: {e}")
            return False
