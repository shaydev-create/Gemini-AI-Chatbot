# Script para automatizar activación de entorno, instalación de dependencias y ejecución de tests

Write-Host "Activando entorno virtual..."
. .\.venv\Scripts\Activate.ps1

Write-Host "Instalando flask-migrate en el entorno virtual..."
pip install flask-migrate

Write-Host "Ejecutando pruebas automáticas..."
pytest --maxfail=5 --disable-warnings --cov=app --cov-report=html

Write-Host "Proceso completado. Revisa los resultados de pytest y la cobertura en la carpeta htmlcov."
