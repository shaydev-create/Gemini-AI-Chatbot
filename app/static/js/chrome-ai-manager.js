/**
 * Chrome Built-in AI Integration
 * Provides access to Chrome's built-in AI APIs for enhanced user experience
 */

class ChromeAIManager {
    constructor() {
        this.promptSession = null;
        this.isAvailable = false;
        this.isInitialized = false;
        this.responseCache = new Map(); // Cache simple para respuestas
        this.capabilities = {
            prompt: false,
            summarizer: false,
            writer: false,
            rewriter: false,
            translator: false,
            proofreader: false
        };
    }

    /**
     * Initialize Chrome AI APIs - Modo Local Simple
     */
    async initialize() {
        try {
            // Verificar si Chrome Built-in AI está disponible
            if (!this.isChromeBrowserCompatible()) {
                console.log('Chrome Built-in AI: No disponible en este entorno');
                return false;
            }

            // Verificar disponibilidad de APIs
            await this.checkAPIAvailability();
            
            // NO inicializar aquí - esperar gesto del usuario
            // if (this.capabilities.prompt) {
            //     await this.initializePromptAPI();
            // }

            this.isInitialized = true;
            console.log('Chrome Built-in AI inicializado correctamente', this.capabilities);
            return this.capabilities.prompt; // Retorna true si prompt API está disponible

        } catch (error) {
            console.error('Error al inicializar Chrome Built-in AI:', error);
            return false;
        }
    }

    /**
     * Pre-initialize sessions for instant response
     */
    async preInitializeSessions() {
        try {
            // Only initialize prompt session (most commonly used)
            if (this.capabilities.prompt && !this.sessions.prompt) {
                this.sessions.prompt = await window.ai.languageModel.create({
                    systemPrompt: "You are a helpful AI assistant. Respond quickly and concisely."
                });
                console.log('⚡ Prompt session pre-initialized for instant responses');
            }
        } catch (error) {
            console.warn('Session pre-initialization failed:', error);
        }
    }

    /**
     * Check if browser supports Chrome Built-in AI
     */
    isChromeBrowserCompatible() {
        return typeof window !== 'undefined' && 
               'LanguageModel' in window;
    }

    /**
     * Check availability of all Chrome AI APIs
     */
    async checkAPIAvailability() {
        console.log('🔍 Checking Chrome Built-in AI API availability...');
        
        // Check Prompt API (LanguageModel)
        if ('LanguageModel' in window) {
            try {
                const availability = await LanguageModel.availability();
                this.capabilities.prompt = availability !== 'unavailable';
                console.log('✅ Prompt API (LanguageModel) availability:', availability);
            } catch (error) {
                console.log('❌ Prompt API not available:', error.message);
            }
        } else {
            console.log('❌ LanguageModel not found in window');
        }

        // Check Summarizer API
        if ('ai' in window && 'summarizer' in window.ai) {
            try {
                const availability = await window.ai.summarizer.availability();
                this.capabilities.summarizer = availability !== 'unavailable';
                console.log('✅ Summarizer API availability:', availability);
            } catch (error) {
                console.log('❌ Summarizer API not available:', error.message);
            }
        } else {
            console.log('❌ window.ai.summarizer not found');
        }

        // Check Writer API
        if ('ai' in window && 'writer' in window.ai) {
            try {
                const availability = await window.ai.writer.availability();
                this.capabilities.writer = availability !== 'unavailable';
                console.log('✅ Writer API availability:', availability);
            } catch (error) {
                console.log('❌ Writer API not available:', error.message);
            }
        } else {
            console.log('❌ window.ai.writer not found');
        }

        // Check Rewriter API
        if ('ai' in window && 'rewriter' in window.ai) {
            try {
                const availability = await window.ai.rewriter.availability();
                this.capabilities.rewriter = availability !== 'unavailable';
                console.log('✅ Rewriter API availability:', availability);
            } catch (error) {
                console.log('❌ Rewriter API not available:', error.message);
            }
        } else {
            console.log('❌ window.ai.rewriter not found');
        }

        // Check Translator API
        if ('ai' in window && 'translator' in window.ai) {
            try {
                const availability = await window.ai.translator.availability();
                this.capabilities.translator = availability !== 'unavailable';
                console.log('✅ Translator API availability:', availability);
            } catch (error) {
                console.log('❌ Translator API not available:', error.message);
            }
        } else {
            console.log('❌ window.ai.translator not found');
        }

        // Check Language Detector API (for proofreading)
        if ('ai' in window && 'languageDetector' in window.ai) {
            try {
                const availability = await window.ai.languageDetector.availability();
                this.capabilities.proofreader = availability !== 'unavailable';
                console.log('✅ Language Detector API availability:', availability);
            } catch (error) {
                console.log('❌ Language Detector API not available:', error.message);
            }
        } else {
            console.log('❌ window.ai.languageDetector not found');
        }

        // Log overall capabilities
        console.log('🧠 Chrome AI Capabilities:', this.capabilities);
        console.log('🌐 Available window.ai:', window.ai || 'Not available');
    }

