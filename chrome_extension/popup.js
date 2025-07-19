// 🚀 Gemini AI Futuristic Chatbot - Popup Script
document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const statusElement = document.getElementById('status');
    const statusText = document.getElementById('statusText');
    const openChatBtn = document.getElementById('openChatBtn');
    const newTabBtn = document.getElementById('newTabBtn');
    const helpBtn = document.getElementById('helpBtn');

    // URL de la aplicación local
    const APP_URL = 'https://127.0.0.1:5000';

    // Verificar estado de conexión
    async function checkConnectionStatus() {
        try {
            // Intentar conectar al servidor local
            const response = await fetch(APP_URL, { 
                method: 'HEAD',
                mode: 'no-cors'
            });
            updateStatus('online', '✅ Servidor local conectado');
            enableButtons(true);
            return true;
        } catch (error) {
            updateStatus('offline', '❌ Servidor local no disponible');
            enableButtons(false);
            return false;
        }
    }

    // Actualizar estado visual
    function updateStatus(status, message) {
        statusElement.className = `status ${status}`;
        statusText.textContent = message;
    }

    // Habilitar/deshabilitar botones
    function enableButtons(enabled) {
        openChatBtn.disabled = !enabled;
        newTabBtn.disabled = !enabled;
    }

    // Abrir chatbot en nueva pestaña
    function openChat() {
        chrome.tabs.create({ 
            url: APP_URL,
            active: true
        });
        window.close();
    }

    // Abrir nueva pestaña con la aplicación
    function openNewTab() {
        chrome.tabs.create({ 
            url: APP_URL,
            active: true
        });
        window.close();
    }

    // Mostrar ayuda
    function showHelp() {
        const helpText = `🚀 Gemini AI Futuristic Chatbot

📋 Instrucciones:
1. Asegúrate de que tu servidor local esté ejecutándose
2. Ejecuta: python app.py
3. El servidor debe estar en: https://127.0.0.1:5000
4. Haz clic en "Abrir Chatbot" para comenzar

🔧 Requisitos:
• Python 3.8+
• Google Gemini API Key configurada
• Certificados SSL (generados automáticamente)

💡 Funciones:
• Chat inteligente con IA
• Análisis de documentos
• Síntesis de voz
• Interfaz futurista

¿Necesitas ayuda? Revisa el README.md del proyecto.`;
        
        alert(helpText);
    }

    // Event listeners
    openChatBtn.addEventListener('click', openChat);
    newTabBtn.addEventListener('click', openNewTab);
    helpBtn.addEventListener('click', showHelp);

    // Verificar conexión al cargar
    checkConnectionStatus();

    // Verificar conexión cada 10 segundos
    setInterval(checkConnectionStatus, 10000);

    console.log('🚀 Popup de Gemini AI Chatbot cargado');
});

// Manejar errores globales
window.addEventListener('error', function(e) {
    console.error('❌ Error en popup:', e.error);
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('❌ Promise rechazada:', e.reason);
});