# 启动后端服务脚本

# 确保在backend目录
Set-Location -Path "$PSScriptRoot\backend"

# 检查虚拟环境
if (Test-Path "$PSScriptRoot\.venv\Scripts\Activate.ps1") {
    Write-Host "激活虚拟环境..." -ForegroundColor Green
    & "$PSScriptRoot\.venv\Scripts\Activate.ps1"
}

# 检查.env文件
if (-not (Test-Path ".env")) {
    Write-Host "错误: 未找到.env配置文件!" -ForegroundColor Red
    Write-Host "请先配置 backend\.env 文件" -ForegroundColor Yellow
    exit 1
}

# 检查data目录
if (-not (Test-Path "data")) {
    Write-Host "创建data目录..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "data" | Out-Null
}

# 显示当前目录
Write-Host "当前目录: $(Get-Location)" -ForegroundColor Cyan

# 启动服务
Write-Host "启动后端服务..." -ForegroundColor Green
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

