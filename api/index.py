"""
Vercel serverless function entry point for Gemini AI Chatbot
"""
import os
from flask import Flask, request, jsonify
import google.generativeai as genai

# Configurar Gemini AI
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Crear aplicación Flask
app = Flask(__name__)

@app.route('/')
def index():
    """Página principal del chatbot."""
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🚀 Gemini AI Chatbot</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            
            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                width: 100%;
                max-width: 800px;
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, #4285f4 0%, #34a853 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
                font-weight: 300;
            }
            
            .header p {
                opacity: 0.9;
                font-size: 1.1em;
            }
            
            .chat-container {
                height: 500px;
                overflow-y: auto;
                padding: 30px;
                background: #fafafa;
                border-bottom: 1px solid #eee;
            }
            
            .message {
                margin: 15px 0;
                padding: 15px 20px;
                border-radius: 15px;
                max-width: 80%;
                word-wrap: break-word;
                animation: fadeIn 0.3s ease-in;
            }
            
            .user {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                margin-left: auto;
                text-align: right;
            }
            
            .bot {
                background: #e8f5e8;
                color: #2d5a2d;
                border-left: 4px solid #4caf50;
            }
            
            .input-container {
                padding: 30px;
                background: white;
                display: flex;
                gap: 15px;
                align-items: center;
            }
            
            #messageInput {
                flex: 1;
                padding: 15px 20px;
                border: 2px solid #e0e0e0;
                border-radius: 25px;
                font-size: 16px;
                outline: none;
                transition: border-color 0.3s ease;
            }
            
            #messageInput:focus {
                border-color: #4285f4;
            }
            
            #sendButton {
                padding: 15px 30px;
                background: linear-gradient(135deg, #4285f4 0%, #34a853 100%);
                color: white;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 500;
                transition: transform 0.2s ease;
            }
            
            #sendButton:hover {
                transform: translateY(-2px);
            }
            
            #sendButton:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            
            .loading {
                display: none;
                text-align: center;
                padding: 20px;
                color: #666;
            }
            
            .loading::after {
                content: '';
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid #f3f3f3;
                border-top: 3px solid #4285f4;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-left: 10px;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            @media (max-width: 600px) {
                .container {
                    margin: 10px;
                    border-radius: 15px;
                }
                
                .header h1 {
                    font-size: 2em;
                }
                
                .chat-container {
                    height: 400px;
                    padding: 20px;
                }
                
                .input-container {
                    padding: 20px;
                    flex-direction: column;
                }
                
                #messageInput {
                    width: 100%;
                    margin-bottom: 10px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Gemini AI Chatbot</h1>
                <p>Tu asistente inteligente powered by Google Gemini</p>
            </div>
            
            <div id="chat" class="chat-container">
                <div class="message bot">
                    ¡Hola! 👋 Soy tu asistente AI powered by Google Gemini. 
                    ¿En qué puedo ayudarte hoy?
                </div>
            </div>
            
            <div class="loading" id="loading">
                Pensando...
            </div>
            
            <div class="input-container">
                <input 
                    type="text" 
                    id="messageInput" 
                    placeholder="Escribe tu mensaje aquí..." 
                    onkeypress="if(event.key==='Enter') sendMessage()"
                    autocomplete="off"
                >
                <button id="sendButton" onclick="sendMessage()">
                    Enviar 🚀
                </button>
            </div>
        </div>
        
        <script>
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const chat = document.getElementById('chat');
                const loading = document.getElementById('loading');
                const sendButton = document.getElementById('sendButton');
                const message = input.value.trim();
                
                if (!message) return;
                
                // Deshabilitar input y botón
                input.disabled = true;
                sendButton.disabled = true;
                
                // Mostrar mensaje del usuario
                chat.innerHTML += `<div class="message user">${escapeHtml(message)}</div>`;
                input.value = '';
                
                // Mostrar loading
                loading.style.display = 'block';
                chat.scrollTop = chat.scrollHeight;
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message: message })
                    });
                    
                    const data = await response.json();
                    
                    // Ocultar loading
                    loading.style.display = 'none';
                    
                    // Mostrar respuesta del bot
                    chat.innerHTML += `<div class="message bot">${escapeHtml(data.response || 'Error en la respuesta')}</div>`;
                    
                } catch (error) {
                    loading.style.display = 'none';
                    chat.innerHTML += `<div class="message bot">❌ Error: No se pudo conectar con el servidor. Por favor, intenta de nuevo.</div>`;
                }
                
                // Rehabilitar input y botón
                input.disabled = false;
                sendButton.disabled = false;
                input.focus();
                
                // Scroll al final
                chat.scrollTop = chat.scrollHeight;
            }
            
            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
            
            // Focus automático en el input
            document.getElementById('messageInput').focus();
        </script>
    </body>
    </html>
    """

@app.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint para el chat con Gemini AI."""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not GEMINI_API_KEY:
            return jsonify({
                'response': '⚠️ Error: API key de Gemini no configurada. Por favor configura GEMINI_API_KEY en las variables de entorno de Vercel.'
            })
        
        if not message:
            return jsonify({'response': 'Por favor envía un mensaje válido.'})
        
        # Configurar el modelo
        model = genai.GenerativeModel('gemini-pro')
        
        # Generar respuesta
        response = model.generate_content(message)
        
        return jsonify({
            'response': response.text if response.text else 'No pude generar una respuesta. Intenta reformular tu pregunta.'
        })
        
    except Exception as e:
        return jsonify({
            'response': f'❌ Error: {str(e)}'
        })

# Para Vercel
if __name__ == '__main__':
    app.run(debug=True)