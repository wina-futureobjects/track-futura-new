#!/usr/bin/env powershell

# Manual Upsun Deployment - Authentication Fixed
Write-Host "🚀 Manual Upsun Deployment" -ForegroundColor Green

# Check if API token is set
if (-not $env:UPSUN_CLI_TOKEN) {
    Write-Host "❌ UPSUN_CLI_TOKEN not set!" -ForegroundColor Red
    Write-Host "Please set your API token:" -ForegroundColor Yellow
    Write-Host '  $env:UPSUN_CLI_TOKEN="your-token-here"' -ForegroundColor Gray
    Write-Host "Get token from: https://console.upsun.com/user/api-tokens" -ForegroundColor Cyan
    exit 1
}

# Set project context
Write-Host "📋 Setting project context..." -ForegroundColor Yellow
upsun project:set-remote inhoolfrqniuu
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to set project context!" -ForegroundColor Red
    exit 1
}

# Deploy
Write-Host "🚀 Deploying to Upsun..." -ForegroundColor Yellow
upsun push
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Deployment successful!" -ForegroundColor Green
Write-Host "🌐 App URL: https://main-bvxea6i-inhoolfrqniuu.upsun.app" -ForegroundColor Cyan