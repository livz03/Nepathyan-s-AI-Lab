@echo off
echo Starting Cortex AI Attendance System...

start "Backend Server" cmd /k "cd /d e:\Nepathyan s AI Lab && python -m uvicorn backend.main:app --reload --port 8000"
start "Frontend App" cmd /k "cd /d e:\Nepathyan s AI Lab\frontend && npm run dev"

echo System started!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
pause
