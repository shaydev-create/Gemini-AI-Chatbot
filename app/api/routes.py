"""
Rutas API del Gemini AI Chatbot.
"""

import base64
import io
import time
from typing import Any, Tuple

import bleach
import PyPDF2
from flask import Blueprint, current_app, jsonify, request

from app.auth import get_current_user_from_jwt

api_bp = Blueprint("api_bp", __name__)


def extract_text_from_pdf(pdf_base64: str) -> str:
    """Extract text from a base64 encoded PDF."""
    try:
        # Decodificar base64 a bytes
        # Manejar posibles prefijos como "data:application/pdf;base64,"
        if "," in pdf_base64:
            pdf_base64 = pdf_base64.split(",")[1]

        pdf_bytes = base64.b64decode(pdf_base64)
        pdf_file = io.BytesIO(pdf_bytes)

        # Leer PDF
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = []

        # Extraer texto de todas las páginas
        for page in pdf_reader.pages:
            text.append(page.extract_text())

        return "\n".join(text)
    except Exception as e:
        current_app.logger.error(f"Error extracting text from PDF: {str(e)}")
        raise Exception(f"No se pudo leer el PDF: {str(e)}") from e


@api_bp.route("/chat/send", methods=["POST"])
def send_message() -> Tuple:  # noqa: C901
    """
    Endpoint para enviar un mensaje al chatbot y recibir una respuesta.
    Soporta contexto de imagen y documentos PDF.
    """
    data = request.get_json()
    if not data or not data.get("message"):
        return jsonify({"message": "El campo 'message' es requerido."}), 400

    # 🔒 SECURITY: Sanitizar entrada del usuario para prevenir XSS/Injection
    user_message = bleach.clean(data["message"].strip())

    session_id = data.get("session_id", "anonymous")
    image_context = data.get("image_context", None)
    pdf_context = data.get("pdf_context", None)
    history = data.get("history", [])  # Recibir historial
    language = data.get("language", "es")

    if not user_message:
        return jsonify({"message": "El mensaje no puede estar vacío."}), 400
    if len(user_message) > 4000:
        return (
            jsonify({"message": "El mensaje excede el límite de 4000 caracteres."}),
            400,
        )

    # Intentar obtener usuario autenticado
    try:
        current_user = get_current_user_from_jwt()
        user_id = current_user.id if current_user else None
    except Exception:
        user_id = None

    gemini_service = current_app.config.get("GEMINI_SERVICE")
    if not gemini_service:
        return (
            jsonify({"message": "El servicio de IA no está disponible en este momento."}),
            503,
        )

    try:
        final_prompt = user_message

        # 1. Manejo de IMÁGENES (Multimodal - Sin historial complejo por ahora)
        if image_context and image_context.get("has_image"):
            # ... (Lógica de imagen igual que antes) ...
            image_name = image_context.get("image_name", "imagen")
            context_message = image_context.get("context_message", "")

            if language == "en":
                final_prompt = f"""
{context_message}

Image context:
- File name: {image_name}
- User asks: {user_message}

Please analyze the provided image and respond to the user's question in detail and helpfully.
"""
            else:
                final_prompt = f"""
{context_message}

Contexto de imagen:
- Nombre del archivo: {image_name}
- El usuario pregunta: {user_message}

Por favor, analiza la imagen proporcionada y responde a la pregunta del usuario de manera detallada y útil.
"""
            current_app.logger.info(f"Processing message with image context: {image_name}")

            # Reset history for image requests to avoid multimodal conflicts
            history = []

        # 2. Manejo de PDFs (Contexto inyectado en prompt - Sin historial complejo)
        elif pdf_context and pdf_context.get("has_pdf"):
            # ... (Lógica de PDF igual que antes) ...
            pdf_name = pdf_context.get("pdf_name", "documento.pdf")
            pdf_data = pdf_context.get("pdf_data")
            pdf_text = extract_text_from_pdf(pdf_data)

            if len(pdf_text) > 30000:
                pdf_text = pdf_text[:30000] + "\n...[Texto truncado]..."

            if language == "en":
                final_prompt = f"""
Document Context (Extracted from PDF '{pdf_name}'):
---
{pdf_text}
---

User Question: {user_message}

Instructions: Answer the question based strictly on the provided document context.
"""
            else:
                final_prompt = f"""
Contexto del Documento (Extraído del PDF '{pdf_name}'):
---
{pdf_text}
---

Pregunta del Usuario: {user_message}

Instrucciones: Responde a la pregunta basándote estrictamente en el contexto del documento.
"""
            current_app.logger.info(f"Processing message with PDF context: {pdf_name}")

            # Reset history for PDF requests
            history = []

        response_text = gemini_service.generate_response(
            session_id=session_id,
            user_id=user_id,
            prompt=final_prompt,
            image_data=image_context.get("image_data") if image_context else None,
            history=history,  # Pasar historial
            language=language,
        )
        return jsonify({"response": response_text, "session_id": session_id}), 200
    except Exception as e:
        current_app.logger.exception("Error al generar respuesta del chat: %s", str(e))
        return jsonify({"message": f"Error: {str(e)}"}), 500


@api_bp.route("/chat/stream", methods=["POST"])
def stream_message() -> Tuple:
    """
    Endpoint para enviar un mensaje y recibir una respuesta en streaming.
    """
    # Implementación del streaming (más compleja, se deja como ejemplo conceptual)
    # Se necesitaría una función que devuelva un generador y una Response con `mimetype='text/event-stream'`.
    return jsonify({"message": "Endpoint de streaming no implementado aún."}), 501


@api_bp.route("/health", methods=["GET"])
def health_check() -> Tuple:
    """
    Endpoint de health check para verificar que la API está activa.
    """
    metrics: dict[str, Any] = {}
    uptime_seconds = int(time.time() - getattr(current_app, "start_time", time.time()))
    metrics["uptime_seconds"] = uptime_seconds
    return (
        jsonify({"status": "healthy", "timestamp": int(time.time()), "metrics": metrics}),
        200,
    )


# Export Blueprint for import in app and tests
__all__: list[Any] = ["api_bp"]
