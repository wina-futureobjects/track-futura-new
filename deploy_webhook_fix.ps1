# Upsun Deployment Script - Correct Commands
# Deploy webhook URL fix to production

Write-Host "Deploying webhook URL fix to Upsun production..." -ForegroundColor Green

# Check if Upsun CLI is installed
if (-not (Get-Command "upsun" -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Upsun CLI not found!" -ForegroundColor Red
    Write-Host "Please install Upsun CLI first." -ForegroundColor White
    exit 1
}

# Check current project info
Write-Host "Checking current project..." -ForegroundColor Yellow
upsun project:info

# Deploy using environment:push
Write-Host "Pushing changes to production environment..." -ForegroundColor Yellow
upsun environment:push --yes

if ($LASTEXITCODE -eq 0) {
    Write-Host "Deployment successful!" -ForegroundColor Green
    Write-Host "Webhook URL fix is now live on production." -ForegroundColor Green
    Write-Host "Production URL: https://trackfutura.futureobjects.io/" -ForegroundColor Cyan
} else {
    Write-Host "Deployment failed!" -ForegroundColor Red
    exit 1
}