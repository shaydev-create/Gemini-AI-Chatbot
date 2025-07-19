// 🚀 Gemini AI Futuristic Chatbot - Background Script
// Service Worker para Chrome Extension

console.log('🚀 Gemini AI Chatbot - Background script iniciado');

// Configuración del chatbot
const CHATBOT_CONFIG = {
    name: '🚀 Gemini AI Futuristic Chatbot',
    version: '1.0.0',
    serverUrl: 'https://127.0.0.1:5000'
};

// Evento de instalación
chrome.runtime.onInstalled.addListener((details) => {
    console.log('✅ Extensión instalada:', details.reason);
    
    if (details.reason === 'install') {
        // Primera instalación
        console.log('🎉 Primera instalación del Gemini AI Chatbot');
        
        // Configurar datos iniciales
        chrome.storage.local.set({
            'chatbot_installed': true,
            'install_date': new Date().toISOString(),
            'version': CHATBOT_CONFIG.version
        });
    }
});

// Evento de activación de la extensión
chrome.action.onClicked.addListener((tab) => {
    console.log('🖱️ Icono de extensión clickeado');
    
    // Abrir popup (esto se maneja automáticamente por el manifest)
    // Solo registramos el evento para analytics
    chrome.storage.local.get(['usage_count'], (result) => {
        const count = (result.usage_count || 0) + 1;
        chrome.storage.local.set({ 'usage_count': count });
        console.log(`📊 Uso #${count} del chatbot`);
    });
});

// Manejar mensajes del popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('📨 Mensaje recibido:', request);
    
    switch (request.action) {
        case 'getConfig':
            sendResponse({
                success: true,
                config: CHATBOT_CONFIG
            });
            break;
            
        case 'openChatbot':
            // Abrir el chatbot en una nueva pestaña
            chrome.tabs.create({
                url: CHATBOT_CONFIG.serverUrl,
                active: true
            });
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