@echo off
echo Starting HSE System (Fast Mode - No Rebuild)...
echo.

REM Stop any running containers
echo Stopping existing containers...
docker-compose -f docker-compose.frontend.yml down

echo.
echo Starting all services...
docker-compose -f docker-compose.frontend.yml up -d

echo.
echo Waiting for services to be ready...
timeout /t 10 /nobreak > nul

echo.
echo System started! Access points:
echo ================================
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8000/docs
echo MinIO Console: http://localhost:9001
echo ================================
echo.
echo To check logs: docker-compose -f docker-compose.frontend.yml logs -f
echo To stop: docker-compose -f docker-compose.frontend.yml down
echo.
pause