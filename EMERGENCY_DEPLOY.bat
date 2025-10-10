@echo off
echo.
echo 🚨 EMERGENCY DEPLOYMENT - MANUAL INSTRUCTIONS
echo ==========================================
echo.
echo STEP 1: Go to Upsun Dashboard
echo https://console.upsun.com/projects/inhoolfrqniuu
echo.
echo STEP 2: Click on "trackfutura" app
echo.
echo STEP 3: Click "Terminal" or "SSH" button
echo.
echo STEP 4: Run these commands ONE BY ONE:
echo.
echo cd /app
echo git pull origin main
echo cd backend
echo python urgent_fix.py
echo.
echo ✅ After running these commands, your data will be live at:
echo.
echo 📁 Job 2 (103): https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/103
echo 📁 Job 3 (104): https://main-bvxea6i-inhoolfrqniuu.eu-5.platformsh.site/organizations/1/projects/1/data-storage/job/104
echo.
echo 🎉 ALL DONE! Your workflow management will show "completed" status!
echo.
pause