    /**
     * Initialize Prompt API - MODO LOCAL ORIGINAL (Funciona Sin Internet)
     */
    async initializePromptAPI() {
        try {
            // Check if LanguageModel is available
            if (typeof LanguageModel === 'undefined') {
                console.error('LanguageModel not available');
                return false;
            }

            // Get model parameters
            const params = await LanguageModel.params();
            console.log('LanguageModel params:', params);

            // Create session - NO especificar temperature ni topK para usar defaults
            this.promptSession = await LanguageModel.create({
                systemPrompt: 'Eres un asistente AI útil. Responde en español de manera clara y concisa.',
                monitor(m) {
                    m.addEventListener('downloadprogress', (e) => {
                        console.log(`📥 Descargando modelo: ${Math.round(e.loaded * 100)}%`);
                        document.dispatchEvent(new CustomEvent('chrome-ai-download-progress', {
                            detail: { progress: e.loaded * 100 }
                        }));
                    });
                }
            });

            console.log('✅ Chrome AI Prompt API inicializada correctamente (MODO LOCAL)');
            return true;

        } catch (error) {
            console.error('❌ Error al inicializar Chrome AI:', error);
            return false;
        }
    }

    /**
     * Send prompt to Chrome Built-in AI LOCAL (Sin Internet) - SOLO CHROME AI
     */
    async prompt(message, options = {}) {
        if (!this.capabilities.prompt) {
            throw new Error('Prompt API not available');
        }

        // Initialize prompt session on first use (user gesture required)
        if (!this.promptSession) {
            console.log('🚀 Initializing Chrome AI on first use...');
            const success = await this.initializePromptAPI();
            if (!success) {
                throw new Error('Failed to initialize Chrome AI session');
            }
        }

        try {
            const { streaming = false, signal = null } = options;
            
            // Opciones mínimas para Chrome AI
            const promptOptions = {};
            if (signal && signal instanceof AbortSignal) {
                promptOptions.signal = signal;
            }

            let result;
            if (streaming) {
                result = await this.promptSession.promptStreaming(message, promptOptions);
            } else {
                result = await this.promptSession.prompt(message, promptOptions);
            }
            
            console.log('✅ Chrome AI Local response received');
            return result;

        } catch (error) {
            console.error('❌ Chrome AI Local error:', error);
            throw error;
        }
    }

    /**
     * Summarize text using Chrome Built-in AI
     */
    async summarize(text, options = {}) {
        if (!this.capabilities.summarizer) {
            throw new Error('Summarizer API not available');
        }

        try {
            console.log('🔄 Creating summarizer session...');
            const summarizer = await window.ai.summarizer.create({
                type: options.type || 'tl;dr',
                format: options.format || 'markdown',
                length: options.length || 'medium'
            });
            
            console.log('📄 Summarizing text...');
            const summary = await summarizer.summarize(text);
            summarizer.destroy();
            
            console.log('✅ Summary completed');
            return summary;

        } catch (error) {
            console.error('Chrome AI summarize error:', error);
            throw error;
        }
    }

    /**
     * Write content using Chrome Built-in AI
     */
    async write(prompt, options = {}) {
        if (!this.capabilities.writer) {
            throw new Error('Writer API not available');
        }

        try {
            console.log('🔄 Creating writer session...');
            const writer = await window.ai.writer.create({
                tone: options.tone || 'neutral',
                format: options.format || 'plain-text',
                length: options.length || 'medium'
            });
            
            console.log('✍️ Writing content...');
            const content = await writer.write(prompt);
            writer.destroy();
            
            console.log('✅ Writing completed');
            return content;

        } catch (error) {
            console.error('Chrome AI write error:', error);
            throw error;
        }
    }

    /**
     * Rewrite text using Chrome Built-in AI
     */
    async rewrite(text, options = {}) {
        if (!this.capabilities.rewriter) {
            throw new Error('Rewriter API not available');
        }

        try {
            console.log('🔄 Creating rewriter session...');
            const rewriter = await window.ai.rewriter.create({
                tone: options.tone || 'as-is',
                format: options.format || 'as-is',
                length: options.length || 'as-is'
            });
            
            console.log('🖊️ Rewriting text...');
            const rewritten = await rewriter.rewrite(text);
            rewriter.destroy();
            
            console.log('✅ Rewriting completed');
            return rewritten;

        } catch (error) {
            console.error('Chrome AI rewrite error:', error);
            throw error;
        }
    }

