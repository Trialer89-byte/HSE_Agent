@echo off
echo ========================================
echo  HSE Agent - SETUP AND START DEV MODE
echo ========================================
echo.
echo This will:
echo 1. Install frontend dependencies (if needed)
echo 2. Start backend services in Docker
echo 3. Start frontend in development mode
echo.
pause

REM Check if npm is installed
where npm >nul 2>&1
if errorlevel 1 (
    echo ERROR: npm is not installed. Please install Node.js first.
    echo Download from: https://nodejs.org/
    pause
    exit /b 1
)

REM Start backend services in Docker
echo Starting backend services in Docker...
start "Backend Services" cmd /k "docker-compose -f docker-compose.frontend.yml up postgres redis minio weaviate transformers backend"

REM Install frontend dependencies
echo.
echo Checking frontend dependencies...
cd frontend
if not exist node_modules (
    echo Installing frontend dependencies (this may take a few minutes)...
    call npm install
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo Dependencies installed successfully!
) else (
    echo Dependencies already installed.
)

REM Wait for backend to be ready
echo.
echo Waiting for backend to start...
timeout /t 10 /nobreak > nul

REM Start frontend in dev mode
echo Starting frontend in development mode...
start "Frontend Dev" cmd /k "npm run dev"

cd ..
echo.
echo ========================================
echo  Services are starting...
echo ========================================
echo.
echo Frontend (dev): http://localhost:3000
echo Backend API: http://localhost:8000/docs
echo.
echo Note: The frontend may take 10-20 seconds to compile initially.
echo.
echo To stop: Close both command windows
echo.
pause