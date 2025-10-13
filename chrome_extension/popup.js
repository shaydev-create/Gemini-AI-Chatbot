// 🚀 Gemini AI Futuristic Chatbot - popup.js
// Lógica de la interfaz de usuario para la extensión

'use strict';

// --- Elementos del DOM ---
const dom = {
    views: {
        settings: document.getElementById('settingsView'),
        chat: document.getElementById('chatView'),
    },
    buttons: {
        settings: document.getElementById('settingsButton'),
        saveApiKey: document.getElementById('saveApiKey'),
        backToChat: document.getElementById('backToChat'),
        send: document.getElementById('sendButton'),
    },
    inputs: {
        apiKey: document.getElementById('apiKeyInput'),
        message: document.getElementById('messageInput'),
    },
    containers: {
        messages: document.getElementById('chatMessages'),
    },
    status: {
        server: {
            light: document.querySelector('#serverStatus .status-light'),
            text: document.getElementById('serverStatusText'),
        },
        connection: {
            light: document.getElementById('connectionLight'),
            text: document.getElementById('connectionText'),
        },
    },
};

// --- Estado de la Aplicación ---
const state = {
    apiKey: null,
    serverOnline: false,
    currentView: 'chat',
    conversation: [],
    typing: false,
};

// --- Comunicación con el Service Worker ---
const api = {
    sendMessage: (action, data = {}) => {
        return new Promise((resolve, reject) => {
            chrome.runtime.sendMessage({ action, data }, (response) => {
                if (chrome.runtime.lastError) {
                    return reject(chrome.runtime.lastError);
                }
                if (response && response.success) {
                    resolve(response.data);
                } else {
                    reject(new Error(response ? response.error : 'Respuesta inválida del Service Worker'));
                }
            });
        });
    },
};

// --- Lógica de la Interfaz ---

/**
 * Cambia la vista activa en la interfaz.
 * @param {string} viewName - 'chat' o 'settings'.
 */
function switchView(viewName) {
    state.currentView = viewName;
    Object.values(dom.views).forEach(view => view.classList.remove('active'));
    if (dom.views[viewName]) {
        dom.views[viewName].classList.add('active');
    }
    // Si cambiamos a la vista de configuración, actualizamos el estado del servidor
    if (viewName === 'settings') {
        updateServerStatus();
    }
}

/**
 * Añade un mensaje al contenedor de chat.
 * @param {string} text - El contenido del mensaje.
 * @param {string} sender - 'user', 'ai', o 'error'.
 */
function addMessage(text, sender) {
    const messageEl = document.createElement('div');
    messageEl.classList.add('message', `${sender}-message`);
    messageEl.textContent = text;
    dom.containers.messages.appendChild(messageEl);
    scrollToBottom();
}

/**
 * Muestra u oculta el indicador de "escribiendo".
 * @param {boolean} isTyping - True para mostrar, false para ocultar.
 */
function setTypingIndicator(isTyping) {
    if (isTyping === state.typing) return;
    state.typing = isTyping;

    const existingIndicator = dom.containers.messages.querySelector('.typing-indicator');
    if (isTyping) {
        if (!existingIndicator) {
            const indicatorEl = document.createElement('div');
            indicatorEl.className = 'message ai-message typing-indicator';
            indicatorEl.innerHTML = '<span></span><span></span><span></span>';
            dom.containers.messages.appendChild(indicatorEl);
            scrollToBottom();
        }
    } else {
        if (existingIndicator) {
            existingIndicator.remove();
        }
    }
}

/**
 * Desplaza el contenedor de mensajes hasta el final.
 */
function scrollToBottom() {
    dom.containers.messages.scrollTop = dom.containers.messages.scrollHeight;
}

/**
 * Actualiza el estado de la conexión (API Key).
 */
function updateConnectionStatus() {
    if (state.apiKey) {
        dom.status.connection.light.classList.add('online');
        dom.status.connection.text.textContent = 'API Key activa';
    } else {
        dom.status.connection.light.classList.remove('online');
        dom.status.connection.text.textContent = 'API Key requerida';
    }
}

/**
 * Actualiza el estado del servidor backend en la vista de configuración.
 */
