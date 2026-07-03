@echo off
REM StockFlow Launcher for Windows
REM This script sets up and runs the inventory management system

setlocal enabledelayedexpansion

echo.
echo ========================================
echo   STOCKFLOW - Inventory Management
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.11+ from https://www.python.org
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

REM Run migrations
echo Setting up database...
python manage.py migrate --noinput
if errorlevel 1 (
    echo ERROR: Failed to apply migrations.
    pause
    exit /b 1
)

REM Check if an administrator account exists, if not prompt to create one
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); import sys; sys.exit(0 if User.objects.filter(is_superuser=True).exists() or User.objects.filter(role='ADMIN').exists() else 1)" 2>nul
if errorlevel 1 (
    echo.
    echo No administrator account found. Create one now:
    echo.
    python manage.py createsuperuser
)

REM Start the server
echo.
echo ========================================
echo Starting server at http://127.0.0.1:8000
echo Admin panel at http://127.0.0.1:8000/admin
echo Press CTRL+C to stop the server
echo ========================================
echo.

REM Open browser
timeout /t 2 /nobreak >nul
start http://127.0.0.1:8000

REM Run the development server
python manage.py runserver
