@echo off
echo ========================================
echo     TEST SISTEMA MULTI-TENANT HSE
echo ========================================

echo.
echo 1. TEST LOGIN SUPERADMIN
echo ----------------------------------------
curl -s -X POST "http://localhost:8000/api/v1/auth/login" -H "Content-Type: application/json" -d "{\"username\": \"superadmin\", \"password\": \"SuperAdmin123!\"}" > login_response.json
echo Login eseguito. Risposta salvata in login_response.json

echo.
echo 2. VISUALIZZA DOCUMENTAZIONE API
echo ----------------------------------------
echo Apri il browser e vai a:
echo http://localhost:8000/api/docs
echo.

echo.
echo 3. TEST ENDPOINTS DISPONIBILI
echo ----------------------------------------
echo Health Check:
curl -s "http://localhost:8000/health"
echo.
echo.

echo.
echo 4. INFO SISTEMA
echo ----------------------------------------
curl -s "http://localhost:8000/"
echo.
echo.

echo ========================================
echo Per test avanzati, usa la documentazione
echo interattiva su http://localhost:8000/api/docs
echo ========================================
pause