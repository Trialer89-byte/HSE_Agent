@echo off
echo 🧪 Test Gemini API - Solo Test Veloce
echo ====================================
echo.

REM Check if main .env exists
if not exist .env (
    echo ❌ File .env non trovato!
    pause
    exit /b 1
)

echo ✅ File .env presente

REM Check Python
py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py
) else (
    python --version >nul 2>&1
    if not errorlevel 1 (
        set PYTHON_CMD=python
    ) else (
        echo ❌ Python non trovato
        echo 📥 Installa Python da: https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

echo ✅ Python trovato: %PYTHON_CMD%

REM Install minimal dependencies
echo 📦 Installando dipendenze minime...
cd backend
%PYTHON_CMD% -m pip install google-generativeai python-dotenv --quiet
if errorlevel 1 (
    echo ❌ Installazione fallita
    echo 🔧 Prova manualmente: pip install google-generativeai python-dotenv
    cd ..
    pause
    exit /b 1
)

echo ✅ Dipendenze installate

REM Check if GEMINI_API_KEY is in .env
findstr /C:"GEMINI_API_KEY=" .env >nul 2>&1
if errorlevel 1 (
    echo ⚠️  GEMINI_API_KEY non trovata in backend\.env
    echo 📝 Aggiungila manualmente o riesegui quick-start.bat
    cd ..
    pause
    exit /b 1
)

echo ✅ GEMINI_API_KEY trovata

REM Simple Python test
echo 🧪 Test Gemini API...
%PYTHON_CMD% -c "
import os
from dotenv import load_dotenv
load_dotenv()

try:
    import google.generativeai as genai
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == 'your-gemini-api-key-here':
        print('❌ GEMINI_API_KEY non configurata correttamente')
        exit(1)
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    response = model.generate_content('Rispondi solo: Test OK')
    print('✅ Gemini API funziona!')
    print('📋 Risposta:', response.text.strip())
    
except Exception as e:
    print('❌ Errore Gemini:', str(e))
    exit(1)
"

if errorlevel 1 (
    echo.
    echo ❌ Test Gemini fallito
    echo 🔧 Possibili cause:
    echo   - API key non valida
    echo   - Problema di rete
    echo   - Rate limiting
    echo.
    echo 🔑 Verifica la tua API key su: https://makersuite.google.com/app/apikey
    echo 📝 Controlla che in backend\.env ci sia: GEMINI_API_KEY=AIzaSy...
    echo.
) else (
    echo.
    echo ✅ GEMINI API FUNZIONA PERFETTAMENTE!
    echo.
    echo 🚀 Ora puoi avviare il sistema completo:
    echo   quick-start.bat
    echo.
    echo 🌐 Oppure manualmente:
    echo   docker-compose -f docker-compose.simple.yml up -d
    echo.
)

cd ..
pause