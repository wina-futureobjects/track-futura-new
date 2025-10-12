@echo off
REM BRIGHTDATA STORAGE COMPLETE FIX DEPLOYMENT
REM This deploys both backend and frontend fixes

echo ========================================
echo BrightData Storage Fix Deployment
echo ========================================
echo.
echo This will deploy:
echo   1. Backend: Create folder before scraping
echo   2. Frontend: Add /data-storage/run/:runId route
echo.
echo Files to be deployed:
echo   - backend/workflow/views.py
echo   - frontend/src/App.tsx
echo.

pause

echo.
echo Checking for changes...
git status

echo.
echo Staging changes...
git add backend/workflow/views.py frontend/src/App.tsx COMPLETE_FIX_DEPLOYMENT.md BRIGHTDATA_STORAGE_FIX_COMPLETE.md

echo.
echo Committing changes...
git commit -m "FIX: Complete BrightData data storage integration" -m "Backend:" -m "- Create UnifiedRunFolder before triggering scrape" -m "- Create BrightDataScraperRequest with folder_id" -m "- Link webhook results to folder via folder_id" -m "- Add cleanup on scraping errors" -m "- Return folder_id and data_storage_url in response" -m "" -m "Frontend:" -m "- Add /data-storage/run/:runId route" -m "- Fix 'No folder identifier provided' error" -m "- Enable direct access to scraped data by run ID" -m "" -m "This ensures scraped data from BrightData appears in Data Storage page."

echo.
echo Pushing to production...
git push upsun main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo DEPLOYMENT SUCCESSFUL!
    echo ========================================
    echo.
    echo Next Steps:
    echo 1. Wait 1-2 minutes for deployment
    echo 2. Test workflow: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/workflow-management
    echo 3. Start a scrape and note folder_id
    echo 4. Wait 2-5 minutes for BrightData webhook
    echo 5. Check Data Storage: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage
    echo 6. Or direct URL: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/run/[folder_id]
    echo.
) else (
    echo.
    echo ========================================
    echo DEPLOYMENT FAILED!
    echo ========================================
    echo.
    echo Please check your git configuration and Upsun remote.
    echo.
)

pause
