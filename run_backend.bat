@echo off
echo Starting Cortex AI Backend...
cd backend
echo Ensure you have activated your virtual environment if you have one.
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause
