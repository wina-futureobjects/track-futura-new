# Upsun Deployment Script - Fixed Version
# Deploy webhook URL fix to production

Write-Host "Deploying webhook URL fix to Upsun production..." -ForegroundColor Green

# Check if Upsun CLI is installed
if (-not (Get-Command "upsun" -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Upsun CLI not found!" -ForegroundColor Red
    Write-Host "Please install Upsun CLI first." -ForegroundColor White
    exit 1
}

# Set project context
$projectId = "inhoolfrqniuu"
Write-Host "Setting project context to $projectId..." -ForegroundColor Yellow
upsun project:set-default $projectId

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to set project context!" -ForegroundColor Red
    exit 1
}

# Deploy
Write-Host "Pushing changes to production..." -ForegroundColor Yellow
upsun push --yes

if ($LASTEXITCODE -eq 0) {
    Write-Host "Deployment successful!" -ForegroundColor Green
    Write-Host "Webhook URL fix is now live on production." -ForegroundColor Green
} else {
    Write-Host "Deployment failed!" -ForegroundColor Red
    exit 1
}