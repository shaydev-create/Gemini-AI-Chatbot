"""Módulo para gestionar la memoria de conversaciones con Gemini AI."""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class ConversationMemory:
    """Clase para gestionar el historial de conversaciones con Gemini AI."""

    def __init__(self, max_history: int = 10):
        """Inicializar la memoria de conversación.

        Args:
            max_history: Número máximo de mensajes a mantener en el historial
        """
        self.max_history = max_history
        self.history: List[Dict[str, Any]] = []
        self.session_id: Optional[str] = None

    def add_message(
        self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Añadir un mensaje al historial.

        Args:
            role: Rol del mensaje (user o assistant)
            content: Contenido del mensaje
            metadata: Metadatos adicionales del mensaje
        """
        if len(self.history) >= self.max_history:
            # Eliminar el mensaje más antiguo
            self.history.pop(0)

        message = {
            "role": role,
            "content": content,
            "timestamp": metadata.get("timestamp") if metadata else None,
        }

        if metadata:
            message["metadata"] = metadata

        self.history.append(message)
        logger.debug(f"Mensaje añadido a la memoria: {role}")

    def get_history(self) -> List[Dict[str, Any]]:
        """Obtener el historial completo de la conversación.

        Returns:
            Lista de mensajes en el historial
        """
        return self.history

    def clear(self) -> None:
        """Limpiar el historial de conversación."""
        self.history = []
        logger.debug("Historial de conversación limpiado")

    def set_session_id(self, session_id: str) -> None:
        """Establecer el ID de sesión para esta conversación.

        Args:
            session_id: ID único de la sesión
        """
        self.session_id = session_id
        logger.debug(f"ID de sesión establecido: {session_id}")

    def get_session_id(self) -> Optional[str]:
        """Obtener el ID de sesión actual.

        Returns:
            ID de sesión o None si no está establecido
        """
        return self.session_id

    def format_for_gemini(self) -> List[Dict[str, str]]:
        """Formatear el historial para enviar a Gemini API.

        Returns:
            Lista de mensajes en formato compatible con Gemini
        """
        formatted_history = []
        for msg in self.history:
            formatted_history.append(
                {
                    "role": "user" if msg["role"] == "user" else "model",
                    "parts": [{"text": msg["content"]}],
                }
            )
        return formatted_history
