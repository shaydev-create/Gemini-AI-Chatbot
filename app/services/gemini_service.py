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

        # System Instruction para definir la personalidad y comportamiento
        system_instruction = """
Eres Gemini, un asistente de inteligencia artificial avanzado, autónomo y proactivo.

Tus principios fundamentales son:
1. **Contexto:** Mantén siempre el hilo de la conversación. Recuerda lo que el usuario dijo anteriormente.
2. **Autonomía:** Si falta información, infiere lo más lógico o pide aclaración, pero intenta avanzar.
3. **Utilidad:** Tus respuestas deben ser prácticas, directas y aportar valor.
4. **Aprendizaje de Sesión:** Adapta tu tono y estilo según las preferencias que el usuario muestre en esta conversación.

Responde siempre en el idioma que el usuario prefiera (por defecto Español), con formato Markdown limpio.
"""

        self.model = genai.GenerativeModel(model_name="gemini-2.0-flash-001", system_instruction=system_instruction)
        logger.info("✅ Servicio Gemini ORIGINAL restaurado y configurado con System Instructions")

    def generate_response(  # noqa: C901
        self,
        message: Optional[str] = None,
        session_id: Optional[str] = None,
        user_id: Optional[int] = None,
        prompt: Optional[str] = None,
        image_data: Optional[str] = None,
        history: Optional[list[dict[str, Any]]] = None,
        language: str = "es",
    ) -> str:
        """
        Generar respuesta usando Gemini AI con historial de conversación.

        Args:
            message: Mensaje del usuario
            session_id: Ignorado
            user_id: Ignorado
            prompt: Alias para message
            image_data: Data URL de imagen
            history: Historial de chat en formato Gemini
            language: Idioma preferido

        Returns:
            String con la respuesta generada
        """
        # Compatibilidad con ambas interfaces
        text_to_process = prompt or message

        if not text_to_process:
            return "Por favor, proporciona un mensaje para procesar."

        start_time = time.time()
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                # 1. Caso Multimodal (Imagen + Texto) - El historial es complejo aquí, usaremos generate_content simple
                if image_data:
                    # ... (Lógica de imagen existente) ...
                    import base64
                    import io

                    from PIL import Image

                    if "," in image_data:
                        header, base64_data = image_data.split(",", 1)
                    else:
                        base64_data = image_data

                    image_bytes = base64.b64decode(base64_data)
                    image = Image.open(io.BytesIO(image_bytes))

                    # Añadir contexto de idioma
                    lang_instr = "Responde en Español. " if language == "es" else "Respond in English. "
                    final_prompt = lang_instr + text_to_process

                    content = [final_prompt, image]
                    logger.info(f"🖼️ Processing multimodal request: {text_to_process[:50]}...")

                    response = self.model.generate_content(
                        content, generation_config=genai.types.GenerationConfig(temperature=0.7, max_output_tokens=2048)
                    )
                    return response.text

                # 2. Caso Texto Puro con Historial (Chat Session)
                else:
                    # Configurar historial si existe
                    chat_history = []
                    if history:
                        # Validar y limpiar historial
                        for msg in history:
                            if "role" in msg and "parts" in msg:
                                # Asegurar que 'parts' sea una lista de strings o el formato correcto
                                parts = msg["parts"]
                                if (
                                    isinstance(parts, list)
                                    and len(parts) > 0
                                    and isinstance(parts[0], dict)
                                    and "text" in parts[0]
                                ):
                                    chat_history.append(msg)

                    # Iniciar sesión de chat con historial
                    chat = self.model.start_chat(history=chat_history)

                    logger.info(f"💬 Processing chat request with {len(chat_history)} history messages...")

                    # Enviar mensaje
                    response = chat.send_message(
                        text_to_process, generation_config=genai.types.GenerationConfig(temperature=0.7, max_output_tokens=2048)
                    )

                    logger.info(f"✅ Respuesta generada en {time.time() - start_time:.2f}s")
                    return response.text

            except Exception as e:
                logger.error(f"❌ Error de Gemini (Intento {attempt + 1}): {e}")
                # ... (Manejo de errores existente) ...
                if attempt == max_retries - 1:
                    return f"Error en el servicio de IA: {str(e)}"
                time.sleep(retry_delay * (2**attempt))

        return "Error desconocido."

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
