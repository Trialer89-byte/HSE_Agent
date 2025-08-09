@echo off
echo ========================================
echo  HSE Agent - PRODUCTION MODE  
echo ========================================
echo.
echo This will start the full system in Docker
echo (Frontend + Backend + All Services)
echo.
echo Choose your option:
echo 1. Quick start (use existing images)
echo 2. Full rebuild (after code changes)
echo.
set /p choice="Enter 1 or 2: "

if "%choice%"=="1" goto quick
if "%choice%"=="2" goto rebuild
echo Invalid choice
pause
exit /b 1

:quick
echo Starting with existing images...
docker-compose -f docker-compose.frontend.yml up -d
goto end

:rebuild
echo Rebuilding and starting (this may take 3-5 minutes)...
docker-compose -f docker-compose.frontend.yml up --build -d
goto end

:end
echo.
echo ========================================
echo  System started in PRODUCTION MODE
echo ========================================
echo.
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8000/docs
echo MinIO Console: http://localhost:9001
echo.
echo To check logs: docker-compose -f docker-compose.frontend.yml logs -f
echo To stop: docker-compose -f docker-compose.frontend.yml down
echo.
pause