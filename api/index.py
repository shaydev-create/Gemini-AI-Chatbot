"""
Vercel serverless function entry point for Gemini AI Chatbot
"""
import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

# Configurar Gemini AI
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Crear aplicación Flask
app = Flask(__name__, 
           template_folder='../app/templates',
           static_folder='../app/static')

@app.route('/')
def index():
    """Página principal del chatbot."""
    try:
        return render_template('index.html')
    except Exception as e:
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>🚀 Gemini AI Chatbot</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1 {{ color: #4285f4; text-align: center; }}
                .chat-container {{ border: 1px solid #ddd; height: 400px; overflow-y: auto; padding: 20px; margin: 20px 0; border-radius: 5px; background: #fafafa; }}
                .input-container {{ display: flex; gap: 10px; }}
                input {{ flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
                button {{ padding: 10px 20px; background: #4285f4; color: white; border: none; border-radius: 5px; cursor: pointer; }}
                button:hover {{ background: #3367d6; }}
                .message {{ margin: 10px 0; padding: 10px; border-radius: 5px; }}
                .user {{ background: #e3f2fd; text-align: right; }}
                .bot {{ background: #f1f8e9; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 Gemini AI Chatbot</h1>
                <div id="chat" class="chat-container">
                    <div class="message bot">¡Hola! Soy tu asistente AI. ¿En qué puedo ayudarte?</div>
                </div>
                <div class="input-container">
                    <input type="text" id="messageInput" placeholder="Escribe tu mensaje aquí..." onkeypress="if(event.key==='Enter') sendMessage()">
                    <button onclick="sendMessage()">Enviar</button>
                </div>
            </div>
            
            <script>
                async function sendMessage() {{
                    const input = document.getElementById('messageInput');
                    const chat = document.getElementById('chat');
                    const message = input.value.trim();
                    
                    if (!message) return;
                    
                    // Mostrar mensaje del usuario
                    chat.innerHTML += `<div class="message user">${{message}}</div>`;
                    input.value = '';
                    
                    try {{
                        const response = await fetch('/api/chat', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{ message: message }})
                        }});
                        
                        const data = await response.json();
                        chat.innerHTML += `<div class="message bot">${{data.response || 'Error en la respuesta'}}</div>`;
                    }} catch (error) {{
                        chat.innerHTML += `<div class="message bot">Error: No se pudo conectar con el servidor</div>`;
                    }}
                    
                    chat.scrollTop = chat.scrollHeight;
                }}
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
                'response': 'Error: API key de Gemini no configurada. Por favor configura GEMINI_API_KEY en las variables de entorno.'
            })
        
        if not message:
            return jsonify({'response': 'Por favor envía un mensaje válido.'})
        
        # Configurar el modelo
        model = genai.GenerativeModel('gemini-pro')
        
        # Generar respuesta
        response = model.generate_content(message)
        
        return jsonify({
            'response': response.text if response.text else 'No pude generar una respuesta.'
        })
        
    except Exception as e:
        return jsonify({
            'response': f'Error: {str(e)}'
        })

# Para Vercel
if __name__ == '__main__':
    app.run(debug=True)