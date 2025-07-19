from flask import Flask, request, jsonify
import os
import google.generativeai as genai

app = Flask(__name__)

# Configurar Gemini
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

@app.route('/')
def home():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Gemini AI Chatbot</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial; margin: 0; padding: 20px; background: #f0f2f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { background: #4267B2; color: white; padding: 20px; text-align: center; }
        .chat { height: 400px; overflow-y: auto; padding: 20px; border-bottom: 1px solid #eee; }
        .input-area { padding: 20px; display: flex; gap: 10px; }
        input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 20px; outline: none; }
        button { padding: 10px 20px; background: #4267B2; color: white; border: none; border-radius: 20px; cursor: pointer; }
        .message { margin: 10px 0; padding: 10px 15px; border-radius: 15px; max-width: 80%; }
        .user { background: #4267B2; color: white; margin-left: auto; text-align: right; }
        .bot { background: #f1f3f4; color: #333; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>🤖 Gemini AI Chatbot</h2>
            <p>Tu asistente inteligente</p>
        </div>
        <div id="chat" class="chat">
            <div class="message bot">¡Hola! Soy tu asistente AI. ¿En qué puedo ayudarte?</div>
        </div>
        <div class="input-area">
            <input type="text" id="input" placeholder="Escribe tu mensaje..." onkeypress="if(event.key==='Enter') send()">
            <button onclick="send()">Enviar</button>
        </div>
    </div>

    <script>
        async function send() {
            const input = document.getElementById('input');
            const chat = document.getElementById('chat');
            const message = input.value.trim();
            
            if (!message) return;
            
            chat.innerHTML += `<div class="message user">${message}</div>`;
            input.value = '';
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message})
                });
                const data = await response.json();
                chat.innerHTML += `<div class="message bot">${data.response}</div>`;
            } catch (error) {
                chat.innerHTML += `<div class="message bot">Error: No se pudo conectar</div>`;
            }
            
            chat.scrollTop = chat.scrollHeight;
        }
    </script>
</body>
</html>
    '''

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not GEMINI_API_KEY:
            return jsonify({'response': 'Error: Configura GEMINI_API_KEY en Vercel'})
        
        if not message:
            return jsonify({'response': 'Envía un mensaje válido'})
        
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(message)
        
        return jsonify({'response': response.text or 'No pude responder'})
        
    except Exception as e:
        return jsonify({'response': f'Error: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)