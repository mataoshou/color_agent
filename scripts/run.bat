@echo off
REM AI Chat Agent Run Script for Windows
REM This script activates the virtual environment and starts the application

setlocal enabledelayedexpansion

echo.
echo ========================================
echo AI Chat Agent
echo ========================================
echo.

REM Step 1: Check if virtual environment exists
echo [INFO] Checking virtual environment...
if not exist venv (
    echo [ERROR] Virtual environment not found!
    echo [INFO] Please run the installation script first:
    echo   scripts\install.bat
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment found
echo.

REM Step 2: Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment activated
echo.

REM Step 3: Check if main.py exists
echo [INFO] Checking application files...
if not exist main.py (
    echo [ERROR] main.py not found!
    echo [INFO] Please ensure you are in the correct directory
    pause
    exit /b 1
)
echo [SUCCESS] Application files found
echo.

REM Step 4: Check configuration file
echo [INFO] Checking configuration file...
if not exist config.yaml (
    echo [WARNING] config.yaml not found!
    echo [INFO] A default configuration will be created on first run
) else (
    echo [SUCCESS] Configuration file found
)
echo.

REM Step 5: Check required directories
echo [INFO] Checking required directories...
if not exist sessions mkdir sessions
if not exist logs mkdir logs
echo [SUCCESS] Required directories ready
echo.

REM Step 6: Start the application
echo.
echo ========================================
echo Starting Application
echo ========================================
echo.
echo [INFO] Launching AI Chat Agent...
echo.

REM Run the application
python main.py

REM Capture exit code
set EXIT_CODE=%ERRORLEVEL%

echo.
if !EXIT_CODE! EQU 0 (
    echo [SUCCESS] Application closed successfully
) else (
    echo [WARNING] Application exited with code !EXIT_CODE!
)

REM Deactivate virtual environment
call venv\Scripts\deactivate.bat 2>nul

pause
exit /b !EXIT_CODE!
