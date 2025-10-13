// 🚀 Gemini AI Futuristic Chatbot - Content Script with Chrome Built-in AI
// Se ejecuta en el contexto de las páginas web visitadas por el usuario.

'use strict';

// Chrome Built-in AI integration
let chromeAI = null;
let isAIReady = false;

// Initialize Chrome AI
const initializeChromeAI = async () => {
    try {
        // Check if Chrome Built-in AI is available
        if (typeof LanguageModel !== 'undefined') {
            const availability = await LanguageModel.availability();
            if (availability !== 'unavailable') {
                const session = await LanguageModel.create({
                    temperature: 0.7,
                    topK: 40,
                    initialPrompts: [{
                        role: 'system',
                        content: 'You are a helpful AI assistant that can analyze web page content and provide insights.'
                    }]
                });
                chromeAI = session;
                isAIReady = true;
                log('info', '🧠 Chrome Built-in AI initialized successfully');
                return true;
            }
        }
        return false;
    } catch (error) {
        log('error', 'Failed to initialize Chrome AI:', error);
        return false;
    }
};

// Initialize on load
initializeChromeAI();

// --- Logging ---
const log = (level, ...args) => {
    const prefix = `[Gemini AI Content Script - ${level.toUpperCase()}]`;
    console.log(prefix, ...args);
};

log('info', 'Script inyectado en la página con Chrome AI support.');

// --- Manejador de Mensajes del Service Worker ---
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    log('info', 'Mensaje recibido:', request.action);

    const handler = messageHandlers[request.action];
    if (handler) {
        try {
            // Check if it's an async handler
            const result = handler(request.data);
            if (result instanceof Promise) {
                result.then(data => {
                    if (sendResponse) sendResponse({ success: true, data });
                }).catch(error => {
                    if (sendResponse) sendResponse({ success: false, error: error.message });
                });
                return true; // Will respond asynchronously
            } else {
                if (sendResponse) sendResponse({ success: true, data: result });
                return false;
            }
        } catch (error) {
            log('error', `Error en la acción '${request.action}':`, error.message);
            if (sendResponse) sendResponse({ success: false, error: error.message });
            return false;
        }
    } else {
        log('warn', 'Acción no reconocida:', request.action);
        if (sendResponse) sendResponse({ success: false, error: 'Acción no reconocida en content.js' });
        return false;
    }
});

