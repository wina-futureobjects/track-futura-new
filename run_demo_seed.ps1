#!/usr/bin/env pwsh
# Demo Data Seeding Script for Track Futura
# This script sets up demo data for easy deployment demos

Write-Host "🌱 Track Futura Demo Data Seeding" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "backend\manage.py")) {
    Write-Host "❌ Error: manage.py not found in backend directory" -ForegroundColor Red
    Write-Host "Please run this script from the root directory of your project" -ForegroundColor Yellow
    exit 1
}

# Change to backend directory
Set-Location backend

Write-Host "📂 Changed to backend directory" -ForegroundColor Blue

# Check if virtual environment exists and activate it
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "🐍 Activating virtual environment..." -ForegroundColor Blue
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "⚠️  Virtual environment not found. Using system Python..." -ForegroundColor Yellow
}

# Run migrations first
Write-Host "🔄 Running migrations..." -ForegroundColor Blue
try {
    python manage.py makemigrations --check 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "📝 Creating new migrations..." -ForegroundColor Yellow
        python manage.py makemigrations
    }
    
    python manage.py migrate
    Write-Host "✅ Migrations completed" -ForegroundColor Green
} catch {
    Write-Host "❌ Migration failed: $_" -ForegroundColor Red
    exit 1
}

# Run the seeding
Write-Host "🌱 Seeding demo data..." -ForegroundColor Blue
try {
    python seed_demo_data.py --reset
    Write-Host "✅ Demo data seeding completed!" -ForegroundColor Green
} catch {
    Write-Host "❌ Seeding failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n🎉 Setup Complete!" -ForegroundColor Green
Write-Host "================" -ForegroundColor Green
Write-Host "Your demo environment is ready!" -ForegroundColor White
Write-Host "`n👤 Admin Accounts:" -ForegroundColor Cyan
Write-Host "  • superadmin / admin123!" -ForegroundColor White
Write-Host "  • tenantadmin / admin123!" -ForegroundColor White
Write-Host "`n👥 Regular Users:" -ForegroundColor Cyan
Write-Host "  • Use any demo user with password: demo123!" -ForegroundColor White
Write-Host "`n🚀 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Start your server: python manage.py runserver 8001" -ForegroundColor White
Write-Host "  2. Open your frontend application" -ForegroundColor White
Write-Host "  3. Login with any of the demo accounts" -ForegroundColor White
Write-Host "  4. Explore the organizations and projects!" -ForegroundColor White

# Go back to root directory
Set-Location ..
Write-Host "`n📂 Returned to root directory" -ForegroundColor Blue 