@echo off
echo ========================================
echo  HSE Agent - DEVELOPMENT MODE
echo ========================================
echo.
echo This will start:
echo - Backend services in Docker
echo - Frontend in development mode (hot reload)
echo.
pause

REM Start backend services in Docker
echo Starting backend services in Docker...
start "Backend Services" cmd /k "docker-compose -f docker-compose.frontend.yml up postgres redis minio weaviate transformers backend"

REM Wait for backend to be ready
echo Waiting for backend to start...
timeout /t 10 /nobreak > nul

REM Start frontend in dev mode
echo Starting frontend in development mode...
cd frontend

REM Check if node_modules exists
if not exist node_modules (
    echo Installing frontend dependencies first time setup...
    call npm install
)

start "Frontend Dev" cmd /k "npm run dev"

echo.
echo ========================================
echo  Services are starting...
echo ========================================
echo.
echo Frontend (dev): http://localhost:3000
echo Backend API: http://localhost:8000/docs
echo.
echo To stop: Close both command windows
echo.
pause