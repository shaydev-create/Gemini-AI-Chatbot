// 🧠 Chrome Built-in AI APIs - Implementación JavaScript
// Para integrar en tu aplicación Gemini AI Chatbot

class ChromeAIManager {
    constructor() {
        this.promptSession = null;
        this.summarizer = null;
        this.writer = null;
        this.rewriter = null;
        this.translator = null;
        this.languageDetector = null;
    }

    // 🔍 Verificar disponibilidad de Chrome AI APIs
    async checkAvailability() {
        const availability = {
            promptAPI: 'ai' in window && 'languageModel' in window.ai,
            summarizerAPI: 'ai' in window && 'summarizer' in window.ai,
            writerAPI: 'ai' in window && 'writer' in window.ai,
            rewriterAPI: 'ai' in window && 'rewriter' in window.ai,
            translatorAPI: 'translation' in window,
            languageDetection: 'translation' in window && 'languageDetector' in window.translation
        };
        
        console.log('Chrome AI Availability:', availability);
        return availability;
    }

    // 🚀 Inicializar todas las APIs
    async initialize() {
        try {
            const availability = await this.checkAvailability();
            
            // Inicializar Prompt API (ya tienes esto implementado)
            if (availability.promptAPI) {
                this.promptSession = await window.ai.languageModel.create({
                    temperature: 0.7,
                    topK: 40
                });
                console.log('✅ Prompt API initialized');
            }

            // Inicializar Summarizer API
            if (availability.summarizerAPI) {
                this.summarizer = await window.ai.summarizer.create();
                console.log('✅ Summarizer API initialized');
            }

            // Inicializar Writer API
            if (availability.writerAPI) {
                this.writer = await window.ai.writer.create();
                console.log('✅ Writer API initialized');
            }

            // Inicializar Rewriter API
            if (availability.rewriterAPI) {
                this.rewriter = await window.ai.rewriter.create();
                console.log('✅ Rewriter API initialized');
            }

            // Inicializar Language Detection
            if (availability.languageDetection) {
                this.languageDetector = await window.translation.createDetector();
                console.log('✅ Language Detector initialized');
            }

            return availability;
        } catch (error) {
            console.error('Chrome AI initialization error:', error);
            return null;
        }
    }

    // 📄 SUMMARIZER API - Resumir texto
    async summarizeText(text, options = {}) {
        try {
            if (!this.summarizer) {
                throw new Error('Summarizer API not available');
            }

            const summary = await this.summarizer.summarize(text, {
                type: options.type || 'key-points', // 'tl;dr', 'key-points', 'teaser', 'headline'
                format: options.format || 'markdown',
                length: options.length || 'medium' // 'short', 'medium', 'long'
            });

            return {
                success: true,
                summary: summary,
                originalLength: text.length,
                summaryLength: summary.length,
                compressionRatio: (summary.length / text.length * 100).toFixed(1) + '%'
            };
        } catch (error) {
            console.error('Summarizer error:', error);
            return {
                success: false,
                error: error.message,
                fallback: await this.fallbackSummarize(text)
            };
        }
    }

    // ✏️ WRITER API - Generar contenido creativo
    async generateContent(prompt, options = {}) {
        try {
            if (!this.writer) {
                throw new Error('Writer API not available');
            }

            const content = await this.writer.write(prompt, {
                tone: options.tone || 'neutral', // 'formal', 'casual', 'creative', 'professional'
                format: options.format || 'plain-text', // 'plain-text', 'markdown'
                length: options.length || 'medium' // 'short', 'medium', 'long'
            });

            return {
                success: true,
                content: content,
                prompt: prompt,
                options: options,
                wordCount: content.split(' ').length
            };
        } catch (error) {
            console.error('Writer error:', error);
            return {
                success: false,
                error: error.message,
                fallback: await this.fallbackWrite(prompt)
            };
        }
    }

    // 🖊️ REWRITER API - Mejorar y reescribir contenido
    async rewriteContent(text, options = {}) {
        try {
            if (!this.rewriter) {
                throw new Error('Rewriter API not available');
            }

            const rewritten = await this.rewriter.rewrite(text, {
                tone: options.tone || 'neutral', // 'formal', 'casual', 'creative', 'professional'
                format: options.format || 'plain-text',
                length: options.length || 'as-is' // 'shorter', 'longer', 'as-is'
            });

            return {
                success: true,
                original: text,
                rewritten: rewritten,
                options: options,
                improvement: this.calculateImprovement(text, rewritten)
            };
        } catch (error) {
            console.error('Rewriter error:', error);
            return {
                success: false,
                error: error.message,
                fallback: await this.fallbackRewrite(text)
            };
        }
    }