async function updateServerStatus() {
    try {
        const status = await api.sendMessage('checkServerStatus');
        state.serverOnline = status.serverOnline;
        if (status.serverOnline) {
            dom.status.server.light.classList.add('online');
            dom.status.server.text.textContent = `Online (${status.message})`;
        } else {
            dom.status.server.light.classList.remove('online');
            dom.status.server.text.textContent = 'Offline';
        }
    } catch (error) {
        state.serverOnline = false;
        dom.status.server.light.classList.remove('online');
        dom.status.server.text.textContent = 'Error al verificar';
    }
}

// --- Manejadores de Eventos ---

async function handleSendMessage() {
    const messageText = dom.inputs.message.value.trim();
    if (!messageText) return;

    addMessage(messageText, 'user');
    state.conversation.push({ role: 'user', text: messageText });
    dom.inputs.message.value = '';
    dom.buttons.send.disabled = true;
    setTypingIndicator(true);

    try {
        // Esta es una llamada simulada. En una implementación real,
        // enviaríamos el mensaje al backend a través del service worker.
        // const response = await api.sendMessage('sendChatMessage', { conversation: state.conversation });
        
        // Simulación de respuesta de la IA
        await new Promise(resolve => setTimeout(resolve, 1500));
        const response = `Esta es una respuesta simulada para: "${messageText}"`;

        addMessage(response, 'ai');
        state.conversation.push({ role: 'ai', text: response });

    } catch (error) {
        addMessage(`Error: ${error.message}`, 'error');
    } finally {
        setTypingIndicator(false);
        dom.buttons.send.disabled = false;
        dom.inputs.message.focus();
    }
}

async function handleSaveApiKey() {
    const newApiKey = dom.inputs.apiKey.value.trim();
    if (!newApiKey) {
        addMessage('Por favor, ingresa una API Key.', 'error');
        return;
    }

    try {
        await api.sendMessage('saveApiKey', { apiKey: newApiKey });
        state.apiKey = newApiKey;
        updateConnectionStatus();
        addMessage('API Key guardada correctamente.', 'ai');
        switchView('chat');
    } catch (error) {
        addMessage(`Error al guardar la API Key: ${error.message}`, 'error');
    }
}

// --- Chrome AI Handlers ---

async function handleChromeAI(action) {
    try {
        setAIButtonsEnabled(false);
        addMessage(`🧠 Processing with Chrome AI...`, 'system');
        
        const result = await sendToActiveTab(action);
        
        if (result.success) {
            addMessage(result.data, 'ai');
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        addMessage(`❌ Chrome AI Error: ${error.message}`, 'error');
    } finally {
        setAIButtonsEnabled(true);
    }
}

async function handleProofread() {
    try {
        // Get selected text from the page
        const selectedText = await getSelectedText();
        
        if (!selectedText || selectedText.trim().length === 0) {
            addMessage('❓ Please select some text on the page to proofread.', 'system');
            return;
        }
        
        setAIButtonsEnabled(false);
        addMessage(`🧠 Proofreading selected text...`, 'system');
        
        const result = await sendToActiveTab('proofreadText', { text: selectedText });
        
        if (result.success) {
            addMessage(`✏️ **Original:** ${selectedText}\n\n**Corrected:** ${result.data}`, 'ai');
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        addMessage(`❌ Proofreading Error: ${error.message}`, 'error');
    } finally {
        setAIButtonsEnabled(true);
    }
}

async function sendToActiveTab(action, data = {}) {
    return new Promise((resolve) => {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (tabs[0]) {
                chrome.tabs.sendMessage(tabs[0].id, { action, data }, (response) => {
                    if (chrome.runtime.lastError) {
                        resolve({ success: false, error: chrome.runtime.lastError.message });
                    } else {
                        resolve(response || { success: false, error: 'No response from content script' });
                    }
                });
            } else {
                resolve({ success: false, error: 'No active tab found' });
            }
        });
    });
}

