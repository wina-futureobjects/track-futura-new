#!/usr/bin/env pwsh
# EMERGENCY DEPLOYMENT SCRIPT FOR PRODUCTION
# ==========================================
# This script will deploy the fix to your Upsun production server

Write-Host "🚨 EMERGENCY DEPLOYMENT STARTING..." -ForegroundColor Red
Write-Host "=" * 50

# Check if upsun CLI is available
if (Get-Command upsun -ErrorAction SilentlyContinue) {
    Write-Host "✅ Upsun CLI found" -ForegroundColor Green
    
    # Try to connect and run the fix
    try {
        Write-Host "🚀 Deploying fix to production..." -ForegroundColor Yellow
        
        # Method 1: Execute commands directly
        $commands = @(
            "cd /app",
            "git pull origin main",
            "cd backend", 
            "python urgent_fix.py"
        )
        
        foreach ($cmd in $commands) {
            Write-Host "📋 Executing: $cmd" -ForegroundColor Cyan
            upsun ssh -p inhoolfrqniuu -e main-bvxea6i --app trackfutura -- $cmd
            
            if ($LASTEXITCODE -ne 0) {
                Write-Host "❌ Command failed: $cmd" -ForegroundColor Red
            } else {
                Write-Host "✅ Command succeeded: $cmd" -ForegroundColor Green
            }
        }
        
        Write-Host "🎉 DEPLOYMENT COMPLETE!" -ForegroundColor Green
        
    } catch {
        Write-Host "❌ Deployment failed: $_" -ForegroundColor Red
        Write-Host "🔄 Trying alternative method..." -ForegroundColor Yellow
        
        # Method 2: Single command execution
        $fullCommand = "cd /app && git pull origin main && cd backend && python urgent_fix.py"
        Write-Host "📋 Executing full command..." -ForegroundColor Cyan
        upsun ssh -p inhoolfrqniuu -e main-bvxea6i --app trackfutura -- $fullCommand
    }
    
} else {
    Write-Host "❌ Upsun CLI not found!" -ForegroundColor Red
    Write-Host "📥 Installing Upsun CLI..." -ForegroundColor Yellow
    
    # Try to install upsun CLI
    try {
        if (Get-Command winget -ErrorAction SilentlyContinue) {
            winget install upsun.cli
        } elseif (Get-Command curl -ErrorAction SilentlyContinue) {
            curl -fsSL https://upsun.com/cli/install.sh | sh
        } else {
            Write-Host "❌ Cannot install Upsun CLI automatically" -ForegroundColor Red
            Write-Host "📝 Please install manually from: https://upsun.com/cli/" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "❌ CLI installation failed: $_" -ForegroundColor Red
    }
}

Write-Host "`n🚨 IF DEPLOYMENT FAILED, USE THESE MANUAL STEPS:" -ForegroundColor Yellow
Write-Host "=" * 50
Write-Host "1. Go to your Upsun dashboard: https://console.upsun.com/projects/inhoolfrqniuu" -ForegroundColor White
Write-Host "2. Open terminal for app 'trackfutura'" -ForegroundColor White
Write-Host "3. Run these commands one by one:" -ForegroundColor White
Write-Host "   cd /app" -ForegroundColor Cyan
Write-Host "   git pull origin main" -ForegroundColor Cyan
Write-Host "   cd backend" -ForegroundColor Cyan
Write-Host "   python urgent_fix.py" -ForegroundColor Cyan
Write-Host "`n✅ Your data will be live at:" -ForegroundColor Green
Write-Host "   📁 Job 2: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/103" -ForegroundColor White  
Write-Host "   📁 Job 3: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/104" -ForegroundColor White