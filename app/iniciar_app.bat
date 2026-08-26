@echo off
REM ====================================
REM Análisis de Bienestar Psicológico
REM Universidad Santo Tomás
REM ====================================

echo.
echo ====================================
echo  Análisis de Bienestar Psicológico
echo  Universidad Santo Tomás
echo ====================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no está instalado o no está en el PATH
    pause
    exit /b 1
)

REM Verificar entorno virtual
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Activando entorno virtual...
    call venv\Scripts\activate.bat
) else (
    echo [INFO] No se encontró entorno virtual, usando Python del sistema
)

REM Verificar dependencias
echo.
echo [INFO] Verificando dependencias...
pip install -r requirements_app.txt -q

REM Ejecutar aplicación
echo.
echo [INFO] Iniciando aplicación...
echo [INFO] La aplicación se abrirá en tu navegador
echo [INFO] Para detener presiona Ctrl+C
echo.

streamlit run app/main.py

pause
