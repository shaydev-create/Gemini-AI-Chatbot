#!/bin/bash
# ===============================================================================
# 🚀 SCRIPT DE DEPLOYMENT AUTOMATIZADO - GEMINI AI CHATBOT
#
# Este script automatiza el despliegue completo de la aplicación, incluyendo
# la configuración del servidor, base de datos, Gunicorn y Nginx.
#
# Uso:
#   export DOMAIN_NAME="tudominio.com"
#   export ADMIN_EMAIL="admin@tudominio.com"
#   export DB_PASSWORD="your-secure-database-password"
#   sudo -E bash deploy.sh deploy
#
# ===============================================================================

set -euo pipefail # Salir en caso de error, variables no definidas o errores en pipes

# --- Configuración (Editable) ---
# Variables que pueden ser sobrescritas por variables de entorno.
readonly APP_NAME="gemini-ai-chatbot"
readonly APP_USER="${APP_USER:-gemini}" # Usuario del sistema para la aplicación
readonly APP_GROUP="${APP_GROUP:-gemini}"
readonly APP_DIR="/var/www/${APP_NAME}"
readonly GIT_REPO="https://github.com/shaydev-create/Gemini-AI-Chatbot.git"
readonly VENV_DIR="${APP_DIR}/venv"

readonly DB_NAME="${DB_NAME:-gemini_prod}"
readonly DB_USER="${DB_USER:-gemini_user}"

# --- Variables de Entorno Requeridas ---
: "${DOMAIN_NAME:?La variable de entorno DOMAIN_NAME debe estar definida (ej: tudominio.com)}"
: "${ADMIN_EMAIL:?La variable de entorno ADMIN_EMAIL debe estar definida (ej: admin@tudominio.com)}"
: "${DB_PASSWORD:?La variable de entorno DB_PASSWORD debe estar definida}"

# --- Funciones de Logging ---
log() {
    echo "INFO: $1"
}

log_error() {
    echo "ERROR: $1" >&2
    exit 1
}

# --- Funciones de Despliegue ---

function setup_system() {
    log "Configurando el sistema..."
    # Crear usuario y grupo para la aplicación si no existen
    if ! id -u "${APP_USER}" >/dev/null 2>&1; then
        log "Creando usuario del sistema '${APP_USER}'..."
        useradd -m -r -s /bin/false "${APP_USER}"
    fi

    log "Instalando dependencias del sistema..."
    apt-get update
    apt-get install -y python3-pip python3-venv nginx postgresql certbot python3-certbot-nginx git curl
}

function setup_database() {
    log "Configurando la base de datos PostgreSQL..."
    # Usar -U postgres para ejecutar comandos como el usuario postgres
    sudo -u postgres psql -c "CREATE DATABASE ${DB_NAME};" || log "La base de datos '${DB_NAME}' ya existe."
    sudo -u postgres psql -c "CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';" || log "El usuario '${DB_USER}' ya existe."
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};"
    sudo -u postgres psql -c "ALTER DATABASE ${DB_NAME} OWNER TO ${DB_USER};"
    log "Base de datos configurada."
}

function deploy_code() {
    log "Desplegando el código de la aplicación..."
    mkdir -p "${APP_DIR}"

    if [ ! -d "${APP_DIR}/.git" ]; then
        log "Clonando el repositorio..."
        git clone "${GIT_REPO}" "${APP_DIR}"
    else
        log "Actualizando el repositorio..."
        # Asegurarse de que el directorio pertenece al usuario correcto antes de hacer pull
        chown -R "${APP_USER}:${APP_GROUP}" "${APP_DIR}"
        sudo -u "${APP_USER}" git -C "${APP_DIR}" pull
    fi

    log "Configurando el entorno virtual de Python..."
    # Crear venv como el usuario de la app
    sudo -u "${APP_USER}" python3 -m venv "${VENV_DIR}"

    log "Instalando dependencias de Python..."
    # Activar venv y instalar dependencias
    sudo -u "${APP_USER}" "${VENV_DIR}/bin/pip" install --upgrade pip
    sudo -u "${APP_USER}" "${VENV_DIR}/bin/pip" install -r "${APP_DIR}/requirements.txt"

    log "Aplicando migraciones de la base de datos..."
    # Las variables de entorno para la DB deben estar disponibles
    export DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@localhost/${DB_NAME}"
    sudo -u "${APP_USER}" -E "${VENV_DIR}/bin/flask" db upgrade

    # Establecer permisos finales
    chown -R "${APP_USER}:${APP_GROUP}" "${APP_DIR}"
    log "Código desplegado y dependencias instaladas."
}

