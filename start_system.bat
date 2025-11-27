@echo off
echo Starting Cortex AI Attendance System...

start cmd /k ".\run_backend.bat"
start cmd /k ".\run_frontend.bat"

echo System started!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
pause
