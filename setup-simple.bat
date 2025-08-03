@echo off
echo 🚀 HSE Enterprise System - Setup Semplificato
echo =============================================
echo.

echo ⚠️  PREREQUISITI NECESSARI:
echo   1. Docker Desktop installato e avviato
echo   2. Python 3.11+ installato con pip
echo   3. Gemini API Key gratuita da: https://makersuite.google.com/app/apikey
echo.

echo ❓ Hai tutti i prerequisiti? (s/n)
set /p ready="> "
if /i not "%ready%"=="s" (
    echo.
    echo 📚 Guida installazione:
    echo   Docker: https://www.docker.com/products/docker-desktop
    echo   Python: https://www.python.org/downloads/ (SPUNTA "Add to PATH"!)
    echo   Gemini: https://makersuite.google.com/app/apikey
    echo.
    pause
    exit /b 1
)

REM Step 1: Setup .env
echo.
echo 📋 Step 1: Configurazione .env
if not exist .env (
    copy .env.example .env
    echo ✅ File .env creato
) else (
    echo ✅ File .env già presente
)

echo.
echo 🔑 Ora inserisci le tue configurazioni:
echo   - GEMINI_API_KEY=your-key-here
echo   - DB_PASSWORD=password-sicura
echo   - JWT_SECRET_KEY=chiave-ultra-sicura
echo.
notepad .env

echo.
echo ❓ Hai completato la configurazione? (s/n)
set /p configured="> "
if /i not "%configured%"=="s" (
    echo ⏸️  Completa il file .env e riesegui lo script
    pause
    exit /b 1
)

REM Step 2: Test Python
echo.
echo 📦 Step 2: Test Python
py --version
if errorlevel 1 (
    python --version
    if errorlevel 1 (
        echo ❌ Python non trovato nel PATH
        echo 🔧 Reinstalla Python con "Add to PATH" spuntato
        pause
        exit /b 1
    )
    set PYTHON_CMD=python
) else (
    set PYTHON_CMD=py
)

echo ✅ Python OK: %PYTHON_CMD%

REM Step 3: Docker
echo.
echo 🐳 Step 3: Test Docker
docker --version
if errorlevel 1 (
    echo ❌ Docker non trovato
    echo 💾 Installa Docker Desktop e riavvia il PC
    pause
    exit /b 1
)

echo ✅ Docker OK

REM Step 4: Install deps and test
echo.
echo 📚 Step 4: Installazione dipendenze Python
cd backend
%PYTHON_CMD% -m pip install google-generativeai python-dotenv
cd ..

echo.
echo 🧪 Step 5: Test Gemini API
cd backend
%PYTHON_CMD% test_gemini.py
if errorlevel 1 (
    echo.
    echo ❌ Test Gemini fallito
    echo 🔧 Verifica:
    echo   - GEMINI_API_KEY corretto nel file .env
    echo   - Connessione internet attiva
    echo   - API key valida (non scaduta)
    echo.
    cd ..
    pause
    exit /b 1
)
cd ..

echo ✅ Test Gemini OK!

REM Step 6: Start system
echo.
echo 🚀 Step 6: Avvio sistema completo
echo Questo potrebbe richiedere alcuni minuti...

docker-compose -f docker-compose.enterprise.yml up -d

echo.
echo ⏳ Attendere avvio servizi (90 secondi)...
timeout /t 90 >nul

echo.
echo 🗄️  Inizializzazione database...
%PYTHON_CMD% scripts\init-database.py

echo.
echo 🎉 SETUP COMPLETATO!
echo ====================
echo.
echo 🌐 Accessi:
echo   API: http://localhost:8000/api/docs
echo   Health: http://localhost:8000/health
echo.
echo 🔑 Login:
echo   User: admin
echo   Pass: HSEAdmin2024!
echo.
echo 🤖 AI: Gemini (gratuito)
echo.
echo 📊 Stato servizi:
docker-compose -f docker-compose.enterprise.yml ps

echo.
echo ✅ Tutto pronto! Apri http://localhost:8000/api/docs per iniziare
pause