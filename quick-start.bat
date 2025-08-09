@echo off
echo Quick Starting HSE System (no rebuild)...

REM Start without building
docker-compose -f docker-compose.frontend.yml up -d

echo.
echo System starting up...
echo.
echo Access points:
echo - Frontend: http://localhost:3000
echo - Backend API: http://localhost:8000/docs
echo - MinIO Console: http://localhost:9001
echo.
echo To view logs: docker-compose -f docker-compose.frontend.yml logs -f
echo To stop: docker-compose -f docker-compose.frontend.yml down
echo.
pause
