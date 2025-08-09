@echo off
echo ========================================
echo  HSE Agent - STOP ALL SERVICES
echo ========================================
echo.
echo This will stop all Docker containers and services
echo.
pause

echo Stopping Docker services...
docker-compose -f docker-compose.frontend.yml down

echo.
echo ========================================
echo  All services stopped
echo ========================================
echo.
echo Note: If you were running frontend in dev mode,
echo manually close that command window too.
echo.
pause