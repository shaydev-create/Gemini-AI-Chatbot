/**
 *  Gemini AI Chatbot - Main JavaScript
 * Funcionalidades principales del chatbot
 */

// Configuración global
const CONFIG = {
    API_BASE_URL: '/api',
    MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
    SUPPORTED_FORMATS: ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
};

// Estado global de la aplicación
const AppState = {
    isConnected: false,
    currentConversation: null,
    user: null,
    theme: localStorage.getItem('theme') || 'light'
};

/**
 * Inicialización de la aplicación
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log(' Gemini AI Chatbot iniciado');
    initializeTheme();
    initializeServiceWorker();
    initializeEventListeners();
    checkAuthentication();
});

/**
 * Inicializar tema
 */
function initializeTheme() {
    document.documentElement.setAttribute('data-theme', AppState.theme);
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
}

/**
 * Alternar tema
 */
function toggleTheme() {
    AppState.theme = AppState.theme === 'light' ? 'dark' : 'light';
    localStorage.setItem('theme', AppState.theme);
    document.documentElement.setAttribute('data-theme', AppState.theme);
}

/**
 * Inicializar Service Worker para PWA
 */
function initializeServiceWorker() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/sw.js')
            .then(registration => {
                console.log(' Service Worker registrado:', registration);
            })
            .catch(error => {
                console.error(' Error registrando Service Worker:', error);
            });
    }
}

/**
 * Inicializar event listeners
 */
function initializeEventListeners() {
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', handleChatSubmit);
    }
    
    const fileInput = document.getElementById('file-input');
    if (fileInput) {
        fileInput.addEventListener('change', handleFileUpload);
    }
    
    const clearButton = document.getElementById('clear-chat');
    if (clearButton) {
        clearButton.addEventListener('click', clearChat);
    }
}

// Exportar para uso global
window.GeminiChatbot = {
    CONFIG,
    AppState
};
