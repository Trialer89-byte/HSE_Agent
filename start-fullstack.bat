@echo off
echo Starting HSE Multi-Tenant System with Frontend...

REM Check if Docker is running
docker version >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not running. Please start Docker Desktop.
    pause
    exit /b 1
)

REM Check for environment file
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
)

REM Start the full stack
echo Starting all services...
docker-compose -f docker-compose.frontend.yml up --build

pause