    /**
     * Translate text using Chrome Built-in AI
     */
    async translate(text, sourceLanguage, targetLanguage, options = {}) {
        if (!this.capabilities.translator) {
            throw new Error('Translator API not available');
        }

        try {
            console.log('🔄 Creating translator session...');
            const translator = await window.ai.translator.create({
                sourceLanguage,
                targetLanguage
            });
            
            console.log('🌐 Translating text...');
            const translated = await translator.translate(text);
            translator.destroy();
            
            console.log('✅ Translation completed');
            return translated;

        } catch (error) {
            console.error('Chrome AI translate error:', error);
            throw error;
        }
    }

    /**
     * Proofread text using Chrome Built-in AI (using language detection + rewriter)
     */
    async proofread(text, options = {}) {
        // Use rewriter API for proofreading since there's no dedicated proofreader API
        if (!this.capabilities.rewriter) {
            throw new Error('Rewriter API (for proofreading) not available');
        }

        try {
            console.log('🔄 Creating proofreader session (using rewriter)...');
            const rewriter = await window.ai.rewriter.create({
                tone: 'more-formal',
                format: 'as-is',
                length: 'as-is'
            });
            
            console.log('📖 Proofreading text...');
            const corrected = await rewriter.rewrite(text);
            rewriter.destroy();
            
            console.log('✅ Proofreading completed');
            return corrected;

        } catch (error) {
            console.error('Chrome AI proofread error:', error);
            throw error;
        }
    }

    /**
     * Get session usage information
     */
    getUsageInfo() {
        if (!this.promptSession) {
            return null;
        }

        return {
            inputUsage: this.promptSession.inputUsage,
            inputQuota: this.promptSession.inputQuota,
            usagePercentage: Math.round((this.promptSession.inputUsage / this.promptSession.inputQuota) * 100)
        };
    }

    /**
     * Clone current session for parallel processing
     */
    async cloneSession(signal = null) {
        if (!this.promptSession) {
            throw new Error('No active session to clone');
        }

        try {
            return await this.promptSession.clone({ signal });
        } catch (error) {
            console.error('Failed to clone session:', error);
            throw error;
        }
    }

    /**
     * Destroy current session
     */
    async destroy() {
        if (this.promptSession) {
            try {
                this.promptSession.destroy();
                this.promptSession = null;
                console.log('Chrome AI session destroyed');
            } catch (error) {
                console.error('Error destroying session:', error);
            }
        }
    }

    /**
     * Check if any Chrome AI capability is available
     */
    hasAnyCapability() {
        return Object.values(this.capabilities).some(cap => cap);
    }

    /**
     * Get available capabilities
     */
    getCapabilities() {
        return { ...this.capabilities };
    }

    /**
     * Ultra-fast hybrid function with caching and optimization
     */
    async processWithHybridAI(text, operation, options = {}) {
        const startTime = performance.now();
        
        // Generate cache key for response caching
        const cacheKey = `${operation}:${text.substring(0, 100)}:${JSON.stringify(options)}`;
        
        // Check cache first for instant responses
        if (this.responseCache.has(cacheKey)) {
            const cachedResponse = this.responseCache.get(cacheKey);
            console.log(`⚡ Cache hit for ${operation} - instant response`);
            return cachedResponse;
        }

        let result;
        let usedAPI = 'unknown';

        try {
            // Fast path: Use Chrome AI if available
            if (this.capabilities.prompt) {
                console.log(`🚀 Fast Chrome AI processing: ${operation}`);
                usedAPI = 'chrome-ai';
                
                if (this.capabilities[operation]) {
                    // Use specific API
                    result = await this.executeSpecificAPI(operation, text, options);
                } else {
                    // Use Prompt API for all tasks (fastest)
                    result = await this.usePromptAPIForTask(text, operation, options);
                }
            } else {
                // Direct Gemini fallback (no Chrome AI available)
                console.log(`🌐 Direct Gemini processing: ${operation}`);
                usedAPI = 'gemini';
                result = await this.fallbackToGemini(text, operation, options);
            }

            // Cache successful results for future instant responses
            this.cacheResponse(cacheKey, result);

            // Track performance
            const duration = performance.now() - startTime;
            this.updatePerformanceMetrics(usedAPI, duration);
            console.log(`✅ ${operation} completed in ${duration.toFixed(2)}ms using ${usedAPI}`);

            return result;

        } catch (error) {
            console.warn(`❌ ${operation} failed, trying Gemini fallback:`, error);
            
            // Emergency fallback to Gemini
            try {
                usedAPI = 'gemini-fallback';
                result = await this.fallbackToGemini(text, operation, options);
                this.cacheResponse(cacheKey, result);
                return result;
            } catch (fallbackError) {
                console.error(`💥 All methods failed for ${operation}:`, fallbackError);
                throw new Error(`Failed to process ${operation}: ${fallbackError.message}`);
            }
        }
    }

