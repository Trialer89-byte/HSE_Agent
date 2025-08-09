@echo off
echo ========================================
echo  STOP ALL AND RUN DEV MODE ONLY
echo ========================================
echo.
echo Stopping all Docker containers...
docker-compose -f docker-compose.frontend.yml down

echo.
echo Killing any running Node processes...
taskkill /F /IM node.exe 2>nul
if errorlevel 1 echo No Node processes were running

echo.
echo Waiting for ports to be freed...
timeout /t 3 /nobreak > nul

echo.
echo Starting ONLY backend services in Docker (no frontend)...
docker-compose -f docker-compose.frontend.yml up -d postgres redis minio weaviate transformers backend

echo.
echo Waiting for backend to be ready...
timeout /t 10 /nobreak > nul

echo.
echo Starting frontend in development mode...
cd frontend
echo Installing dependencies if needed...
if not exist node_modules (
    call npm install
)

echo.
echo Starting dev server...
npm run dev