async function getSelectedText() {
    return new Promise((resolve) => {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (tabs[0]) {
                chrome.tabs.executeScript(tabs[0].id, {
                    code: 'window.getSelection().toString();'
                }, (result) => {
                    if (chrome.runtime.lastError) {
                        resolve('');
                    } else {
                        resolve(result && result[0] ? result[0] : '');
                    }
                });
            } else {
                resolve('');
            }
        });
    });
}

function setAIButtonsEnabled(enabled) {
    const buttons = ['summarizeBtn', 'keyInfoBtn', 'translateBtn', 'sentimentBtn', 'questionsBtn', 'proofreadBtn'];
    buttons.forEach(buttonId => {
        const button = document.getElementById(buttonId);
        if (button) {
            button.disabled = !enabled;
        }
    });
}

async function checkChromeAIAvailability() {
    try {
        const result = await sendToActiveTab('checkAIAvailability');
        const statusElement = document.getElementById('aiStatusText');
        
        if (result.success && result.data.available) {
            statusElement.textContent = '🧠 Chrome AI Available';
            statusElement.parentElement.className = 'ai-status available';
            setAIButtonsEnabled(true);
        } else {
            statusElement.textContent = '❌ Chrome AI Unavailable';
            statusElement.parentElement.className = 'ai-status unavailable';
            setAIButtonsEnabled(false);
        }
    } catch (error) {
        console.error('Failed to check Chrome AI availability:', error);
        const statusElement = document.getElementById('aiStatusText');
        statusElement.textContent = '⚠️ Chrome AI Status Unknown';
        statusElement.parentElement.className = 'ai-status';
    }
}

// --- Inicialización ---

function setupEventListeners() {
    dom.buttons.settings.addEventListener('click', () => switchView('settings'));
    dom.buttons.backToChat.addEventListener('click', () => switchView('chat'));
    dom.buttons.saveApiKey.addEventListener('click', handleSaveApiKey);
    dom.buttons.send.addEventListener('click', handleSendMessage);
    dom.inputs.message.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });
    
    // Chrome AI buttons
    setupChromeAIEventListeners();
}

function setupChromeAIEventListeners() {
    const aiButtons = {
        summarize: document.getElementById('summarizeBtn'),
        keyInfo: document.getElementById('keyInfoBtn'),
        translate: document.getElementById('translateBtn'),
        sentiment: document.getElementById('sentimentBtn'),
        questions: document.getElementById('questionsBtn'),
        proofread: document.getElementById('proofreadBtn')
    };
    
    if (aiButtons.summarize) {
        aiButtons.summarize.addEventListener('click', () => handleChromeAI('summarizePage'));
    }
    if (aiButtons.keyInfo) {
        aiButtons.keyInfo.addEventListener('click', () => handleChromeAI('extractKeyInfo'));
    }
    if (aiButtons.translate) {
        aiButtons.translate.addEventListener('click', () => handleChromeAI('translateContent'));
    }
    if (aiButtons.sentiment) {
        aiButtons.sentiment.addEventListener('click', () => handleChromeAI('analyzeSentiment'));
    }
    if (aiButtons.questions) {
        aiButtons.questions.addEventListener('click', () => handleChromeAI('generateQuestions'));
    }
    if (aiButtons.proofread) {
        aiButtons.proofread.addEventListener('click', () => handleProofread());
    }
}

async function initialize() {
    setupEventListeners();
    
    // Check Chrome AI availability
    await checkChromeAIAvailability();
    
    try {
        state.apiKey = await api.sendMessage('getApiKey');
        if (!state.apiKey) {
            switchView('settings');
            addMessage('🔧 Welcome! Please configure your Google Gemini API Key to start using cloud AI features.', 'ai');
            addMessage('💡 Chrome Built-in AI features are available without API key configuration.', 'system');
        } else {
            switchView('chat');
            addMessage('🚀 Hello! I can help you with both local Chrome AI and cloud Gemini features. What would you like to do?', 'ai');
        }
    } catch (error) {
        switchView('settings');
        addMessage(`❌ Initialization error: ${error.message}. Please configure your API Key for cloud features.`, 'error');
        addMessage('💡 Chrome Built-in AI features may still be available.', 'system');
    }
    updateConnectionStatus();
}

// Iniciar la aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', initialize);