@echo off
echo ========================================
echo  Sistema de Gestion Turistica - Dev
echo ========================================
echo.

cd /d "%~dp0"

echo Verificando entorno virtual...
if exist venv\Scripts\activate.bat (
    echo Activando entorno virtual...
    call venv\Scripts\activate.bat
) else (
    echo Entorno virtual no encontrado. Por favor, ejecuta setup_local.py primero.
    pause
    exit /b 1
)

echo.
echo Iniciando servidor de desarrollo...
echo El servidor estara disponible en:
echo   - Dashboard: http://localhost:8000/
echo   - Panel Admin: http://localhost:8000/admin/
echo   - API Health: http://localhost:8000/api/health/
echo.
echo Credenciales:
echo   - Usuario: piero
echo   - Contraseña: piero12345
echo.
echo Presiona Ctrl+C para detener el servidor.
echo.

python manage.py runserver

pause
