@echo off
echo ========================================
echo  INSTALACIÓN RÁPIDA - SISTEMA TURISMO
echo ========================================
echo.

cd /d "%~dp0"

echo Paso 1: Creando entorno virtual...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Python no encontrado. Por favor instala Python 3.8+
    pause
    exit /b 1
)

echo Paso 2: Activando entorno virtual...
call venv\Scripts\activate.bat

echo Paso 3: Instalando dependencias...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias
    pause
    exit /b 1
)

echo.
echo ========================================
echo  CONFIGURACIÓN DE BASE DE DATOS
echo ========================================
echo.
echo Elige una opcion:
echo 1. SQLite (Recomendado - no necesita instalar nada)
echo 2. PostgreSQL (si ya tienes PostgreSQL instalado)
echo.
set /p opcion="Escribe tu opcion (1 o 2): "

if "%opcion%"=="1" (
    echo.
    echo Configurando SQLite...
    (
        echo # Configuracion para pruebas locales
        echo DB_NAME=sqlite:///db.sqlite3
        echo SECRET_KEY=django-insecure-key-demo-local
        echo DEBUG=True
        echo REDIS_URL=redis://localhost:6379/0
    ) > .env
    echo ✅ Configuracion SQLite creada
) else if "%opcion%"=="2" (
    echo.
    echo Configurando PostgreSQL...
    echo Asegurate de tener PostgreSQL corriendo y la base de datos 'turismo_db' creada
    (
        echo DB_NAME=turismo_db
        echo DB_USER=postgres
        echo DB_PASSWORD=password
        echo DB_HOST=localhost
        echo DB_PORT=5432
        echo SECRET_KEY=django-insecure-key-demo-local
        echo DEBUG=True
        echo REDIS_URL=redis://localhost:6379/0
    ) > .env
    echo ✅ Configuracion PostgreSQL creada
    echo ⚠️  Asegurate de crear la base de datos: createdb turismo_db
) else (
    echo Opcion no valida. Usando SQLite por defecto.
    (
        echo DB_NAME=sqlite:///db.sqlite3
        echo SECRET_KEY=django-insecure-key-demo-local
        echo DEBUG=True
        echo REDIS_URL=redis://localhost:6379/0
    ) > .env
)

echo.
echo Paso 4: Ejecutando migraciones...
python manage.py migrate
if errorlevel 1 (
    echo ERROR: Error en migraciones. Verifica la configuracion de la base de datos
    pause
    exit /b 1
)

echo Paso 5: Creando superusuario y datos de prueba...
python setup_local.py
if errorlevel 1 (
    echo ADVERTENCIA: Hubo errores creando datos de prueba, pero el sistema deberia funcionar
)

echo.
echo ========================================
echo  ¡INSTALACIÓN COMPLETADA!
echo ========================================
echo.
echo Sistema listo para usar:
echo.
echo 🌐 Accesos:
echo    - Dashboard: http://localhost:8000/
echo    - Panel Admin: http://localhost:8000/admin/
echo    - API Health: http://localhost:8000/api/health/
echo.
echo 👤 Credenciales:
echo    - Usuario: piero
echo    - Contraseña: piero12345
echo.
echo 🚀 Para iniciar el servidor:
echo    start_dev.bat
echo.
echo Presiona cualquier tecla para continuar...
pause > nul
