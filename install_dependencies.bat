@echo off
echo Installing Backend Dependencies...
cd backend
pip install -r ../requirements.txt

echo.
echo Attempting to install dlib (required for face_recognition)...
pip install dlib
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Standard dlib installation failed. This is common on Windows.
    echo Please install "Desktop development with C++" from Visual Studio Build Tools.
    echo Alternatively, try installing a pre-built wheel from:
    echo https://github.com/z-mahmoudi/dlib-wheels
    echo.
    echo For now, we will proceed, but face recognition might fail.
    pause
)

echo.
echo Installing Frontend Dependencies...
cd ../frontend
call npm install
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] NPM install failed. Please ensure Node.js is installed and added to PATH.
    echo Download: https://nodejs.org/
    pause
    exit /b
)

echo.
echo All dependencies installed!
pause