    /**
     * Execute specific Chrome AI API with session reuse
     */
    async executeSpecificAPI(operation, text, options) {
        switch (operation) {
            case 'summarize':
                return await this.summarize(text, options);
            case 'writer':
                return await this.write(text, options);
            case 'rewriter':
                return await this.rewrite(text, options);
            case 'translator':
                return await this.translate(text, options.sourceLanguage || 'auto', options.targetLanguage || 'es', options);
            case 'proofreader':
                return await this.proofread(text, options);
            case 'prompt':
                return await this.prompt(text, options);
            default:
                throw new Error(`Unknown operation: ${operation}`);
        }
    }

    /**
     * Ultra-fast Prompt API task execution with optimized prompts
     */
    async usePromptAPIForTask(text, operation, options = {}) {
        // Use pre-initialized session for instant response
        if (!this.sessions.prompt) {
            await this.preInitializeSessions();
        }

        // Optimized prompts for speed (shorter = faster)
        let prompt = '';
        
        switch (operation) {
            case 'summarize':
                prompt = `Summarize: ${text}`;
                break;
            case 'writer':
                const tone = options.tone || 'neutral';
                prompt = `Write ${tone}: ${text}`;
                break;
            case 'rewriter':
                prompt = `Rewrite: ${text}`;
                break;
            case 'translator':
                const targetLang = options.targetLanguage || 'Spanish';
                prompt = `Translate to ${targetLang}: ${text}`;
                break;
            case 'proofreader':
                prompt = `Fix grammar: ${text}`;
                break;
            default:
                prompt = text;
        }

        return await this.prompt(prompt, { ...options, fast: true });
    }

    /**
     * Cache management for ultra-fast responses
     */
    cacheResponse(key, response) {
        // Limit cache size to prevent memory issues
        if (this.responseCache.size >= this.maxCacheSize) {
            const firstKey = this.responseCache.keys().next().value;
            this.responseCache.delete(firstKey);
        }
        
        this.responseCache.set(key, response);
    }

    /**
     * Performance metrics tracking
     */
    updatePerformanceMetrics(api, duration) {
        if (this.performanceMetrics[api]) {
            this.performanceMetrics[api].total += duration;
            this.performanceMetrics[api].count += 1;
        }
    }

    /**
     * Get performance statistics
     */
    getPerformanceStats() {
        const stats = {};
        for (const [api, metrics] of Object.entries(this.performanceMetrics)) {
            if (metrics.count > 0) {
                stats[api] = {
                    averageMs: (metrics.total / metrics.count).toFixed(2),
                    totalCalls: metrics.count
                };
            }
        }
        return stats;
    }

    /**
     * Clear cache for fresh responses
     */
    clearCache() {
        this.responseCache.clear();
        console.log('🗑️ Response cache cleared');
    }

    /**
     * Ultra-fast Gemini API fallback with optimized requests
     */
    async fallbackToGemini(text, operation, options = {}) {
        const startTime = performance.now();
        
        // Fast cache check for Gemini responses too
        const cacheKey = `gemini:${operation}:${text.substring(0, 50)}`;
        if (this.responseCache.has(cacheKey)) {
            console.log('⚡ Gemini cache hit');
            return this.responseCache.get(cacheKey);
        }

        // Ultra-short prompts for faster processing
        let prompt = '';
        switch (operation) {
            case 'summarize':
                prompt = `Resumen: ${text}`;
                break;
            case 'writer':
                prompt = `Escribe sobre: ${text}`;
                break;
            case 'rewriter':
                prompt = `Mejora: ${text}`;
                break;
            case 'translator':
                const targetLang = options.targetLanguage || 'español';
                prompt = `A ${targetLang}: ${text}`;
                break;
            case 'proofreader':
                prompt = `Corrige: ${text}`;
                break;
            default:
                prompt = text;
        }

        try {
            // Ultra-fast fetch with timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s timeout
            
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    message: prompt,
                    fast_mode: true // Signal to backend for faster processing
                }),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            const result = data.response || data.message || 'Sin respuesta';
            
            // Cache successful Gemini responses
            this.cacheResponse(cacheKey, result);
            
            const duration = performance.now() - startTime;
            console.log(`🌐 Gemini response in ${duration.toFixed(2)}ms`);
            
            return result;

        } catch (error) {
            if (error.name === 'AbortError') {
                throw new Error('Gemini API timeout - response took too long');
            }
            console.error('Gemini fallback error:', error);
            throw new Error(`Gemini fallback failed for ${operation}: ${error.message}`);
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChromeAIManager;
} else {
    window.ChromeAIManager = ChromeAIManager;
}