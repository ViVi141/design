# 启动前端服务脚本

# 确保在frontend目录
Set-Location -Path "$PSScriptRoot\frontend"

# 检查.env.development文件
if (-not (Test-Path ".env.development")) {
    Write-Host "错误: 未找到.env.development配置文件!" -ForegroundColor Red
    Write-Host "请先配置 frontend\.env.development 文件" -ForegroundColor Yellow
    exit 1
}

# 检查node_modules
if (-not (Test-Path "node_modules")) {
    Write-Host "安装依赖..." -ForegroundColor Yellow
    pnpm install
}

# 显示当前目录
Write-Host "当前目录: $(Get-Location)" -ForegroundColor Cyan

# 启动服务
Write-Host "启动前端服务..." -ForegroundColor Green
pnpm dev

