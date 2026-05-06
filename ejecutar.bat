@echo off
title Buscador de Definiciones Multi-API
echo ===================================================
echo    BUSCADOR DE DEFINICIONES MULTI-API v2.0
echo ===================================================
echo.
echo Autor: Christian Lera
echo.
echo Iniciando el programa...

:: Verificar si Python está instalado
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH.
    echo.
    echo Descarga Python desde: https://www.python.org/downloads/
    echo Asegurate de marcar "Add Python to PATH" durante la instalacion.
    echo.
    pause
    exit /b 1
)

:: Verificar si existe el archivo principal
if not exist "BuscadorDeDefiniciones.py" (
    echo ERROR: No se encuentra el archivo BuscadorDeDefiniciones.py
    echo Asegurate de que este archivo .bat esta en la misma carpeta que el programa.
    echo.
    pause
    exit /b 1
)

:: Verificar si requests está instalado
python -c "import requests" > nul 2>&1
if errorlevel 1 (
    echo ADVERTENCIA: La libreria 'requests' no esta instalada.
    echo ¿Deseas instalarla ahora? (S/N)
    set /p instalar=
    if /i "%instalar%"=="S" (
        echo Instalando requests...
        pip install requests
        echo.
    ) else (
        echo Continuando sin requests... Algunas APIs podrian fallar.
        echo.
    )
)

:: Ejecutar el programa
echo.
echo Ejecutando Buscador de Definiciones...
echo.
python BuscadorDeDefiniciones.py

:: Pausar si hubo error
if errorlevel 1 (
    echo.
    echo El programa se cerro con un error.
    echo.
    pause
)