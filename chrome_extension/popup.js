// 🚀 Gemini AI Futuristic Chatbot - Popup Script
// Funcionalidad completa del chatbot en la extensión

let apiKey = '';
let conversationHistory = [];

// Inicializar cuando se carga el popup
document.addEventListener('DOMContentLoaded', function() {
    initializePopup();
});

// Inicializar la interfaz del popup
async function initializePopup() {
    try {
        // Cargar API key guardada
        const result = await chrome.storage.sync.get(['geminiApiKey']);
        
        if (result.geminiApiKey) {
            apiKey = result.geminiApiKey;
            showChatInterface();
        } else {
            showSetupInterface();
        }
        
        // Configurar event listeners
        setupEventListeners();
        
    } catch (error) {
        console.error('Error inicializando popup:', error);
        showError('Error al inicializar la extensión');
    }
}

// Configurar event listeners
function setupEventListeners() {
    // Botón para guardar API key
    const saveButton = document.getElementById('saveApiKey');
    if (saveButton) {
        saveButton.addEventListener('click', saveApiKey);
    }
    
    // Input de API key (Enter para guardar)
    const apiKeyInput = document.getElementById('apiKeyInput');
    if (apiKeyInput) {
        apiKeyInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                saveApiKey();
            }
        });
    }
    
    // Botón de enviar mensaje
    const sendButton = document.getElementById('sendButton');
    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }
    
    // Input de mensaje (Enter para enviar)
    const messageInput = document.getElementById('messageInput');
    if (messageInput) {
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
}

// Mostrar interfaz de configuración
function showSetupInterface() {
    const setupContainer = document.getElementById('setupContainer');
    const chatInterface = document.getElementById('chatInterface');
    
    if (setupContainer) setupContainer.style.display = 'block';
    if (chatInterface) chatInterface.style.display = 'none';
}

// Mostrar interfaz de chat
function showChatInterface() {
    const setupContainer = document.getElementById('setupContainer');
    const chatInterface = document.getElementById('chatInterface');
    
    if (setupContainer) setupContainer.style.display = 'none';
    if (chatInterface) chatInterface.style.display = 'block';
    
    // Mostrar mensaje de bienvenida si es la primera vez
    if (conversationHistory.length === 0) {
        addWelcomeMessage();
    }
}

// Guardar API key
async function saveApiKey() {
    const apiKeyInput = document.getElementById('apiKeyInput');
    const setupError = document.getElementById('setupError');
    
    if (!apiKeyInput) return;
    
    const key = apiKeyInput.value.trim();
    
    if (!key) {
        showSetupError('Por favor ingresa una API Key válida');
        return;
    }
    
    // Validar formato básico de API key
    if (!key.startsWith('AIza') || key.length < 30) {
        showSetupError('La API Key no parece válida. Debe comenzar con "AIza"');
        return;
    }
    
    try {
        // Guardar en storage
        await chrome.storage.sync.set({ geminiApiKey: key });
        apiKey = key;
        
        // Limpiar error y mostrar chat
        if (setupError) setupError.textContent = '';
        showChatInterface();
        
    } catch (error) {
        console.error('Error guardando API key:', error);
        showSetupError('Error al guardar la API Key');
    }
}

// Mostrar error en configuración
function showSetupError(message) {
    const setupError = document.getElementById('setupError');
    if (setupError) {
        setupError.textContent = message;
    }
}

// Agregar mensaje de bienvenida
function addWelcomeMessage() {
    const welcomeText = `¡Hola! 👋 Soy tu asistente de IA con Google Gemini.

Puedo ayudarte con:
• Responder preguntas
• Explicar conceptos
• Ayudar con tareas
• Generar contenido
• Y mucho más

¿En qué puedo ayudarte hoy?`;

    addMessage(welcomeText, 'ai');
}

// Enviar mensaje al chatbot
async function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    
    if (!messageInput || !sendButton) return;
    
    const message = messageInput.value.trim();
    
    if (!message) return;
    
    // Mostrar mensaje del usuario
    addMessage(message, 'user');
    messageInput.value = '';
    
    // Deshabilitar interfaz mientras se procesa
    setLoadingState(true);
    
    try {
        // Agregar mensaje a historial
        conversationHistory.push({
            role: 'user',
            parts: [{ text: message }]
        });
        
        // Llamar a la API de Gemini
        const response = await callGeminiAPI(message);
        
        if (response) {
            // Mostrar respuesta de la IA
            addMessage(response, 'ai');
            
            // Agregar respuesta al historial
            conversationHistory.push({
                role: 'model',
                parts: [{ text: response }]
            });
        } else {
            addMessage('Lo siento, no pude procesar tu mensaje. Inténtalo de nuevo.', 'ai');
        }
        
    } catch (error) {
        console.error('Error enviando mensaje:', error);
        addMessage('Error: ' + error.message, 'ai');
    } finally {
        setLoadingState(false);
    }
}

// Llamar a la API de Gemini
async function callGeminiAPI(message) {
    try {
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-001:generateContent?key=${apiKey}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                contents: conversationHistory.concat([{
                    role: 'user',
                    parts: [{ text: message }]
                }]),
                generationConfig: {
                    temperature: 0.7,
                    topK: 40,
                    topP: 0.95,
                    maxOutputTokens: 1024,
                }
            })
        });
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.candidates && data.candidates[0] && data.candidates[0].content) {
            return data.candidates[0].content.parts[0].text;
        } else {
            throw new Error('Respuesta inválida de la API');
        }
        
    } catch (error) {
        console.error('Error en API de Gemini:', error);
        throw error;
    }
}

// Agregar mensaje a la interfaz
function addMessage(text, sender) {
    const chatContainer = document.getElementById('chatContainer');
    if (!chatContainer) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    // Formatear texto (convertir saltos de línea)
    const formattedText = text.replace(/\n/g, '<br>');
    messageDiv.innerHTML = formattedText;
    
    chatContainer.appendChild(messageDiv);
    
    // Scroll al final
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Establecer estado de carga
function setLoadingState(loading) {
    const sendButton = document.getElementById('sendButton');
    const messageInput = document.getElementById('messageInput');
    
    if (sendButton) {
        sendButton.disabled = loading;
        sendButton.innerHTML = loading ? '<div class="loading"></div>' : 'Enviar';
    }
    
    if (messageInput) {
        messageInput.disabled = loading;
    }
}

// Mostrar error general
function showError(message) {
    addMessage(`❌ ${message}`, 'ai');
}

// Limpiar conversación (función adicional)
function clearConversation() {
    conversationHistory = [];
    const chatContainer = document.getElementById('chatContainer');
    if (chatContainer) {
        chatContainer.innerHTML = '';
        addWelcomeMessage();
    }
}

// Exportar funciones para uso en background script si es necesario
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initializePopup,
        sendMessage,
        clearConversation
    };
}