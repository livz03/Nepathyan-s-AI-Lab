@echo off
echo ==========================================
echo   Cortex AI Attendance - Emergency Launch
echo ==========================================

echo [1/4] Killing old processes...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1

echo [2/4] Installing Backend Dependencies...
cd /d "e:\Nepathyan s AI Lab"
pip install fastapi uvicorn pydantic-settings python-socketio openai google-generativeai scikit-learn motor python-dotenv python-multipart python-jose[cryptography] passlib[bcrypt] >nul

echo [3/4] Starting Backend Server...
start "Backend Server" cmd /k "python -m uvicorn backend.main:app --reload --port 8000 --host 0.0.0.0"

echo [4/4] Starting Frontend App...
cd frontend
start "Frontend App" cmd /k "npm run dev"

echo ==========================================
echo   System Launched!
echo   Backend: http://localhost:8000/docs
echo   Frontend: http://localhost:5173
echo ==========================================
pause
