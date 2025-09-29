// 🚀 Gemini AI Futuristic Chatbot - Background Script
// Service Worker para Chrome Extension

console.log('🚀 Gemini AI Chatbot - Background script iniciado');

// Configuración del chatbot
const CHATBOT_CONFIG = {
    name: '🚀 Gemini AI Futuristic Chatbot',
    version: '1.0.3',
    description: 'Asistente de IA independiente con Google Gemini'
};

// Evento de instalación
chrome.runtime.onInstalled.addListener((details) => {
    console.log('✅ Extensión instalada:', details.reason);
    
    if (details.reason === 'install') {
        console.log('🎉 Primera instalación del Gemini AI Chatbot');
        
        // Mostrar página de bienvenida
        chrome.tabs.create({
            url: chrome.runtime.getURL('welcome.html')
        });
    }
    
    if (details.reason === 'update') {
        console.log('🔄 Extensión actualizada');
    }
});

// Manejar mensajes del popup y content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('📨 Mensaje recibido:', request);
    
    switch (request.action) {
        case 'getConfig':
            sendResponse({
                success: true,
                config: CHATBOT_CONFIG
            });
            break;
            
        case 'getApiKey':
            // Obtener API key del storage
            chrome.storage.sync.get(['geminiApiKey'], (result) => {
                sendResponse({
                    success: true,
                    apiKey: result.geminiApiKey || null
                });
            });
            return true; // Mantener el canal abierto para respuesta asíncrona
            
        case 'saveApiKey':
            // Guardar API key en storage
            chrome.storage.sync.set({ geminiApiKey: request.apiKey }, () => {
                sendResponse({
                    success: true,
                    message: 'API Key guardada correctamente'
                });
            });
            return true;
            
        case 'clearData':
            // Limpiar todos los datos almacenados
            chrome.storage.sync.clear(() => {
                sendResponse({
                    success: true,
                    message: 'Datos limpiados correctamente'
                });
            });
            return true;
            sendResponse({ success: true });
            break;
            
        case 'checkServer':
            // Verificar si el servidor está disponible
            fetch(CHATBOT_CONFIG.serverUrl)
                .then(response => {
                    sendResponse({ 
                        success: true, 
                        serverAvailable: response.ok 
                    });
                })
                .catch(() => {
                    sendResponse({ 
                        success: true, 
                        serverAvailable: false 
                    });
                });
            return true; // Mantener el canal abierto para respuesta asíncrona
            
        default:
            sendResponse({ success: false, error: 'Acción no reconocida' });
    }
});

// Evento de inicio
chrome.runtime.onStartup.addListener(() => {
    console.log('🔄 Chrome iniciado - Gemini AI Chatbot listo');
});

console.log('✅ Background script configurado correctamente');