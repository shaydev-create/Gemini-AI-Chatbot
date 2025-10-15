"""Módulo para gestionar la memoria de conversaciones con Gemini AI."""

import logging
from typing import Any, Dict, List, Optional

from app.config.extensions import db
from app.models import ChatMessage, ChatSession

logger=logging.getLogger(__name__)


class ConversationMemory:
    """
    Clase para gestionar el historial de conversaciones de forma persistente
    utilizando la base de datos.
    """

    def __init__(self, session_id: str, user_id: int, max_history: int = 20) -> None:
        """
        Inicializa la memoria de conversación, cargando o creando una sesión.

        Args:
            session_id: El ID único de la sesión de chat.
            user_id: El ID del usuario propietario de la sesión.
            max_history: Número máximo de mensajes a recuperar del historial.
        """
        self.max_history = max_history
        self.session: ChatSession = self._load_or_create_session(session_id, user_id)

    def _load_or_create_session(self, session_id: str, user_id: int) -> ChatSession:
        """Carga una sesión existente o crea una nueva si no se encuentra."""
        session=ChatSession.query.filter_by(
            session_id=session_id, user_id=user_id
        ).first()
        if session:
            logger.debug(
                "Sesión de chat cargada desde la base de datos: %s", session_id
            )
            return session
        else:
            logger.info(
                "Creando nueva sesión de chat en la base de datos: %s", session_id
            )
            new_session=ChatSession(session_id=session_id, user_id=user_id)
            db.session.add(new_session)
            db.session.commit()
            return new_session

    def add_message(
        self, role: str, content: str, tokens: Optional[int] = None
    ) -> None:
        """
        Añade un mensaje a la sesión de chat actual y lo guarda en la base de datos.

        Args:
            role: El rol del mensaje ('user' o 'model').
            content: El contenido del mensaje.
            tokens: El número de tokens utilizados por el mensaje (opcional).
        """
        if role not in ["user", "model"]:
            raise ValueError("El rol debe ser 'user' o 'model'")

        message=ChatMessage(
            session_id=self.session.id, role=role, content=content, tokens=tokens
        )
        db.session.add(message)
        db.session.commit()
        logger.debug(
            "Mensaje de '%s' añadido a la sesión %s", role, self.session.session_id
        )

    def get_history(self) -> List[ChatMessage]:
        """
        Obtiene el historial de mensajes de la sesión actual desde la base de datos.

        Returns:
            Una lista de objetos ChatMessage, ordenados del más antiguo al más reciente.
        """
        # Get total count of messages
        total_messages=ChatMessage.query.filter_by(session_id=self.session.id).count()

        # If we have more messages than the max_history limit, we need to skip the oldest ones
        if total_messages > self.max_history:
            offset=total_messages - self.max_history
            return (
                ChatMessage.query.filter_by(session_id=self.session.id)
                .order_by(ChatMessage.created_at.asc())
                .offset(offset)
                .limit(self.max_history)
                .all()
            )
        else:
            return (
                ChatMessage.query.filter_by(session_id=self.session.id)
                .order_by(ChatMessage.created_at.asc())
                .all()
            )

    def clear(self) -> None:
        """
        Elimina todos los mensajes asociados a la sesión de chat actual.
        """
        try:
            num_deleted=ChatMessage.query.filter_by(
                session_id=self.session.id
            ).delete()
            db.session.commit()
            logger.info(
                "Historial de la sesión %s limpiado (%d mensajes eliminados).",
                self.session.session_id,
                num_deleted,
            )
        except Exception:
            db.session.rollback()
            logger.exception(
                "Error al limpiar el historial de la sesión %s", self.session.session_id
            )

    @property
    def session_id(self) -> Any:
        """Devuelve el ID de la sesión actual."""
        return self.session.session_id

    def format_for_gemini(self) -> List[Dict[str, Any]]:
        """
        Formatea el historial de la conversación para ser compatible con la API de Gemini.

        Returns:
            Una lista de mensajes en el formato que espera la API de Gemini.
        """
        history=self.get_history()
        formatted_history: list[Any] = []
        for msg in history:
            formatted_history.append(
                {
                    "role": msg.role,
                    "parts": [{"text": msg.content}],
                }
            )
        return formatted_history
