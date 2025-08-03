@echo off
echo 🚀 HSE Enterprise System - Windows Quick Start (Gemini)
echo ========================================================
echo.

REM Check prerequisites
echo 📋 Checking prerequisites...

REM Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker non trovato. Installa Docker Desktop:
    echo    https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
echo ✅ Docker OK

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python non trovato. Installa Python 3.11+:
    echo    https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python OK

REM Setup .env file
if not exist .env (
    echo 📋 Creando file .env...
    copy .env.example .env
    
    echo.
    echo ⚠️  CONFIGURAZIONE RICHIESTA:
    echo    1. Ottieni Gemini API Key GRATUITA: https://makersuite.google.com/app/apikey
    echo    2. Genera password sicure per database, redis, etc.
    echo    3. Il file .env è stato aperto automaticamente
    echo.
    
    notepad .env
    
    echo.
    echo ❓ Hai completato la configurazione di .env? (s/n)
    set /p configured="> "
    if /i not "%configured%"=="s" (
        echo ⏸️  Completa la configurazione di .env e riesegui lo script
        pause
        exit /b 1
    )
)

REM Test Gemini API
echo.
echo 🧪 Testing Gemini API integration...
cd backend
pip install google-generativeai python-dotenv >nul 2>&1
python test_gemini.py

if errorlevel 1 (
    echo ❌ Gemini test failed. Verifica:
    echo    - GEMINI_API_KEY nel file .env
    echo    - Connessione internet
    echo    - Validità della API key
    cd ..
    pause
    exit /b 1
)
cd ..

echo ✅ Gemini integration OK!
echo.

REM Create required directories
echo 📁 Creating directories...
if not exist logs mkdir logs
if not exist monitoring\grafana\dashboards mkdir monitoring\grafana\dashboards
if not exist monitoring\grafana\datasources mkdir monitoring\grafana\datasources

REM Start Docker services
echo 🐳 Starting Docker services...
docker-compose -f docker-compose.enterprise.yml pull
docker-compose -f docker-compose.enterprise.yml up -d

echo.
echo ⏳ Waiting for services to start (60 seconds)...
timeout /t 60 >nul

REM Initialize database
echo 🗄️  Initializing database...
cd backend
pip install -r requirements.txt >nul 2>&1
cd ..
python scripts\init-database.py

if errorlevel 1 (
    echo ❌ Database initialization failed
    echo 🔧 Try manual setup:
    echo    python scripts\init-database.py
)

REM Check service health
echo.
echo 🏥 Checking service health...
curl -f -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Backend API not responding yet. May need more time.
    echo    Check manually: http://localhost:8000/health
) else (
    echo ✅ Backend API: OK
)

REM Show final status
echo.
echo 🎉 HSE Enterprise System Started!
echo ===================================
echo.
echo 🌐 Access Points:
echo    Backend API:    http://localhost:8000
echo    API Docs:       http://localhost:8000/api/docs  
echo    Health Check:   http://localhost:8000/health
echo    Traefik Dash:   http://localhost:8080
echo.
echo 🔑 Default Login:
echo    Username: admin
echo    Password: HSEAdmin2024!
echo.
echo 🤖 AI Provider: Gemini (Google)
echo    Model: gemini-1.5-pro
echo    Cost: FREE (con rate limits)
echo.
echo 🧪 Quick Test:
echo    1. Apri: http://localhost:8000/api/docs
echo    2. Login con credenziali admin
echo    3. Crea un permesso di lavoro con POST /api/v1/permits/
echo    4. Testa analisi AI con POST /api/v1/permits/{id}/analyze
echo.
echo 📊 Status containers:
docker-compose -f docker-compose.enterprise.yml ps
echo.
echo 🛑 Per fermare il sistema:
echo    docker-compose -f docker-compose.enterprise.yml down
echo.
echo 📖 Documentazione completa: README.md
echo.
pause