# Test authentication and documents API

# 1. Login to get token
Write-Host "Logging in..." -ForegroundColor Green
$loginBody = @{
    username = "admin"
    password = "HSEAdmin2024!"
} | ConvertTo-Json

$loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
    -Method POST `
    -ContentType "application/json" `
    -Body $loginBody

Write-Host "Login successful!" -ForegroundColor Green
Write-Host "Token: $($loginResponse.access_token)" -ForegroundColor Yellow

# 2. Get documents using the token
Write-Host "`nFetching documents..." -ForegroundColor Green
$headers = @{
    "Authorization" = "Bearer $($loginResponse.access_token)"
}

$documentsResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/documents/" `
    -Method GET `
    -Headers $headers

Write-Host "Documents retrieved successfully!" -ForegroundColor Green
$documentsResponse | ConvertTo-Json -Depth 10