# 🚀 Guía Completa de Deployment en Vercel

## 📋 Resumen
Esta guía te llevará paso a paso para deployar tu **Gemini AI Chatbot** en Vercel de manera profesional.

## ✅ Archivos Configurados

Tu proyecto ya tiene todo configurado para Vercel:

- ✅ `vercel.json` - Configuración optimizada
- ✅ `.vercelignore` - Archivos excluidos del deployment
- ✅ `.env.vercel` - Template de variables de entorno
- ✅ `deploy_vercel.py` - Script de deployment automático

## 🎯 Pasos para Conectar con Vercel

### 1. 📦 Instalar Vercel CLI
```bash
# Instalar globalmente
npm i -g vercel

# Verificar instalación
vercel --version
```

### 2. 🔐 Login en Vercel
```bash
vercel login
```
- Se abrirá tu navegador
- Inicia sesión con GitHub, GitLab o email
- Autoriza la aplicación

### 3. 🔗 Conectar Proyecto
```bash
# En la carpeta de tu proyecto
vercel

# Responde las preguntas:
# ? Set up and deploy "~/gemini-ai-chatbot"? [Y/n] Y
# ? Which scope do you want to deploy to? [tu-usuario]
# ? Link to existing project? [y/N] N
# ? What's your project's name? gemini-ai-chatbot
# ? In which directory is your code located? ./
```

### 4. ⚙️ Configurar Variables de Entorno

#### Opción A: Dashboard Web
1. Ve a [Vercel Dashboard](https://vercel.com/dashboard)
2. Selecciona tu proyecto `gemini-ai-chatbot`
3. Ve a **Settings > Environment Variables**
4. Agrega estas variables:

| Variable | Valor | Entorno |
|----------|-------|---------|
| `SECRET_KEY` | `tu-clave-secreta-super-segura` | Production, Preview |
| `GOOGLE_API_KEY` | `tu-google-api-key` | Production, Preview |
| `FLASK_ENV` | `production` | Production |
| `FLASK_DEBUG` | `False` | Production, Preview |
| `GEMINI_MODEL` | `gemini-1.5-flash` | Production, Preview |

#### Opción B: CLI
```bash
# Agregar variables una por una
vercel env add SECRET_KEY
vercel env add GOOGLE_API_KEY
vercel env add FLASK_ENV
vercel env add FLASK_DEBUG
vercel env add GEMINI_MODEL
```

### 5. 🚀 Deploy a Producción
```bash
# Deploy automático con script
python deploy_vercel.py

# O manual
vercel --prod
```

## 🌐 URLs de tu Aplicación

Después del deployment tendrás:

- **Preview URL**: `https://gemini-ai-chatbot-xxx.vercel.app`
- **Production URL**: `https://gemini-ai-chatbot.vercel.app`
- **Custom Domain**: Tu dominio personalizado (opcional)

## 🔧 Configuración Avanzada

### Dominios Personalizados
```bash
# Agregar dominio personalizado
vercel domains add tu-dominio.com

# Configurar DNS
# A record: 76.76.19.61
# CNAME: cname.vercel-dns.com
```

### Monitoreo y Analytics
1. Ve a tu proyecto en Vercel Dashboard
2. Pestaña **Analytics** para métricas
3. Pestaña **Functions** para logs de serverless

### Configuración de Team
```bash
# Crear team
vercel teams create mi-team

# Invitar miembros
vercel teams invite usuario@email.com
```

## 🐛 Troubleshooting

### Error: "Build Failed"
```bash
# Ver logs detallados
vercel logs

# Verificar vercel.json
cat vercel.json

# Verificar requirements.txt
pip install -r requirements.txt
```

### Error: "Function Timeout"
- Aumenta `maxDuration` en `vercel.json`
- Optimiza tu código para ser más rápido
- Considera usar Edge Functions

### Error: "Environment Variables"
```bash
# Listar variables
vercel env ls

# Verificar valores
vercel env pull .env.local
```

## 📊 Optimizaciones

### Performance
- ✅ Caching automático de assets estáticos
- ✅ Compresión Gzip/Brotli
- ✅ CDN global
- ✅ Edge Functions para latencia mínima

### Seguridad
- ✅ Headers de seguridad configurados
- ✅ HTTPS automático
- ✅ Variables de entorno encriptadas

### Monitoreo
- ✅ Analytics integrados
- ✅ Logs en tiempo real
- ✅ Alertas de errores

## 🎯 Comandos Útiles

```bash
# Ver información del proyecto
vercel ls

# Ver logs en tiempo real
vercel logs --follow

# Rollback a versión anterior
vercel rollback [deployment-url]

# Eliminar deployment
vercel rm [deployment-url]

# Ver dominios
vercel domains ls

# Configurar alias
vercel alias set [deployment-url] [alias]
```

## 🔄 Workflow Recomendado

### Desarrollo
1. Desarrolla localmente
2. Commit cambios a Git
3. Push a rama de feature
4. Vercel crea preview automático
5. Revisa preview URL

### Producción
1. Merge a rama main
2. Vercel deploya automáticamente a producción
3. Verifica en production URL
4. Monitorea analytics y logs

## 🎉 ¡Listo!

Tu **Gemini AI Chatbot** está ahora deployado profesionalmente en Vercel con:

- 🚀 **Deploy automático** en cada push
- 🌍 **CDN global** para máxima velocidad
- 🔒 **HTTPS** y seguridad automática
- 📊 **Analytics** y monitoreo integrado
- 🔧 **Escalabilidad** automática

**¡Tu chatbot está listo para el mundo! 🌟**