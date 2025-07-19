// Content script para Gemini AI Chatbot Chrome Extension

// Detectar si estamos en la página de la aplicación
if (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost') {
    console.log('Gemini AI Chatbot detectado');
    
    // Mejorar la experiencia en la aplicación
    document.addEventListener('DOMContentLoaded', () => {
        // Agregar clase para identificar que se ejecuta como extensión
        document.body.classList.add('chrome-extension-mode');
        
        // Agregar funcionalidades específicas de la extensión
        addExtensionFeatures();
        
        // Mejorar la interfaz para la extensión
        enhanceUIForExtension();
        
        // Configurar comunicación con background script
        setupExtensionCommunication();
    });
}

function addExtensionFeatures() {
    // Agregar botón de "Abrir en nueva ventana" si es necesario
    const header = document.querySelector('header, .header, nav');
    if (header) {
        const extensionButton = document.createElement('button');
        extensionButton.innerHTML = '🔗 Extensión';
        extensionButton.className = 'extension-indicator';
        extensionButton.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            z-index: 10000;
            background: rgba(102, 126, 234, 0.9);
            color: white;
            border: none;
            border-radius: 5px;
            padding: 5px 10px;
            font-size: 12px;
            cursor: pointer;
            backdrop-filter: blur(10px);
        `;
        
        extensionButton.addEventListener('click', () => {
            showExtensionInfo();
        });
        
        document.body.appendChild(extensionButton);
    }
    
    // Agregar atajos de teclado específicos para la extensión
    document.addEventListener('keydown', (e) => {
        // Ctrl+Shift+E para abrir en nueva pestaña
        if (e.ctrlKey && e.shiftKey && e.key === 'E') {
            e.preventDefault();
            chrome.runtime.sendMessage({
                action: 'openChat'
            });
        }
        
        // Ctrl+Shift+H para mostrar ayuda de la extensión
        if (e.ctrlKey && e.shiftKey && e.key === 'H') {
            e.preventDefault();
            showExtensionHelp();
        }
    });
}

function enhanceUIForExtension() {
    // Agregar estilos específicos para la extensión
    const extensionStyles = document.createElement('style');
    extensionStyles.textContent = `
        .chrome-extension-mode {
            --extension-accent: #667eea;
        }
        
        .chrome-extension-mode .extension-indicator {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 0.7; }
            50% { opacity: 1; }
            100% { opacity: 0.7; }
        }
        
        .extension-notification {
            position: fixed;
            top: 50px;
            right: 10px;
            background: rgba(102, 126, 234, 0.95);
            color: white;
            padding: 10px 15px;
            border-radius: 8px;
            z-index: 10001;
            font-size: 14px;
            max-width: 300px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transform: translateX(100%);
            transition: transform 0.3s ease;
        }
        
        .extension-notification.show {
            transform: translateX(0);
        }
        
        .extension-help-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            z-index: 10002;
            display: flex;
            align-items: center;
            justify-content: center;
            backdrop-filter: blur(5px);
        }
        
        .extension-help-content {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 30px;
            border-radius: 15px;
            max-width: 500px;
            max-height: 80vh;
            overflow-y: auto;
            position: relative;
        }
        
        .extension-help-close {
            position: absolute;
            top: 10px;
            right: 15px;
            background: none;
            border: none;
            color: white;
            font-size: 24px;
            cursor: pointer;
            opacity: 0.7;
        }
        
        .extension-help-close:hover {
            opacity: 1;
        }
    `;
    
    document.head.appendChild(extensionStyles);
}

function setupExtensionCommunication() {
    // Escuchar mensajes desde el background script
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
        console.log('Mensaje recibido en content script:', request);
        
        switch (request.action) {
            case 'showNotification':
                showExtensionNotification(request.message);
                sendResponse({ success: true });
                break;
                
            case 'highlightElement':
                if (request.selector) {
                    const element = document.querySelector(request.selector);
                    if (element) {
                        highlightElement(element);
                        sendResponse({ success: true });
                    } else {
                        sendResponse({ success: false, error: 'Elemento no encontrado' });
                    }
                }
                break;
                
            case 'getPageInfo':
                sendResponse({
                    title: document.title,
                    url: window.location.href,
                    hasChat: !!document.querySelector('#messages, .messages'),
                    isGeminiApp: true
                });
                break;
                
            default:
                sendResponse({ error: 'Acción no reconocida' });
        }
    });
    
    // Notificar al background script que el content script está listo
    chrome.runtime.sendMessage({
        action: 'contentScriptReady',
        url: window.location.href
    });
}

function showExtensionInfo() {
    showExtensionNotification('🤖 Ejecutándose como extensión de Chrome. Usa Ctrl+Shift+H para ver ayuda.');
}

function showExtensionHelp() {
    const helpModal = document.createElement('div');
    helpModal.className = 'extension-help-modal';
    helpModal.innerHTML = `
        <div class="extension-help-content">
            <button class="extension-help-close">&times;</button>
            <h2>🤖 Gemini AI Chatbot - Ayuda de Extensión</h2>
            <br>
            <h3>Atajos de Teclado:</h3>
            <ul>
                <li><strong>Ctrl+Shift+E:</strong> Abrir en nueva pestaña</li>
                <li><strong>Ctrl+Shift+H:</strong> Mostrar esta ayuda</li>
                <li><strong>Ctrl+K:</strong> Enfocar entrada de chat</li>
                <li><strong>Ctrl+L:</strong> Limpiar chat</li>
            </ul>
            <br>
            <h3>Funciones de la Extensión:</h3>
            <ul>
                <li>🔗 Acceso rápido desde la barra de herramientas</li>
                <li>💬 Popup para mensajes rápidos</li>
                <li>🌐 Integración con el navegador</li>
                <li>📋 Menú contextual para texto seleccionado</li>
            </ul>
            <br>
            <h3>Estado de Conexión:</h3>
            <p>La extensión verifica automáticamente la conexión con el servidor cada minuto.</p>
            <br>
            <p><em>Presiona Escape o haz clic fuera para cerrar</em></p>
        </div>
    `;
    
    // Cerrar modal
    const closeModal = () => {
        helpModal.remove();
    };
    
    helpModal.addEventListener('click', (e) => {
        if (e.target === helpModal) closeModal();
    });
    
    helpModal.querySelector('.extension-help-close').addEventListener('click', closeModal);
    
    document.addEventListener('keydown', function escapeHandler(e) {
        if (e.key === 'Escape') {
            closeModal();
            document.removeEventListener('keydown', escapeHandler);
        }
    });
    
    document.body.appendChild(helpModal);
}

function showExtensionNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'extension-notification';
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Mostrar notificación
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    // Ocultar después de 3 segundos
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

function highlightElement(element) {
    const originalStyle = element.style.cssText;
    
    element.style.cssText += `
        outline: 3px solid #667eea !important;
        outline-offset: 2px !important;
        background: rgba(102, 126, 234, 0.1) !important;
        transition: all 0.3s ease !important;
    `;
    
    // Restaurar estilo original después de 2 segundos
    setTimeout(() => {
        element.style.cssText = originalStyle;
    }, 2000);
}

// Detectar cambios en la página para mantener funcionalidades
const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        if (mutation.type === 'childList') {
            // Verificar si se agregaron nuevos elementos que necesiten funcionalidades de extensión
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType === Node.ELEMENT_NODE) {
                    // Agregar funcionalidades específicas a nuevos elementos si es necesario
                    if (node.matches && node.matches('.message, .chat-input')) {
                        // Mejorar nuevos elementos de chat
                        enhanceNewChatElements(node);
                    }
                }
            });
        }
    });
});

function enhanceNewChatElements(element) {
    // Agregar funcionalidades específicas de extensión a nuevos elementos
    if (element.classList.contains('message')) {
        // Agregar botón de copia rápida a mensajes
        const copyButton = document.createElement('button');
        copyButton.innerHTML = '📋';
        copyButton.style.cssText = `
            position: absolute;
            top: 5px;
            right: 5px;
            background: rgba(255, 255, 255, 0.2);
            border: none;
            border-radius: 3px;
            color: white;
            cursor: pointer;
            font-size: 12px;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        
        element.style.position = 'relative';
        element.appendChild(copyButton);
        
        element.addEventListener('mouseenter', () => {
            copyButton.style.opacity = '1';
        });
        
        element.addEventListener('mouseleave', () => {
            copyButton.style.opacity = '0';
        });
        
        copyButton.addEventListener('click', () => {
            navigator.clipboard.writeText(element.textContent);
            showExtensionNotification('Mensaje copiado al portapapeles');
        });
    }
}

// Iniciar observador
observer.observe(document.body, {
    childList: true,
    subtree: true
});

// Limpiar al descargar la página
window.addEventListener('beforeunload', () => {
    observer.disconnect();
});