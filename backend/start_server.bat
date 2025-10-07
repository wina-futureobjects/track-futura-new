@echo off
echo Starting TrackFutura Server...
echo.

cd /d "%~dp0"

echo Activating virtual environment...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo No virtual environment found, using global Python
)

echo.
echo Starting Django server on 0.0.0.0:8000...
echo.
echo Access the application at: http://localhost:8000
echo Login with: demo / demo123
echo.
echo Press Ctrl+C to stop the server
echo.

python manage.py runserver 0.0.0.0:8000
