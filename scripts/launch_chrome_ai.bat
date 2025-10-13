@echo off
echo 🚀 Iniciando Chrome Canary con Chrome Built-in AI habilitado...
echo.
echo ⚠️  IMPORTANTE: Cierra todas las instancias de Chrome Canary antes de ejecutar
echo.
pause

REM Ruta típica de Chrome Canary en Windows
set CHROME_CANARY="C:\Users\%USERNAME%\AppData\Local\Google\Chrome SxS\Application\chrome.exe"

REM Verificar si existe Chrome Canary
if not exist %CHROME_CANARY% (
    echo ❌ Chrome Canary no encontrado en la ruta esperada
    echo 📥 Descarga Chrome Canary desde: https://www.google.com/chrome/canary/
    pause
    exit /b 1
)

echo 🔧 Lanzando Chrome Canary con APIs de AI habilitadas...
echo.

REM Ejecutar Chrome Canary con todas las flags necesarias
%CHROME_CANARY% ^
    --enable-features=AIAssistantAPI,PromptAPIForGeminiNano,SummarizationAPIForGeminiNano,RewriterAPIForGeminiNano,ComposerAPIForGeminiNano,TranslationAPI ^
    --disable-features=OptimizationGuidePushNotifications ^
    --enable-ai-assistant-api ^
    --user-data-dir="%TEMP%\chrome-ai-profile" ^
    http://127.0.0.1:5000

echo.
echo ✅ Chrome Canary iniciado con Chrome Built-in AI
echo 🌐 Aplicación abierta en: http://127.0.0.1:5000
echo.
echo 💡 NOTA: La primera vez puede tardar en descargar los modelos de AI
pause