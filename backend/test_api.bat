@echo off
echo Testing HSE API Authentication...

echo.
echo 1. Login with admin credentials:
curl -X POST "http://localhost:8000/api/v1/auth/login" -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"HSEAdmin2024!\"}"

echo.
echo.
echo 2. If login successful, copy the access_token from above and use it to test documents API
echo.