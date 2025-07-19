#!/bin/bash
# ===============================================================================
# 🚀 SCRIPT DE DEPLOYMENT - GEMINI AI CHATBOT
# ===============================================================================

set -e  # Salir si hay errores

echo "🚀 Iniciando deployment de Gemini AI Chatbot..."

# Variables
APP_NAME="gemini-chatbot"
APP_DIR="/var/www/$APP_NAME"
BACKUP_DIR="/var/backups/$APP_NAME"
DATE=$(date +%Y%m%d_%H%M%S)

# Funciones
create_backup() {
    echo "📦 Creando backup..."
    mkdir -p $BACKUP_DIR
    if [ -d "$APP_DIR" ]; then
        tar -czf "$BACKUP_DIR/backup_$DATE.tar.gz" -C "$APP_DIR" .
        echo "✅ Backup creado: $BACKUP_DIR/backup_$DATE.tar.gz"
    fi
}

install_dependencies() {
    echo "📦 Instalando dependencias del sistema..."
    apt-get update
    apt-get install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib
}

setup_database() {
    echo "🗄️ Configurando base de datos PostgreSQL..."
    sudo -u postgres createdb gemini_chatbot_prod || true
    sudo -u postgres psql -c "CREATE USER gemini_user WITH PASSWORD 'secure_password';" || true
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE gemini_chatbot_prod TO gemini_user;" || true
}

deploy_app() {
    echo "🚀 Desplegando aplicación..."
    
    # Crear directorio de aplicación
    mkdir -p $APP_DIR
    cd $APP_DIR
    
    # Clonar o actualizar código
    if [ ! -d ".git" ]; then
        git clone https://github.com/tu-usuario/gemini-chatbot.git .
    else
        git pull origin main
    fi
    
    # Crear entorno virtual
    python3 -m venv venv
    source venv/bin/activate
    
    # Instalar dependencias Python
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install gunicorn psycopg2-binary
    
    # Configurar variables de entorno
    cp .env.production .env
    
    # Inicializar base de datos
    python -c "from app import app, db; app.app_context().push(); db.create_all()"
}

setup_gunicorn() {
    echo "⚙️ Configurando Gunicorn..."
    
    cat > /etc/systemd/system/gemini-chatbot.service << EOF
[Unit]
Description=Gemini AI Chatbot
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable gemini-chatbot
    systemctl start gemini-chatbot
}

setup_nginx() {
    echo "🌐 Configurando Nginx..."
    
    cat > /etc/nginx/sites-available/gemini-chatbot << EOF
server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tu-dominio.com www.tu-dominio.com;

    ssl_certificate /etc/ssl/certs/tu-dominio.com.crt;
    ssl_certificate_key /etc/ssl/private/tu-dominio.com.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias $APP_DIR/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

    ln -sf /etc/nginx/sites-available/gemini-chatbot /etc/nginx/sites-enabled/
    nginx -t
    systemctl reload nginx
}

setup_ssl() {
    echo "🔒 Configurando SSL con Let's Encrypt..."
    apt-get install -y certbot python3-certbot-nginx
    certbot --nginx -d tu-dominio.com -d www.tu-dominio.com --non-interactive --agree-tos --email admin@tu-dominio.com
}

setup_monitoring() {
    echo "📊 Configurando monitoreo..."
    
    # Logrotate
    cat > /etc/logrotate.d/gemini-chatbot << EOF
/var/log/gemini-chatbot/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
}
EOF

    # Cron para backup
    echo "0 2 * * * root $0 backup" >> /etc/crontab
}

# Función principal
main() {
    case "$1" in
        "deploy")
            create_backup
            install_dependencies
            setup_database
            deploy_app
            setup_gunicorn
            setup_nginx
            setup_ssl
            setup_monitoring
            echo "✅ Deployment completado!"
            echo "🌐 Tu aplicación está disponible en: https://tu-dominio.com"
            ;;
        "backup")
            create_backup
            ;;
        "restart")
            systemctl restart gemini-chatbot
            systemctl reload nginx
            echo "✅ Servicios reiniciados"
            ;;
        *)
            echo "Uso: $0 {deploy|backup|restart}"
            echo "  deploy  - Despliega la aplicación completa"
            echo "  backup  - Crea backup de la aplicación"
            echo "  restart - Reinicia los servicios"
            exit 1
            ;;
    esac
}

# Verificar que se ejecuta como root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script debe ejecutarse como root"
    exit 1
fi

main "$@"