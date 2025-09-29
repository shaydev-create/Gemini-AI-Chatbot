#  Docker Deployment - Gemini AI Chatbot

## Requisitos Previos

- Docker instalado (versión 20.10 o superior)
- Docker Compose instalado (versión 1.29 o superior)
- Archivo `.env` configurado con tu `GEMINI_API_KEY`

## Despliegue Rápido

### 1. Configuración Inicial

```bash
# Clonar el repositorio
git clone <tu-repositorio>
cd gemini-ai-chatbot

# Configurar variables de entorno
cp .env.example .env
# Editar .env y agregar tu GEMINI_API_KEY
```

### 2. Construcción y Ejecución

```bash
# Construir y ejecutar en modo desarrollo
docker-compose up --build

# Ejecutar en segundo plano
docker-compose up -d

# Ver logs
docker-compose logs -f
```

### 3. Acceso a la Aplicación

- **Aplicación Web**: http://localhost:5000
- **API Health Check**: http://localhost:5000/health

## Comandos Útiles

```bash
# Detener servicios
docker-compose down

# Reconstruir imagen
docker-compose build --no-cache

# Ver estado de contenedores
docker-compose ps

# Acceder al contenedor
docker-compose exec gemini-ai-chatbot bash

# Ver logs específicos
docker-compose logs gemini-ai-chatbot
```

## Despliegue en Producción

### Con Nginx (Recomendado)

```bash
# Ejecutar con perfil de producción
docker-compose --profile production up -d
```

### Variables de Entorno de Producción

```env
FLASK_ENV=production
GEMINI_API_KEY=tu_api_key_aqui
SECRET_KEY=tu_secret_key_seguro
DATABASE_URL=postgresql://user:pass@host:port/db
```

## Estructura de Volúmenes

- `./logs:/app/logs` - Logs de la aplicación
- `./.env:/app/.env` - Variables de entorno

## Troubleshooting

### Problema: Puerto 5000 ocupado
```bash
# Cambiar puerto en docker-compose.yml
ports:
  - "8080:5000"  # Usar puerto 8080 en lugar de 5000
```

### Problema: Permisos de archivos
```bash
# Dar permisos a directorio de logs
sudo chown -R $USER:$USER logs/
```

### Problema: API Key no funciona
```bash
# Verificar variables de entorno
docker-compose exec gemini-ai-chatbot env | grep GEMINI
```

## Monitoreo

### Health Check
La aplicación incluye un health check automático que verifica:
- Estado de la aplicación Flask
- Conectividad con la API de Gemini
- Disponibilidad de recursos

### Logs
```bash
# Logs en tiempo real
docker-compose logs -f --tail=100

# Logs específicos del servicio
docker-compose logs gemini-ai-chatbot
```

## Escalabilidad

### Múltiples Instancias
```bash
# Escalar a 3 instancias
docker-compose up --scale gemini-ai-chatbot=3
```

### Load Balancer
Para producción, considera usar:
- Nginx como load balancer
- Traefik para routing automático
- Kubernetes para orquestación avanzada

## Seguridad

-  Contenedor no-root
-  Variables de entorno seguras
-  Volúmenes limitados
-  Health checks configurados
-  Restart policies definidas

## Backup y Restauración

```bash
# Backup de logs
docker run --rm -v gemini_logs:/data -v $(pwd):/backup alpine tar czf /backup/logs-backup.tar.gz -C /data .

# Restaurar logs
docker run --rm -v gemini_logs:/data -v $(pwd):/backup alpine tar xzf /backup/logs-backup.tar.gz -C /data
```