// --- Handlers de Acciones ---
const messageHandlers = {
    /**
     * Extrae el contenido principal de la página para ser analizado.
     * Intenta ser inteligente al seleccionar el contenido relevante.
     */
    extractPageContent: () => {
        log('info', 'Extrayendo contenido de la página...');
        
        // Estrategia 1: Buscar el elemento <main>
        const mainElement = document.querySelector('main');
        if (mainElement) {
            log('info', 'Contenido extraído desde el elemento <main>.');
            return mainElement.innerText;
        }

        // Estrategia 2: Buscar un elemento con role="main"
        const roleMainElement = document.querySelector('[role="main"]');
        if (roleMainElement) {
            log('info', 'Contenido extraído desde el elemento [role="main"].');
            return roleMainElement.innerText;
        }

        // Estrategia 3: Buscar el artículo principal si existe
        const articleElement = document.querySelector('article');
        if (articleElement) {
            log('info', 'Contenido extraído desde el elemento <article>.');
            return articleElement.innerText;
        }

        // Estrategia 4: Como último recurso, usar el cuerpo del documento,
        // pero intentando limpiar el ruido (nav, header, footer).
        const bodyClone = document.body.cloneNode(true);
        const selectorsToRemove = 'nav, header, footer, aside, script, style, [role="navigation"], [role="banner"], [role="contentinfo"]';
        bodyClone.querySelectorAll(selectorsToRemove).forEach(el => el.remove());
        
        log('warn', 'Usando estrategia de último recurso: innerText del body clonado y limpiado.');
        return bodyClone.innerText || document.body.innerText;
    },

    /**
     * Summarize page content using Chrome Built-in AI
     */
    summarizePage: async () => {
        if (!isAIReady) {
            throw new Error('Chrome AI not available');
        }

        const content = messageHandlers.extractPageContent();
        const prompt = `Please provide a concise summary of the following web page content:\n\n${content.substring(0, 2000)}`;
        
        try {
            const summary = await chromeAI.prompt(prompt);
            log('info', 'Page summarized using Chrome AI');
            return summary;
        } catch (error) {
            log('error', 'Chrome AI summarization failed:', error);
            throw error;
        }
    },

    /**
     * Extract key information from page using Chrome Built-in AI
     */
    extractKeyInfo: async () => {
        if (!isAIReady) {
            throw new Error('Chrome AI not available');
        }

        const content = messageHandlers.extractPageContent();
        const prompt = `Extract the key information, main points, and important details from this web page content. Format as bullet points:\n\n${content.substring(0, 2000)}`;
        
        try {
            const keyInfo = await chromeAI.prompt(prompt);
            log('info', 'Key information extracted using Chrome AI');
            return keyInfo;
        } catch (error) {
            log('error', 'Chrome AI key info extraction failed:', error);
            throw error;
        }
    },

    /**
     * Translate page content using Chrome Built-in AI
     */
    translateContent: async (data) => {
        if (!isAIReady) {
            throw new Error('Chrome AI not available');
        }

        const { text, targetLanguage = 'English' } = data;
        const content = text || messageHandlers.extractPageContent().substring(0, 1500);
        const prompt = `Translate the following text to ${targetLanguage}:\n\n${content}`;
        
        try {
            const translation = await chromeAI.prompt(prompt);
            log('info', `Content translated to ${targetLanguage} using Chrome AI`);
            return translation;
        } catch (error) {
            log('error', 'Chrome AI translation failed:', error);
            throw error;
        }
    },

    /**
     * Analyze page sentiment using Chrome Built-in AI
     */
    analyzeSentiment: async () => {
        if (!isAIReady) {
            throw new Error('Chrome AI not available');
        }

        const content = messageHandlers.extractPageContent();
        const prompt = `Analyze the sentiment and tone of this web page content. Provide a brief analysis including whether it's positive, negative, or neutral, and explain why:\n\n${content.substring(0, 1500)}`;
        
        try {
            const analysis = await chromeAI.prompt(prompt);
            log('info', 'Sentiment analyzed using Chrome AI');
            return analysis;
        } catch (error) {
            log('error', 'Chrome AI sentiment analysis failed:', error);
            throw error;
        }
    },

    /**
     * Generate questions about the page content using Chrome Built-in AI
     */
    generateQuestions: async () => {
        if (!isAIReady) {
            throw new Error('Chrome AI not available');
        }

        const content = messageHandlers.extractPageContent();
        const prompt = `Based on this web page content, generate 5 thoughtful questions that would help someone better understand the topic:\n\n${content.substring(0, 1500)}`;
        
        try {
            const questions = await chromeAI.prompt(prompt);
            log('info', 'Questions generated using Chrome AI');
            return questions;
        } catch (error) {
            log('error', 'Chrome AI question generation failed:', error);
            throw error;
        }
    },

    /**
     * Check Chrome AI availability
     */
    checkAIAvailability: () => {
        return {
            available: isAIReady,
            apis: {
                prompt: typeof LanguageModel !== 'undefined',
                summarizer: typeof SummarizerAPI !== 'undefined',
                writer: typeof WriterAPI !== 'undefined',
                rewriter: typeof RewriterAPI !== 'undefined',
                translator: typeof TranslatorAPI !== 'undefined',
                proofreader: typeof ProofreaderAPI !== 'undefined'
            }
        };
    },

    /**
     * Proofread selected text using Chrome Built-in AI
     */
    proofreadText: async (data) => {
        if (!isAIReady) {
            throw new Error('Chrome AI not available');
        }

        const { text } = data;
        if (!text) {
            throw new Error('No text provided for proofreading');
        }

        const prompt = `Please proofread and correct the following text, fixing any grammar, spelling, or punctuation errors while maintaining the original meaning and style:\n\n${text}`;
        
        try {
            const correctedText = await chromeAI.prompt(prompt);
            log('info', 'Text proofread using Chrome AI');
            return correctedText;
        } catch (error) {
            log('error', 'Chrome AI proofreading failed:', error);
            throw error;
        }
    }
};

log('info', 'Content script listo y escuchando mensajes con Chrome AI support.');