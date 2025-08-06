# Test API Multi-Tenant HSE System

# 1. Login e ottieni token
Write-Host "1. LOGIN TEST" -ForegroundColor Green
$loginData = @{
    username = "superadmin"
    password = "SuperAdmin123!"
} | ConvertTo-Json

$loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
    -Method POST `
    -ContentType "application/json" `
    -Body $loginData

$token = $loginResponse.access_token
Write-Host "✓ Login successful! Token obtained." -ForegroundColor Cyan
Write-Host "User: $($loginResponse.user.username) - Role: $($loginResponse.user.role)" -ForegroundColor Yellow

# 2. Test creazione work permit
Write-Host "`n2. CREATE WORK PERMIT TEST" -ForegroundColor Green
$permitData = @{
    title = "Lavoro in spazi confinati - Serbatoio A1"
    description = "Manutenzione interna del serbatoio A1"
    work_type = "confined_space"
    location = "Area Stoccaggio"
    duration_hours = 4
    priority_level = "high"
    dpi_required = @("respiratore", "imbracatura", "rilevatore_gas")
} | ConvertTo-Json

try {
    $permitResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/permits" `
        -Method POST `
        -Headers @{
            "Authorization" = "Bearer $token"
            "X-Tenant-Domain" = "demo.hse-system.com"
        } `
        -ContentType "application/json" `
        -Body $permitData
    
    Write-Host "✓ Work permit created successfully!" -ForegroundColor Cyan
    Write-Host "Permit ID: $($permitResponse.id)" -ForegroundColor Yellow
} 
catch {
    Write-Host "✗ Error creating permit: $_" -ForegroundColor Red
}

# 3. Test lista work permits
Write-Host "`n3. LIST WORK PERMITS TEST" -ForegroundColor Green
try {
    $listResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/permits" `
        -Method GET `
        -Headers @{
            "Authorization" = "Bearer $token"
            "X-Tenant-Domain" = "demo.hse-system.com"
        }
    
    Write-Host "✓ Found $($listResponse.Count) permits" -ForegroundColor Cyan
    foreach ($permit in $listResponse) {
        Write-Host "  - $($permit.title) (ID: $($permit.id))" -ForegroundColor Yellow
    }
} 
catch {
    Write-Host "✗ Error listing permits: $_" -ForegroundColor Red
}

# 4. Test isolamento multi-tenant
Write-Host "`n4. MULTI-TENANT ISOLATION TEST" -ForegroundColor Green
Write-Host "Testing access to different tenant..." -ForegroundColor White

try {
    $crossTenantResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/permits" `
        -Method GET `
        -Headers @{
            "Authorization" = "Bearer $token"
            "X-Tenant-Domain" = "enterprise.hse-system.com"
        }
    
    Write-Host "✓ Access to different tenant - found $($crossTenantResponse.Count) permits" -ForegroundColor Cyan
} 
catch {
    Write-Host "✗ Error accessing different tenant (expected for non-superadmin): $_" -ForegroundColor Yellow
}