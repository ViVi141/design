# Start All Services

Write-Host "Starting backend and frontend..." -ForegroundColor Green

# Check data directory
if (-not (Test-Path "backend\data")) {
    New-Item -ItemType Directory -Path "backend\data" -Force | Out-Null
}

# Start backend in new window
$backendCmd = "cd '$PSScriptRoot\backend'; & '$PSScriptRoot\.venv\Scripts\Activate.ps1'; uvicorn app.main:app --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd

Start-Sleep -Seconds 5

# Start frontend in new window  
$frontendCmd = "cd '$PSScriptRoot\frontend'; pnpm dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd

Write-Host ""
Write-Host "Services started!" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""

