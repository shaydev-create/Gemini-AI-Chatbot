/**
 * Chrome Built-in AI Integration
 * Provides access to Chrome's built-in AI APIs for enhanced user experience
 */

class ChromeAIManager {
    constructor() {
        this.promptSession = null;
        this.isAvailable = false;
        this.isInitialized = false;
        this.responseCache = new Map(); // Cache for faster responses
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
     * Initialize Chrome AI APIs
     */
    async initialize() {
        try {
            // Check if running in supported environment
            if (!this.isChromeBrowserCompatible()) {
                console.log('Chrome Built-in AI: Not available in this environment');
                return false;
            }

            // Check API availability
            await this.checkAPIAvailability();
            
            // DON'T initialize Prompt API here - wait for user gesture
            // if (this.capabilities.prompt) {
            //     await this.initializePromptAPI();
            // }

            this.isInitialized = true;
            console.log('Chrome Built-in AI initialized successfully', this.capabilities);
            return this.capabilities.prompt; // Return true if prompt API is available

        } catch (error) {
            console.error('Chrome Built-in AI initialization failed:', error);
            return false;
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
        // Check Prompt API
        if ('LanguageModel' in window) {
            try {
                const availability = await LanguageModel.availability();
                this.capabilities.prompt = availability !== 'unavailable';
                console.log('Prompt API availability:', availability);
            } catch (error) {
                console.log('Prompt API not available:', error.message);
            }
        }

        // Check Summarizer API
        if ('SummarizerAPI' in window) {
            try {
                const availability = await SummarizerAPI.availability();
                this.capabilities.summarizer = availability !== 'unavailable';
                console.log('Summarizer API availability:', availability);
            } catch (error) {
                console.log('Summarizer API not available:', error.message);
            }
        }

        // Check Writer API
        if ('WriterAPI' in window) {
            try {
                const availability = await WriterAPI.availability();
                this.capabilities.writer = availability !== 'unavailable';
                console.log('Writer API availability:', availability);
            } catch (error) {
                console.log('Writer API not available:', error.message);
            }
        }

        // Check Rewriter API
        if ('RewriterAPI' in window) {
            try {
                const availability = await RewriterAPI.availability();
                this.capabilities.rewriter = availability !== 'unavailable';
                console.log('Rewriter API availability:', availability);
            } catch (error) {
                console.log('Rewriter API not available:', error.message);
            }
        }

        // Check Translator API
        if ('TranslatorAPI' in window) {
            try {
                const availability = await TranslatorAPI.availability();
                this.capabilities.translator = availability !== 'unavailable';
                console.log('Translator API availability:', availability);
            } catch (error) {
                console.log('Translator API not available:', error.message);
            }
        }

        // Check Proofreader API
        if ('ProofreaderAPI' in window) {
            try {
                const availability = await ProofreaderAPI.availability();
                this.capabilities.proofreader = availability !== 'unavailable';
                console.log('Proofreader API availability:', availability);
            } catch (error) {
                console.log('Proofreader API not available:', error.message);
            }
        }
    }

    /**
     * Initialize Prompt API session
     */
    async initializePromptAPI() {
        try {
            const params = await LanguageModel.params();
            console.log('LanguageModel params:', params);

            // Ensure valid topK value (optimized for max speed)
            const validTopK = 1; // Minimum for maximum speed
            
            this.promptSession = await LanguageModel.create({
                temperature: 0.1, // Minimum for consistency and speed
                topK: validTopK,
                systemPrompt: 'Responde de forma concisa.',
                monitor(m) {
                    m.addEventListener('downloadprogress', (e) => {
                        console.log(`Model download progress: ${Math.round(e.loaded * 100)}%`);
                        document.dispatchEvent(new CustomEvent('chrome-ai-download-progress', {
                            detail: { progress: e.loaded * 100 }
                        }));
                    });
                }
            });

            console.log('Prompt API session created successfully');
            return true;

        } catch (error) {
            console.error('Failed to initialize Prompt API:', error);
            return false;
        }
    }

    /**
     * Send prompt to Chrome Built-in AI
     */
    async prompt(message, options = {}) {
        if (!this.capabilities.prompt) {
            throw new Error('Prompt API not available');
        }

        // Check cache first for identical messages
        const cacheKey = message + (options.language || 'es');
        if (this.responseCache.has(cacheKey) && !options.streaming) {
            console.log('🚀 Cache hit - returning cached response');
            return this.responseCache.get(cacheKey);
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
            const { streaming = false, signal = null, language = 'es' } = options;
            
            // Simple and fast language instruction 
            const fullMessage = language === 'es' ? message : message;

            // Build options object only with valid properties
            const promptOptions = {};
            if (signal && signal instanceof AbortSignal) {
                promptOptions.signal = signal;
            }
            
            // Add explicit language specification
            if (language === 'es') {
                promptOptions.outputLanguage = 'es';
            } else {
                promptOptions.outputLanguage = 'en';
            }

            let result;
            if (streaming) {
                result = await this.promptSession.promptStreaming(fullMessage, promptOptions);
            } else {
                result = await this.promptSession.prompt(fullMessage, promptOptions);
                
                // Cache non-streaming responses
                if (result && this.responseCache.size < 50) {
                    this.responseCache.set(cacheKey, result);
                }
            }
            
            return result;

        } catch (error) {
            console.error('Chrome AI prompt error:', error);
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
            const summarizer = await SummarizerAPI.create(options);
            const summary = await summarizer.summarize(text);
            summarizer.destroy();
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
            const writer = await WriterAPI.create(options);
            const content = await writer.write(prompt);
            writer.destroy();
            return content;

        } catch (error) {
            console.error('Chrome AI write error:', error);
            throw error;
        }
    }

    /**
     * Rewrite content using Chrome Built-in AI
     */
    async rewrite(text, options = {}) {
        if (!this.capabilities.rewriter) {
            throw new Error('Rewriter API not available');
        }

        try {
            const rewriter = await RewriterAPI.create(options);
            const rewritten = await rewriter.rewrite(text);
            rewriter.destroy();
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
            const translator = await TranslatorAPI.create({
                sourceLanguage,
                targetLanguage,
                ...options
            });
            const translated = await translator.translate(text);
            translator.destroy();
            return translated;

        } catch (error) {
            console.error('Chrome AI translate error:', error);
            throw error;
        }
    }

    /**
     * Proofread text using Chrome Built-in AI
     */
    async proofread(text, options = {}) {
        if (!this.capabilities.proofreader) {
            throw new Error('Proofreader API not available');
        }

        try {
            const proofreader = await ProofreaderAPI.create(options);
            const corrected = await proofreader.proofread(text);
            proofreader.destroy();
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
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChromeAIManager;
} else {
    window.ChromeAIManager = ChromeAIManager;
}