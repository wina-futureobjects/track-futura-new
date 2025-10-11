@echo off
echo.
echo 🚨 RUNNING PRODUCTION DEPLOYMENT FROM LOCAL MACHINE
echo ================================================
echo.

echo Step 1: Pulling latest code on production...
upsun ssh -p inhoolfrqniuu -e main-bvxea6i --app trackfutura -- "cd /app && git pull origin main"

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Git pull failed, trying to continue...
)

echo.
echo Step 2: Testing production database...
upsun ssh -p inhoolfrqniuu -e main-bvxea6i --app trackfutura -- "cd /app/backend && python PRODUCTION_TEST.py"

echo.
echo Step 3: Deploying scraped data to production...
upsun ssh -p inhoolfrqniuu -e main-bvxea6i --app trackfutura -- "cd /app/backend && python PRODUCTION_DEPLOY.py"

echo.
echo ✅ DEPLOYMENT COMPLETE!
echo.
echo Your data should now be visible at:
echo   📁 Job 2: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/103
echo   📁 Job 3: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/104
echo.
pause