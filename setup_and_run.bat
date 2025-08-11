@echo off
echo ======================================================
echo       CureVerse - AI Health Assistant Setup
echo ======================================================
echo.

REM Check if Python is installed
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH. Please install Python 3.8 or higher.
    pause
    exit /b 1
)
echo [OK] Python is installed.
echo.

REM Check if virtual environment exists, create if not
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created.
) else (
    echo [OK] Virtual environment already exists.
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate
echo [OK] Virtual environment activated.
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
echo [OK] Dependencies installed.
echo.

REM Create necessary directories
echo Setting up project structure...
if not exist static\img (
    mkdir static\img
    echo [OK] Created static/img directory.
) else (
    echo [OK] static/img directory already exists.
)
echo.

REM Run the application
echo ======================================================
echo Starting CureVerse application...
echo.
echo The application will be available at: http://127.0.0.1:5000
echo.
echo Press Ctrl+C to stop the server when you're done.
echo ======================================================
echo.
python app.py

REM Deactivate virtual environment on exit
call venv\Scripts\deactivate