    // 🌐 TRANSLATOR API - Traducir texto
    async translateText(text, targetLanguage, sourceLanguage = 'auto') {
        try {
            // Detectar idioma si es 'auto'
            if (sourceLanguage === 'auto' && this.languageDetector) {
                const detection = await this.languageDetector.detect(text);
                sourceLanguage = detection[0].detectedLanguage;
            }

            // Crear traductor específico
            const translator = await window.translation.createTranslator({
                sourceLanguage: sourceLanguage,
                targetLanguage: targetLanguage
            });

            const translated = await translator.translate(text);

            return {
                success: true,
                original: text,
                translated: translated,
                sourceLanguage: sourceLanguage,
                targetLanguage: targetLanguage,
                confidence: detection ? detection[0].confidence : null
            };
        } catch (error) {
            console.error('Translator error:', error);
            return {
                success: false,
                error: error.message,
                fallback: await this.fallbackTranslate(text, targetLanguage)
            };
        }
    }

    // 🔤 PROOFREADER/CORRECTOR - Corregir gramática
    async proofreadText(text) {
        try {
            // La API de Proofreader puede estar incluida en Rewriter
            if (this.rewriter) {
                const corrected = await this.rewriter.rewrite(text, {
                    tone: 'as-is',
                    format: 'plain-text',
                    length: 'as-is',
                    focus: 'grammar' // Parámetro específico para corrección
                });

                return {
                    success: true,
                    original: text,
                    corrected: corrected,
                    corrections: this.findCorrections(text, corrected)
                };
            } else {
                throw new Error('Proofreader API not available');
            }
        } catch (error) {
            console.error('Proofreader error:', error);
            return {
                success: false,
                error: error.message,
                fallback: await this.fallbackProofread(text)
            };
        }
    }

    // 🔄 FALLBACK a Gemini API cuando Chrome AI no está disponible
    async fallbackSummarize(text) {
        const prompt = `Please summarize the following text in a concise way:\n\n${text}`;
        return await this.callGeminiAPI(prompt);
    }

    async fallbackWrite(prompt) {
        const enhancedPrompt = `As a creative writer, please generate content based on this prompt: ${prompt}`;
        return await this.callGeminiAPI(enhancedPrompt);
    }

    async fallbackRewrite(text) {
        const prompt = `Please improve and rewrite the following text while maintaining its meaning:\n\n${text}`;
        return await this.callGeminiAPI(prompt);
    }

    async fallbackTranslate(text, targetLanguage) {
        const prompt = `Please translate the following text to ${targetLanguage}:\n\n${text}`;
        return await this.callGeminiAPI(prompt);
    }

    async fallbackProofread(text) {
        const prompt = `Please proofread and correct any grammar, spelling, or style errors in the following text:\n\n${text}`;
        return await this.callGeminiAPI(prompt);
    }

    // 🔗 Llamada a Gemini API como fallback
    async callGeminiAPI(prompt) {
        try {
            // Aquí usas tu implementación existente de Gemini API
            const response = await fetch('/api/chat/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: prompt,
                    useGeminiAPI: true
                })
            });
            
            const data = await response.json();
            return data.response || 'No response from Gemini API';
        } catch (error) {
            console.error('Gemini API fallback error:', error);
            return 'Sorry, AI services are temporarily unavailable.';
        }
    }

    // 🧮 Métodos auxiliares
    calculateImprovement(original, rewritten) {
        return {
            lengthChange: rewritten.length - original.length,
            wordChange: rewritten.split(' ').length - original.split(' ').length,
            readabilityImproved: rewritten.length < original.length && rewritten.split(' ').length <= original.split(' ').length
        };
    }

    findCorrections(original, corrected) {
        // Algoritmo simple para encontrar diferencias
        const originalWords = original.split(' ');
        const correctedWords = corrected.split(' ');
        const corrections = [];
        
        // Implementación básica - podrías usar una librería de diff más sofisticada
        for (let i = 0; i < Math.min(originalWords.length, correctedWords.length); i++) {
            if (originalWords[i] !== correctedWords[i]) {
                corrections.push({
                    position: i,
                    original: originalWords[i],
                    corrected: correctedWords[i]
                });
            }
        }
        
        return corrections;
    }
}

// 🚀 Inicializar Chrome AI Manager globalmente
window.chromeAIManager = new ChromeAIManager();

// 🎯 Funciones de utilidad para integrar en tu UI
async function initializeChromeAI() {
    console.log('🧠 Initializing Chrome Built-in AI APIs...');
    const availability = await window.chromeAIManager.initialize();
    
    // Mostrar APIs disponibles en la UI
    updateUIWithAvailableAPIs(availability);
    
    return availability;
}

function updateUIWithAvailableAPIs(availability) {
    // Actualizar la UI para mostrar qué APIs están disponibles
    const apiStatus = {
        'Escritor AI': availability?.writerAPI || false,
        'Corrector': availability?.rewriterAPI || false,
        'Traductor': availability?.translatorAPI || false
    };
    
    console.log('API Status for UI:', apiStatus);
    
    // Aquí actualizarías tu interfaz para habilitar/deshabilitar botones
    // basado en qué APIs están disponibles
}

// 🔄 Auto-inicializar cuando se carga la página
document.addEventListener('DOMContentLoaded', async () => {
    await initializeChromeAI();
});

export { ChromeAIManager, initializeChromeAI };