@echo off
echo 🧪 HSE Enterprise System - Gemini API Test (Fixed)
echo ==================================================
echo.

REM Check if .env exists
if not exist .env (
    echo 📋 Creating .env file from template...
    copy .env.example .env
    echo.
    echo ⚠️  IMPORTANTE: Aggiungi la tua GEMINI_API_KEY al file .env
    echo    1. Ottieni la chiave da: https://makersuite.google.com/app/apikey
    echo    2. Apri .env e sostituisci: GEMINI_API_KEY=your-gemini-api-key-here
    echo    3. Salva il file e riesegui questo script
    echo.
    notepad .env
    pause
    exit /b 1
)

echo 🔍 Checking Python installation...

REM Try different Python commands
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    set PIP_CMD=pip
    goto :python_found
)

py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py
    set PIP_CMD=py -m pip
    goto :python_found
)

python3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python3
    set PIP_CMD=python3 -m pip
    goto :python_found
)

echo ❌ Python non trovato!
echo.
echo 📥 Come installare Python:
echo   1. Vai su: https://www.python.org/downloads/
echo   2. Scarica Python 3.11 o superiore
echo   3. Durante l'installazione, SPUNTA "Add Python to PATH"
echo   4. Riavvia il Command Prompt
echo   5. Riesegui questo script
echo.
pause
exit /b 1

:python_found
echo ✅ Python found: %PYTHON_CMD%

echo 📦 Installing Python dependencies...
cd backend

%PIP_CMD% install google-generativeai python-dotenv
if errorlevel 1 (
    echo ❌ Failed to install dependencies with pip
    echo.
    echo 🔧 Alternative install methods:
    echo   1. Try: %PYTHON_CMD% -m pip install google-generativeai python-dotenv
    echo   2. Or:  %PYTHON_CMD% -m pip install --user google-generativeai python-dotenv
    echo   3. Check internet connection
    echo.
    
    echo ❓ Try alternative install? (s/n)
    set /p try_alt="> "
    if /i "%try_alt%"=="s" (
        echo Trying alternative method...
        %PYTHON_CMD% -m pip install --user google-generativeai python-dotenv
        if errorlevel 1 (
            echo ❌ Alternative method also failed
            echo Please install manually:
            echo   %PIP_CMD% install google-generativeai python-dotenv
            cd ..
            pause
            exit /b 1
        )
    ) else (
        cd ..
        pause
        exit /b 1
    )
)

echo ✅ Dependencies installed successfully!
echo.
echo 🧪 Running Gemini API tests...
%PYTHON_CMD% test_gemini.py

if errorlevel 1 (
    echo.
    echo ❌ Tests failed. Common issues:
    echo    - GEMINI_API_KEY not set or invalid
    echo    - Network connectivity issues
    echo    - Rate limiting (try again in a few minutes)
    echo.
    echo 🔧 Troubleshooting:
    echo    1. Get API key: https://makersuite.google.com/app/apikey
    echo    2. Check .env file has: GEMINI_API_KEY=your-actual-key
    echo    3. Verify internet connection
    echo    4. Try again in 5 minutes (rate limiting)
    echo.
    echo 📝 Your .env file should look like:
    echo    AI_PROVIDER=gemini
    echo    GEMINI_API_KEY=AIzaSyD...your-actual-key-here
    echo    DB_PASSWORD=some_secure_password
    echo.
) else (
    echo.
    echo ✅ Gemini integration ready!
    echo.
    echo 🚀 Next steps:
    echo    1. Start the system: start-windows.bat
    echo    2. Or manually: docker-compose -f docker-compose.enterprise.yml up -d
    echo    3. Test API: http://localhost:8000/api/docs
    echo    4. Login with: admin / HSEAdmin2024!
    echo.
)

cd ..
pause