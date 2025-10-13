"""
Rutas API del Gemini AI Chatbot.
"""

from flask import current_app, jsonify, request

from app.api import api
from app.auth import get_current_user_from_jwt


@api.route("/chat/send", methods=["POST"])
def send_message():
    """
    Endpoint para enviar un mensaje al chatbot y recibir una respuesta.
    Ahora soporta contexto de imagen para análisis multimodal.
    """
    data = request.get_json()
    if not data or not data.get("message"):
        return jsonify({"message": "El campo 'message' es requerido."}), 400

    user_message = data["message"].strip()
    session_id = data.get("session_id", "anonymous")  # Usar sesión anónima si no se proporciona
    image_context = data.get("image_context", None)  # Nuevo: contexto de imagen
    language = data.get("language", "es")  # Obtener idioma, por defecto español

    if not user_message:
        return jsonify({"message": "El mensaje no puede estar vacío."}), 400
    if len(user_message) > 4000:
        return jsonify({"message": "El mensaje excede el límite de 4000 caracteres."}), 400

    # Intentar obtener usuario autenticado, pero no requerirlo
    try:
        current_user = get_current_user_from_jwt()
        user_id = current_user.id if current_user else None
    except:
        user_id = None  # Usuario anónimo

    gemini_service = current_app.gemini_service
    if not gemini_service:
        return jsonify({"message": "El servicio de IA no está disponible en este momento."}), 503

    try:
        # Prepare the prompt with image context if available
        final_prompt = user_message
        
        if image_context and image_context.get("has_image"):
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
        
        response_text = gemini_service.generate_response(
            session_id=session_id,
            user_id=user_id,
            prompt=final_prompt,
            image_data=image_context.get("image_data") if image_context else None,
            language=language
        )
        return jsonify({"response": response_text, "session_id": session_id}), 200
    except Exception as e:
        current_app.logger.exception("Error al generar respuesta del chat: %s", str(e))
        return jsonify({"message": "Error interno al procesar la solicitud."}), 500


@api.route("/chat/stream", methods=["POST"])
def stream_message():
    """
    Endpoint para enviar un mensaje y recibir una respuesta en streaming.
    """
    # Implementación del streaming (más compleja, se deja como ejemplo conceptual)
    # Se necesitaría una función que devuelva un generador y una Response con `mimetype='text/event-stream'`.
    return jsonify({"message": "Endpoint de streaming no implementado aún."}), 501


@api.route("/health", methods=["GET"])
def health_check():
    """
    Endpoint de health check para verificar que la API está activa.
    """
    return jsonify({"status": "healthy"}), 200