function setup_gunicorn() {
    log "Configurando el servicio de Gunicorn..."
    # Crear archivo de entorno para el servicio systemd
    cat > "/etc/${APP_NAME}.conf" << EOF
FLASK_ENV=production
PORT=5000
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@localhost/${DB_NAME}
# Añade aquí otras variables de entorno necesarias (ej. SECRET_KEY, JWT_SECRET_KEY)
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
EOF

    # Crear el archivo de servicio systemd
    cat > "/etc/systemd/system/${APP_NAME}.service" << EOF
[Unit]
Description=Gunicorn service for ${APP_NAME}
After=network.target

[Service]
User=${APP_USER}
Group=${APP_GROUP}
WorkingDirectory=${APP_DIR}
EnvironmentFile=/etc/${APP_NAME}.conf
ExecStart=${VENV_DIR}/bin/gunicorn --config ${APP_DIR}/deployment/gunicorn.conf.py app:create_app()
Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

    log "Habilitando e iniciando el servicio Gunicorn..."
    systemctl daemon-reload
    systemctl enable "${APP_NAME}"
    systemctl start "${APP_NAME}"
    log "Servicio Gunicorn configurado y en ejecución."
}

function setup_nginx() {
    log "Configurando Nginx como reverse proxy..."
    # Deshabilitar el sitio por defecto
    rm -f /etc/nginx/sites-enabled/default

    cat > "/etc/nginx/sites-available/${APP_NAME}" << EOF
server {
    listen 80;
    server_name ${DOMAIN_NAME} www.${DOMAIN_NAME};

    # Redirigir HTTP a HTTPS
    location / {
        return 301 https://\$host\$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name ${DOMAIN_NAME} www.${DOMAIN_NAME};

    # Ubicaciones de los certificados (serán gestionadas por Certbot)
    ssl_certificate /etc/letsencrypt/live/${DOMAIN_NAME}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN_NAME}/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Headers de seguridad
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias ${APP_DIR}/app/static;
        expires 1y;
        access_log off;
        add_header Cache-Control "public, immutable";
    }
}
EOF

    ln -sf "/etc/nginx/sites-available/${APP_NAME}" "/etc/nginx/sites-enabled/"
    nginx -t || log_error "La configuración de Nginx tiene errores."
    systemctl reload nginx
    log "Nginx configurado."
}

function setup_ssl() {
    log "Configurando SSL con Certbot (Let's Encrypt)..."
    # Detener Nginx temporalmente para que Certbot pueda usar el puerto 80
    systemctl stop nginx
    certbot certonly --standalone -d "${DOMAIN_NAME}" -d "www.${DOMAIN_NAME}" --non-interactive --agree-tos -m "${ADMIN_EMAIL}"
    # Volver a iniciar Nginx
    systemctl start nginx
    log "Certificados SSL generados e instalados."
}

# --- Función Principal ---
main() {
    case "${1:-}" in
        "deploy")
            log "Iniciando despliegue completo..."
            setup_system
            setup_database
            deploy_code
            setup_gunicorn
            setup_nginx
            setup_ssl
            log "✅ Despliegue completado exitosamente."
            log "🌐 Tu aplicación debería estar disponible en: https://${DOMAIN_NAME}"
            ;;
        "restart")
            log "Reiniciando servicios..."
            systemctl restart "${APP_NAME}"
            systemctl reload nginx
            log "✅ Servicios reiniciados."
            ;;
        *)
            echo "Uso: $0 {deploy|restart}"
            echo "  deploy  - Ejecuta el proceso de despliegue completo."
            echo "  restart - Reinicia los servicios de Gunicorn y Nginx."
            exit 1
            ;;
    esac
}

# --- Punto de Entrada ---
# Verificar que se ejecuta como root
if [ "$EUID" -ne 0 ]; then
    log_error "Este script debe ejecutarse como root. Usa 'sudo -E bash $0 ...' para preservar las variables de entorno."
fi

main "$@"