@echo off
echo Creating work permit...

REM Prima ottieni il token
curl -s -X POST "http://localhost:8000/api/v1/auth/login" ^
  -H "Content-Type: application/json" ^
  -d "{\"username\": \"superadmin\", \"password\": \"SuperAdmin123!\"}" > temp_login.json

REM Estrai il token (questo è un workaround semplice)
echo.
echo Login successful! Now creating permit...
echo.

REM Crea il permit
curl -X POST "http://localhost:8000/api/v1/permits" ^
  -H "Content-Type: application/json" ^
  -H "accept: application/json" ^
  -H "X-Tenant-Domain: demo.hse-system.com" ^
  -H "Authorization: Bearer <INSERISCI_TOKEN_QUI>" ^
  -d "{\"title\": \"Test Permit\", \"description\": \"Test description\", \"work_type\": \"maintenance\", \"location\": \"Area 1\", \"duration_hours\": 2, \"priority_level\": \"medium\"}"

echo.
pause