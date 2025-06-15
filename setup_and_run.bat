@echo off
REM PipeGuard Setup and Run Script for Windows
REM This script sets up the environment and runs the PipeGuard application

echo ===========================================
echo          PipeGuard Setup Script
echo ===========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.9+ and try again
    pause
    exit /b 1
)

echo Python found, installing dependencies...

REM Install dependencies
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo Dependencies installed successfully!

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo Please edit .env file with your actual credentials before running the app
)

echo ===========================================
echo Choose an option:
echo 1. Run Flask app locally (with mock data)
echo 2. Test monitor pipeline function
echo 3. Run pytest tests
echo 4. Exit
echo ===========================================

set /p choice=Enter your choice (1-4): 

if "%choice%"=="1" (
    echo Starting Flask app locally...
    python run_local.py
) else if "%choice%"=="2" (
    echo Testing monitor pipeline...
    python test_monitor.py
) else if "%choice%"=="3" (
    echo Running tests...
    python -m pytest test_app.py -v
) else if "%choice%"=="4" (
    echo Goodbye!
    exit /b 0
) else (
    echo Invalid choice. Please try again.
    pause
    goto :eof
)

pause
