// 🚀 Gemini AI Futuristic Chatbot - Background Service Worker
// Manifest V3

'use strict';

// --- Configuración y Constantes ---
const CHATBOT_CONFIG = {
    name: '🚀 Gemini AI Futuristic Chatbot',
    version: '2.0.0', // Sincronizado con manifest.json
    serverUrl: 'http://127.0.0.1:5000', // URL del backend local
};

const WELCOME_URL = chrome.runtime.getURL('welcome.html');
const OFFLINE_REASON = 'OFFLINE_DOCUMENT_REQUEST';

// --- Logging ---
const log = (level, ...args) => {
    const prefix = `[${level.toUpperCase()}]`;
    if (level === 'error') {
        console.error(prefix, ...args);
    } else if (level === 'warn') {
        console.warn(prefix, ...args);
    } else {
        console.log(prefix, ...args);
    }
};

log('info', `Service Worker v${CHATBOT_CONFIG.version} iniciado.`);

// --- Ciclo de Vida de la Extensión ---
chrome.runtime.onInstalled.addListener(async (details) => {
    log('info', `Extensión ${details.reason}: v${chrome.runtime.getManifest().version}`);
    if (details.reason === 'install') {
        chrome.tabs.create({ url: WELCOME_URL });
    }
    // Inicializar almacenamiento o realizar migraciones si es necesario
    await initializeStorage();
});

chrome.runtime.onStartup.addListener(() => {
    log('info', 'Navegador iniciado. Gemini AI Chatbot listo.');
});

// --- Manejo de Mensajes ---
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    log('info', 'Mensaje recibido:', request.action);
    const handler = messageHandlers[request.action];

    if (handler) {
        // Usar async/await para manejar promesas de forma limpia
        (async () => {
            try {
                const response = await handler(request.data, sender);
                sendResponse({ success: true, data: response });
            } catch (error) {
                log('error', `Error en la acción '${request.action}':`, error.message);
                sendResponse({ success: false, error: error.message });
            }
        })();
        return true; // Indicar que la respuesta será asíncrona
    } else {
        log('warn', 'Acción no reconocida:', request.action);
        sendResponse({ success: false, error: 'Acción no reconocida' });
        return false;
    }
});

// --- Handlers de Acciones ---
const messageHandlers = {
    getConfig: async () => CHATBOT_CONFIG,

    getApiKey: async () => {
        const { geminiApiKey } = await chrome.storage.sync.get('geminiApiKey');
        return geminiApiKey || null;
    },

    saveApiKey: async (data) => {
        if (!data || !data.apiKey) throw new Error('API Key no proporcionada.');
        await chrome.storage.sync.set({ geminiApiKey: data.apiKey });
        return 'API Key guardada correctamente.';
    },

    clearData: async () => {
        await chrome.storage.sync.clear();
        return 'Datos de la extensión limpiados.';
    },

    checkServerStatus: async () => {
        try {
            const response = await fetch(`${CHATBOT_CONFIG.serverUrl}/api/status`);
            if (!response.ok) throw new Error(`El servidor respondió con estado: ${response.status}`);
            const data = await response.json();
            return { serverOnline: true, ...data };
        } catch (error) {
            log('warn', 'El servidor backend no está disponible:', error.message);
            return { serverOnline: false, message: 'El servidor no está accesible.' };
        }
    },

    analyzeContentWithOffscreen: async (data) => {
        if (!data || !data.html) throw new Error('HTML no proporcionado para análisis.');
        await createOffscreenDocument();
        const response = await chrome.runtime.sendMessage({
            action: 'analyzeDOM',
            target: 'offscreen',
            data: data.html,
        });
        return response;
    },
};

// --- Funciones de Utilidad ---

/**
 * Inicializa el almacenamiento con valores por defecto si no existen.
 */
async function initializeStorage() {
    const items = await chrome.storage.sync.get(['geminiApiKey', 'settings']);
    const defaults = {};
    if (!items.geminiApiKey) {
        defaults.geminiApiKey = null;
    }
    if (!items.settings) {
        defaults.settings = { theme: 'dark', language: 'es' };
    }
    if (Object.keys(defaults).length > 0) {
        await chrome.storage.sync.set(defaults);
        log('info', 'Almacenamiento inicializado con valores por defecto.');
    }
}

/**
 * Crea un documento Offscreen si no existe uno ya.
 * Esto es necesario para usar APIs del DOM que no están disponibles en Service Workers.
 */
async function createOffscreenDocument() {
    const existingContexts = await chrome.runtime.getContexts({
        contextTypes: ['OFFSCREEN_DOCUMENT'],
    });
    if (existingContexts.length > 0) {
        log('info', 'El documento Offscreen ya existe.');
        return;
    }

    log('info', 'Creando documento Offscreen...');
    await chrome.offscreen.createDocument({
        url: 'offscreen.html',
        reasons: ['DOM_PARSER'],
        justification: 'Necesario para analizar contenido HTML de la página activa.',
    });
}

log('info', 'Service Worker configurado y listo para recibir eventos.');