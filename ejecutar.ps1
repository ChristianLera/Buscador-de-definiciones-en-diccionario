# ====================================================
# Ejecutar - Buscador de Definiciones Multi-API
# PowerShell Script
# Autor: Christian Lera
# ====================================================

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "   BUSCADOR DE DEFINICIONES MULTI-API v2.0" -ForegroundColor Yellow
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Autor: Christian Lera" -ForegroundColor Green
Write-Host ""

# Verificar Python
Write-Host "Verificando Python..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "$pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python no esta instalado o no esta en el PATH." -ForegroundColor Red
    Write-Host ""
    Write-Host "Descarga Python desde: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Asegurate de marcar 'Add Python to PATH' durante la instalacion." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Presiona Enter para salir"
    exit 1
}
Write-Host ""

# Verificar archivo principal
if (-not (Test-Path "BuscadorDeDefiniciones.py")) {
    Write-Host "ERROR: No se encuentra el archivo BuscadorDeDefiniciones.py" -ForegroundColor Red
    Write-Host "Asegurate de que este script .ps1 esta en la misma carpeta que el programa." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Verificar requests
Write-Host "Verificando dependencias..." -ForegroundColor Cyan
try {
    python -c "import requests" 2>&1 | Out-Null
    Write-Host "Libreria 'requests' encontrada." -ForegroundColor Green
} catch {
    Write-Host "ADVERTENCIA: La libreria 'requests' no esta instalada." -ForegroundColor Yellow
    Write-Host ""
    $instalar = Read-Host "¿Deseas instalarla ahora? (S/N)"
    if ($instalar -eq "S" -or $instalar -eq "s") {
        Write-Host "Instalando requests..." -ForegroundColor Cyan
        pip install requests
        Write-Host ""
    } else {
        Write-Host "Continuando sin requests... Algunas APIs podrian fallar." -ForegroundColor Red
        Write-Host ""
    }
}

# Ejecutar programa
Write-Host "Ejecutando Buscador de Definiciones..." -ForegroundColor Green
Write-Host ""
python BuscadorDeDefiniciones.py

# Pausar si hubo error
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "El programa se cerro con un error." -ForegroundColor Red
    Write-Host ""
    Read-Host "Presiona Enter para salir"
}