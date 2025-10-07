@echo off
REM Start the Apify polling service
echo Starting Apify polling service...
echo This will continuously check for completed Apify runs every 30 seconds.
echo Press Ctrl+C to stop.
echo.

cd /d %~dp0
.\venv\Scripts\python.exe manage.py poll_apify_runs --continuous --interval 30
