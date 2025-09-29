"""Servicio para procesamiento multimodal con Gemini AI."""

import os
import time
import logging
from typing import Dict, Any, List, Optional
import base64

import google.generativeai as genai
from config.settings import Config
from .gemini_service import get_gemini_service

logger = logging.getLogger(__name__)


class MultimodalService:
    """Servicio para manejar la comunicación multimodal con Google Gemini AI."""

    def __init__(self):
        """Inicializar el servicio multimodal."""
        self.api_key = Config.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY no encontrada en las variables de entorno")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(Config.GEMINI_VISION_MODEL or "gemini-1.5-flash")

    def generate_response(self, message: str, images: List[str] = None) -> Dict[str, Any]:
        """Generar respuesta multimodal usando Gemini AI.

        Args:
            message: Mensaje del usuario
            images: Lista de rutas de imágenes o datos base64

        Returns:
            Dict con la respuesta y metadatos
        """
        start_time = time.time()

        try:
            # Preparar contenido multimodal
            content_parts = []
            
            # Añadir texto
            content_parts.append({"text": message})
            
            # Añadir imágenes si existen
            if images and len(images) > 0:
                for img in images:
                    if img.startswith("data:image"):
                        # Es una imagen en base64
                        img_data = img.split(",")[1]
                        img_bytes = base64.b64decode(img_data)
                        content_parts.append({"inline_data": {
                            "mime_type": "image/jpeg",
                            "data": base64.b64encode(img_bytes).decode("utf-8")
                        }})
                    elif os.path.exists(img):
                        # Es una ruta de archivo
                        mime_type = "image/jpeg"  # Por defecto
                        if img.lower().endswith(".png"):
                            mime_type = "image/png"
                        elif img.lower().endswith(".gif"):
                            mime_type = "image/gif"
                            
                        with open(img, "rb") as f:
                            image_data = f.read()
                            content_parts.append({"inline_data": {
                                "mime_type": mime_type,
                                "data": base64.b64encode(image_data).decode("utf-8")
                            }})
                    else:
                        logger.warning(f"Imagen no encontrada: {img}")

            # Generar respuesta
            response = self.model.generate_content(
                content_parts,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.4,  # Menor temperatura para respuestas más precisas
                    max_output_tokens=2048,
                    top_p=0.8,
                    top_k=40
                ),
            )

            response_text = response.text
            response_time = time.time() - start_time

            logger.info(f"Respuesta multimodal generada en {response_time:.2f}s")

            return {
                "success": True,
                "message": response_text,
                "cached": False,
                "response_time": response_time,
                "model": Config.GEMINI_VISION_MODEL or "gemini-1.5-flash",
            }

        except Exception as e:
            logger.error(f"Error de Gemini Multimodal: {e}")

            # Manejo específico de errores
            error_message = "Error temporal del servicio multimodal. Intenta de nuevo."
            error_code = "GEMINI_MULTIMODAL_ERROR"

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


# Instancia global del servicio
_multimodal_service_instance = None


def get_multimodal_service() -> MultimodalService:
    """Obtener una instancia singleton del servicio multimodal.
    
    Returns:
        MultimodalService: Instancia del servicio multimodal
    """
    global _multimodal_service_instance
    if _multimodal_service_instance is None:
        _multimodal_service_instance = MultimodalService()
    return _multimodal_service_instance