@echo off
echo ============================================================
echo Emotion-Aware Authentication - Setup and Training
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)

echo Step 1: Installing dependencies...
echo ============================================================
python -m pip install -r backend\requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

echo Step 2: Downloading sample datasets...
echo ============================================================
python -m backend.download_datasets --samples
echo.

echo Step 3: Training models...
echo ============================================================
python -m backend.train_models --all
echo.

echo Step 4: Evaluating models...
echo ============================================================
python -m backend.evaluate_models --all
echo.

echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo To start the server, run:
echo   python -m uvicorn backend.main:app --reload
echo.
echo Or simply run: start_server.bat
echo.
pause
