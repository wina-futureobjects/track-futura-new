#!/usr/bin/env powershell

# Upsun Deployment Script for TrackFutura
# Windows PowerShell version
# Project: inhoolfrqniuu

Write-Host "🚀 TrackFutura Upsun Deployment Script" -ForegroundColor Green
Write-Host "Project: inhoolfrqniuu" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Gray

# Check if Upsun CLI is installed
Write-Host "🔧 Checking Upsun CLI..." -ForegroundColor Yellow
if (-not (Get-Command "upsun" -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Upsun CLI not found!" -ForegroundColor Red
    Write-Host "Please install Upsun CLI first:" -ForegroundColor White
    Write-Host "  curl -f https://cli.upsun.com/installer | sh" -ForegroundColor Gray
    Write-Host "  Or visit: https://docs.upsun.com/dev-tools/cli/install" -ForegroundColor Gray
    exit 1
}
Write-Host "✅ Upsun CLI found" -ForegroundColor Green

# Check if logged in
Write-Host "🔐 Checking Upsun authentication..." -ForegroundColor Yellow
$authCheck = upsun auth:info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Not authenticated with Upsun!" -ForegroundColor Red
    Write-Host "Please log in first:" -ForegroundColor White
    Write-Host "  upsun auth:login" -ForegroundColor Gray
    exit 1
}
Write-Host "✅ Authenticated with Upsun" -ForegroundColor Green

# Set project context
Write-Host "📋 Setting project context..." -ForegroundColor Yellow
$projectId = "inhoolfrqniuu"
upsun project:set-default $projectId
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to set project context!" -ForegroundColor Red
    Write-Host "Available projects:" -ForegroundColor White
    upsun projects
    exit 1
}
Write-Host "✅ Project context set to $projectId" -ForegroundColor Green

# Show current project info
Write-Host "📊 Project Information:" -ForegroundColor Yellow
upsun project:info

# Deploy the application
Write-Host "🚀 Starting deployment..." -ForegroundColor Yellow
Write-Host "This will deploy your current Git state to Upsun..." -ForegroundColor White

$confirm = Read-Host "Continue with deployment? (y/N)"
if ($confirm -ne 'y' -and $confirm -ne 'Y') {
    Write-Host "❌ Deployment cancelled" -ForegroundColor Red
    exit 0
}

# Push to Upsun
Write-Host "📤 Pushing to Upsun..." -ForegroundColor Yellow
upsun push --yes
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Deployment completed!" -ForegroundColor Green
Write-Host "" -ForegroundColor White

# Show deployment URL
Write-Host "🌐 Your application should be available at:" -ForegroundColor Green
Write-Host "  https://main-bvxea6i-inhoolfrqniuu.upsun.app" -ForegroundColor Cyan
Write-Host "" -ForegroundColor White

# Environment variables reminder
Write-Host "⚠️  IMPORTANT: Set environment variables in Upsun console:" -ForegroundColor Yellow
Write-Host "1. Go to: https://console.upsun.com/projects/inhoolfrqniuu" -ForegroundColor White
Write-Host "2. Navigate to Environment > Variables" -ForegroundColor White
Write-Host "3. Add these required variables:" -ForegroundColor White
Write-Host "   - APIFY_API_TOKEN (your Apify API token)" -ForegroundColor Gray
Write-Host "   - OPENAI_API_KEY (your OpenAI API key)" -ForegroundColor Gray
Write-Host "" -ForegroundColor White

Write-Host "🎉 Deployment complete! Monitor your app in the Upsun console." -ForegroundColor Green