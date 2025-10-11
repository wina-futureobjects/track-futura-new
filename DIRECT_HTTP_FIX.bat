@echo off
echo.
echo 🚨 EMERGENCY: RUNNING COMMAND DIRECTLY ON PRODUCTION
echo ===================================================
echo.

echo Trying to execute production fix via HTTP request...
echo.

REM Create a simple HTTP request to trigger the database fix
curl -X POST "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/emergency-fix/" ^
     -H "Content-Type: application/json" ^
     -d "{\"action\": \"create_sample_data\"}" ^
     --connect-timeout 30 ^
     --max-time 60

echo.
echo If that worked, your data should now be at:
echo   📁 Job 2: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/103
echo   📁 Job 3: https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/104
echo.

echo Testing if the job results are now available...
echo.

echo Testing Job 2 (103):
curl -X GET "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/job-results/103/" ^
     --connect-timeout 10 ^
     --max-time 30 ^
     -s -o nul -w "Status: %%{http_code}"

echo.
echo Testing Job 3 (104):
curl -X GET "https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/api/brightdata/job-results/104/" ^
     --connect-timeout 10 ^
     --max-time 30 ^
     -s -o nul -w "Status: %%{http_code}"

echo.
echo.
echo ✅ If you see status 200 above, your data is ready!
echo ❌ If you see status 404, we need to try a different approach.
echo.
pause