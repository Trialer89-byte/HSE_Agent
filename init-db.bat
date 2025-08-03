@echo off
echo 🗄️ Inizializzazione Database HSE
echo ================================

REM Copy init script to backend folder temporarily
copy scripts\init-database.py backend\init-database-temp.py

REM Execute inside container
echo 📝 Creazione utente admin e dati iniziali...
docker-compose -f docker-compose.simple.yml exec backend python init-database-temp.py

REM Clean up
del backend\init-database-temp.py

echo.
echo ✅ Database inizializzato!
echo.
echo 🔑 Credenziali Admin:
echo    Username: admin
echo    Password: HSEAdmin2024!
echo.
pause