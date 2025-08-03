@echo off
echo 🚀 HSE Enterprise System - Quick Start per Windows
echo ==================================================
echo.

REM Step 1: Check main .env
if not exist .env (
    echo 📋 Creando file .env principale...
    copy .env.example .env
    
    echo ⚠️  CONFIGURAZIONE OBBLIGATORIA:
    echo   1. Ottieni Gemini API Key GRATUITA: https://makersuite.google.com/app/apikey
    echo   2. Apri il file .env che si sta aprendo ora
    echo   3. Sostituisci GEMINI_API_KEY=your-gemini-api-key-here con la tua chiave
    echo   4. Salva il file
    echo.
    
    notepad .env
    
    echo ❓ Hai configurato GEMINI_API_KEY? (s/n)
    set /p configured="> "
    if /i not "%configured%"=="s" (
        echo ⏸️  Configura prima GEMINI_API_KEY in .env
        pause
        exit /b 1
    )
)

echo ✅ File .env principale presente

REM Step 2: Stop any existing containers
echo 🛑 Fermando eventuali container esistenti...
docker-compose -f docker-compose.simple.yml down 2>nul

REM Step 3: Pull images
echo 📦 Scaricando immagini Docker (può richiedere tempo)...
docker-compose -f docker-compose.simple.yml pull

REM Step 4: Start services
echo 🐳 Avviando servizi...
docker-compose -f docker-compose.simple.yml up -d

REM Step 5: Wait and check
echo ⏳ Attendendo avvio servizi (60 secondi)...
timeout /t 60 >nul

echo 🏥 Verificando stato servizi...
docker-compose -f docker-compose.simple.yml ps

REM Step 6: Check backend health
echo 🔍 Verificando backend...
curl -f -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Backend non ancora pronto. Attendere altri 30 secondi...
    timeout /t 30 >nul
    curl -f -s http://localhost:8000/health >nul 2>&1
    if errorlevel 1 (
        echo ❌ Backend non risponde. Verifica i log:
        echo    docker-compose -f docker-compose.simple.yml logs backend
        echo.
        docker-compose -f docker-compose.simple.yml logs --tail=20 backend
    ) else (
        echo ✅ Backend OK!
    )
) else (
    echo ✅ Backend OK!
)

REM Step 7: Initialize database
echo 🗄️  Inizializzando database...

REM Check if Python is available
py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py
) else (
    python --version >nul 2>&1
    if not errorlevel 1 (
        set PYTHON_CMD=python
    ) else (
        echo ⚠️  Python non trovato. Inizializzazione database manuale richiesta.
        goto :skip_db_init
    )
)

REM Install dependencies and run init
cd backend
%PYTHON_CMD% -m pip install -r requirements.txt --quiet
cd ..
%PYTHON_CMD% scripts\init-database.py

if errorlevel 1 (
    echo ⚠️  Inizializzazione database fallita. Puoi riprovare manualmente:
    echo    python scripts\init-database.py
)

:skip_db_init

echo.
echo 🎉 SISTEMA HSE AVVIATO!
echo ======================
echo.
echo 🌐 Accessi:
echo   Backend API:    http://localhost:8000
echo   API Docs:       http://localhost:8000/api/docs
echo   Health Check:   http://localhost:8000/health
echo   System Info:    http://localhost:8000/api/v1/system/info
echo.
echo 🔑 Credenziali Default:
echo   Username: admin
echo   Password: HSEAdmin2024!
echo.
echo 🤖 AI Provider: Gemini (Google)
echo   Costo: GRATUITO con rate limits
echo.
echo 🧪 Test Rapido:
echo   1. Apri: http://localhost:8000/api/docs
echo   2. Clicca "Authorize" e fai login
echo   3. Testa POST /api/v1/permits/ per creare un permesso
echo   4. Testa POST /api/v1/permits/{id}/analyze per analisi AI
echo.
echo 📊 Stato Servizi:
docker-compose -f docker-compose.simple.yml ps
echo.
echo 🛑 Per fermare il sistema:
echo   docker-compose -f docker-compose.simple.yml down
echo.
echo 📋 Per vedere i log:
echo   docker-compose -f docker-compose.simple.yml logs -f backend
echo.
pause