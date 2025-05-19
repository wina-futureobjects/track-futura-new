#!/usr/bin/env pwsh
# Script to start both frontend and backend servers

Write-Host "Starting Track Futura servers..." -ForegroundColor Cyan

# Start the backend server in a new window with venv activated
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; .\\venv\\Scripts\\activate; python manage.py runserver"

# Start the frontend server in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm run dev"

Write-Host "Servers started in separate windows!" -ForegroundColor Green
Write-Host "Backend: http://localhost:8000" -ForegroundColor Yellow
Write-Host "Frontend: Check the Vite output for the correct URL (typically http://localhost:5173)" -ForegroundColor Yellow 