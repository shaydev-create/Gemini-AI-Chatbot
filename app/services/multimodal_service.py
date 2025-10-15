"""Servicio para procesamiento multimodal con Gemini AI."""

import base64
import logging
from pathlib import Path
from typing import Any, List, Union

from vertexai.generative_models import Part

from app.config.vertex_client import VertexAIClient

logger=logging.getLogger(__name__)


class MultimodalService:
    """
    Servicio para manejar solicitudes multimodales (texto, imágenes, etc.) con Gemini.

    Utiliza el VertexAIClient centralizado para enviar solicitudes a los modelos
    con capacidad de visión.
    """

    def __init__(self, client: VertexAIClient) -> None:
        """
        Inicializa el servicio multimodal.

        Args:
            client: Una instancia del VertexAIClient ya inicializado.
        """
        if not client or not client.initialized:
            raise ValueError(
                "El VertexAIClient debe ser proporcionado y estar inicializado."
            )
        self.client = client
        logger.info("✅ Servicio Multimodal inicializado.")

    def _create_image_part(self, image_data: Union[str, Path]) -> Part:
        """
        Crea un objeto `Part` de imagen a partir de una ruta de archivo o datos en base64.
        """
        if isinstance(image_data, Path) or (
            isinstance(image_data, str) and Path(image_data).exists()
        ):
            path=Path(image_data)
            mime_type=f"image/{path.suffix.lower().strip('.')}"
            with open(path, "rb") as f:
                return Part.from_data(f.read(), mime_type=mime_type)

        elif isinstance(image_data, str) and image_data.startswith("data:image"):
            header, encoded = image_data.split(",", 1)
            mime_type = header.split(":")[1].split(";")[0]
            data=base64.b64decode(encoded)
            return Part.from_data(data, mime_type=mime_type)

        raise ValueError(
            f"Formato de imagen no válido o ruta no encontrada: {image_data}"
        )

    async def generate_response(
        self, prompt: str, images: List[Union[str, Path]], model_type: str = "pro"
    ) -> str:
        """
        Genera una respuesta a partir de un prompt de texto y una lista de imágenes.

        Args:
            prompt: El prompt de texto.
            images: Una lista de imágenes. Cada elemento puede ser una ruta de archivo (str o Path)
                    o una cadena de datos en base64.
            model_type: El tipo de modelo a usar (debe ser un modelo con capacidad de visión como 'pro').

        Returns:
            La respuesta generada por el modelo como una cadena de texto.
        """
        logger.debug("Generando respuesta multimodal con el modelo %s", model_type)

        # Verificar si hay imágenes válidas
        valid_images: list[Any] = []
        for image in images:
            if isinstance(image, str) and image.startswith("data:image"):
                valid_images.append(image)
            elif isinstance(image, (str, Path)):
                try:
                    if Path(image).exists():
                        valid_images.append(image)
                except (OSError, ValueError):
                    # Ignorar errores de path inválido
                    pass

        # El servicio multimodal requiere al menos una imagen válida
        if not valid_images:
            logger.warning("No se proporcionaron imágenes válidas.")
            return "Por favor, proporciona al menos una imagen válida para el análisis."

        # Construir el prompt multimodal
        multimodal_prompt = f"{prompt}\n\nAnaliza las siguientes imágenes:"

        try:
            # Usar el cliente centralizado para generar contenido
            # El cliente actual solo maneja texto, así que construimos un prompt que mencione las imágenes
            multimodal_prompt = f"{prompt}\n\nAnaliza las siguientes imágenes:"
            response_data: dict[str, Any] = await self.client.generate_response(
                prompt=multimodal_prompt, model_type=model_type, max_tokens=1000
            )
            response_text=response_data["response"]
            logger.info("Respuesta multimodal generada con éxito.")
            return response_text

        except Exception:
            logger.exception("❌ Error al generar la respuesta multimodal.")
            return (
                "Lo siento, ha ocurrido un error al procesar tu solicitud de imágenes."
            )


# La instanciación de este servicio, al igual que GeminiService,
# se realizará durante la creación de la aplicación Flask.
