@echo off
cd /d "%~dp0"

echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if errorlevel 1 (
        echo.
        echo ERROR: Python no esta instalado o no esta en el PATH.
        echo Descarguelo desde https://www.python.org/downloads/
        echo Al instalar, marque "Add Python to PATH"
        echo.
        pause
        exit /b 1
    )
    set PY=py
) else (
    set PY=python
)

echo Instalando dependencias (solo la primera vez)...
%PY% -m pip install -r requirements.txt -q
if errorlevel 1 (
    echo.
    echo ERROR al instalar dependencias. Intente manualmente:
    echo   %PY% -m pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo.
echo Iniciando aplicacion...
echo Abra en el navegador: http://127.0.0.1:5000
echo No cierre esta ventana mientras use la app.
echo.
%PY% app.py
pause
