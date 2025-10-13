"""
Manejo de eventos de Socket.IO para la comunicación en tiempo real.
"""
from flask_socketio import emit

from app import socketio


@socketio.on('connect')
def handle_connect():
    """
    Maneja la conexión de un nuevo cliente.
    """
    print('Client connected')
    emit('status', {'msg': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    """
    Maneja la desconexión de un cliente.
    """
    print('Client disconnected')

@socketio.on('message')
def handle_message(data):
    """
    Maneja los mensajes entrantes de los clientes.
    """
    print('received message: ' + str(data))
    # Aquí se procesaría el mensaje y se enviaría a Gemini
    emit('response', {'data': 'This is a response from the server.'})
