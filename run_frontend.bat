@echo off
echo Starting Cortex AI Frontend...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo NPM install failed. Please ensure Node.js is installed.
    pause
    exit /b
)
call npm run dev
pause
