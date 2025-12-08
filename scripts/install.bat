@echo off
REM AI Chat Agent Installation Script for Windows
REM This script sets up the complete environment for the application

setlocal enabledelayedexpansion

echo.
echo ========================================
echo AI Chat Agent Installation
echo ========================================
echo.

REM Step 1: Check Python version
echo [INFO] Checking Python version...
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo [ERROR] Please install Python 3.9 or higher from https://www.python.org/
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] Found Python %PYTHON_VERSION%

REM Check if Python version is 3.9 or higher
python -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python 3.9 or higher is required. Current version: %PYTHON_VERSION%
    pause
    exit /b 1
)

echo [SUCCESS] Python version check passed
echo.

REM Step 2: Create virtual environment
echo [INFO] Creating virtual environment...
if exist venv (
    echo [WARNING] Virtual environment already exists. Removing old environment...
    rmdir /s /q venv
)

python -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment created
echo.

REM Step 3: Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment activated
echo.

REM Step 4: Upgrade pip
echo [INFO] Upgrading pip to latest version...
python -m pip install --upgrade pip
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Failed to upgrade pip, continuing with current version...
) else (
    for /f "tokens=2" %%i in ('pip --version') do set PIP_VERSION=%%i
    echo [SUCCESS] pip upgraded to version !PIP_VERSION!
)
echo.

REM Step 5: Install dependencies
echo [INFO] Installing Python dependencies...
echo [INFO] This may take a few minutes...
echo.

REM Install GUI Framework
echo [INFO] Installing PyQt6 ^(GUI Framework^)...
pip install "PyQt6>=6.5.0"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install PyQt6
    pause
    exit /b 1
)
echo [SUCCESS] PyQt6 installed
echo.

REM Install LangChain Core
echo [INFO] Installing LangChain core libraries...
pip install "langchain>=0.1.0"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install langchain
    pause
    exit /b 1
)
echo [SUCCESS] LangChain installed
echo.

echo [INFO] Installing LangChain OpenAI integration...
pip install "langchain-openai>=0.0.5"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install langchain-openai
    pause
    exit /b 1
)
echo [SUCCESS] LangChain OpenAI installed
echo.

REM Install Configuration and Data libraries
echo [INFO] Installing PyYAML ^(configuration management^)...
pip install "PyYAML>=6.0"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install PyYAML
    pause
    exit /b 1
)
echo [SUCCESS] PyYAML installed
echo.

echo [INFO] Installing requests ^(HTTP library^)...
pip install "requests>=2.31.0"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install requests
    pause
    exit /b 1
)
echo [SUCCESS] requests installed
echo.

REM Install Development Tools
echo [INFO] Installing pytest ^(testing framework^)...
pip install "pytest>=7.4.0"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install pytest
    pause
    exit /b 1
)
echo [SUCCESS] pytest installed
echo.

echo [SUCCESS] All dependencies installed successfully
echo.

REM Step 6: Create application directory structure
echo [INFO] Creating application directory structure...

if not exist sessions mkdir sessions
if not exist logs mkdir logs
if not exist docs mkdir docs

echo [SUCCESS] Directory structure created:
echo [INFO]   - sessions\ (for storing conversation sessions)
echo [INFO]   - logs\ (for application logs)
echo [INFO]   - docs\ (for documentation)
echo.

REM Step 7: Generate default configuration file
echo [INFO] Generating default configuration file...

if exist config.yaml (
    echo [WARNING] config.yaml already exists. Creating backup...
    copy config.yaml config.yaml.backup >nul
    echo [INFO] Backup saved as config.yaml.backup
)

(
echo # AI Chat Agent Configuration File
echo.
echo # Active Model Configuration
echo active_model_id: null  # Will be set when user adds first model
echo.
echo # Model Configurations ^(OpenAPI compatible models^)
echo models: {}
echo.
echo # LangChain Configuration
echo langchain:
echo   temperature: 0.7
echo   max_tokens: 2048
echo   streaming: true
echo   verbose: false
echo.
echo # Working Directory
echo working_directory: "."
echo.
echo # Session Configuration
echo session:
echo   storage_path: "./sessions"
echo   auto_save: true
echo   max_history: 100
echo.
echo # File Operation Configuration
echo file_operations:
echo   allowed_formats:
echo     - .txt
echo     - .md
echo     - .py
echo     - .js
echo     - .json
echo     - .yaml
echo     - .yml
echo     - .xml
echo     - .html
echo     - .css
echo     - .sh
echo     - .bat
echo   max_file_size: 10485760  # 10MB in bytes
echo.
echo # Logging Configuration
echo logging:
echo   level: "INFO"
echo   file: "./logs/agent.log"
echo   max_bytes: 10485760  # 10MB
echo   backup_count: 5
echo.
echo # UI Configuration
echo ui:
echo   theme: "light"
echo   window_width: 1200
echo   window_height: 800
) > config.yaml

echo [SUCCESS] Default configuration file created
echo.

REM Step 8: Verify installation
echo.
echo ========================================
echo Verifying Installation
echo ========================================
echo.

echo [INFO] Checking installed packages...
set VERIFICATION_FAILED=0

REM Check critical dependencies
echo [INFO] Checking PyQt6...
python -c "import PyQt6" 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] * PyQt6 installed
) else (
    echo [ERROR] * PyQt6 not found
    set VERIFICATION_FAILED=1
)

echo [INFO] Checking langchain...
python -c "import langchain" 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] * langchain installed
) else (
    echo [ERROR] * langchain not found
    set VERIFICATION_FAILED=1
)

echo [INFO] Checking langchain-openai...
python -c "import langchain_openai" 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] * langchain-openai installed
) else (
    echo [ERROR] * langchain-openai not found
    set VERIFICATION_FAILED=1
)

echo [INFO] Checking yaml...
python -c "import yaml" 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] * yaml installed
) else (
    echo [ERROR] * yaml not found
    set VERIFICATION_FAILED=1
)

echo [INFO] Checking requests...
python -c "import requests" 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] * requests installed
) else (
    echo [ERROR] * requests not found
    set VERIFICATION_FAILED=1
)

echo.
echo [INFO] Checking directories...
if exist sessions (
    echo [SUCCESS] * sessions\ exists
) else (
    echo [ERROR] * sessions\ not found
    set VERIFICATION_FAILED=1
)

if exist logs (
    echo [SUCCESS] * logs\ exists
) else (
    echo [ERROR] * logs\ not found
    set VERIFICATION_FAILED=1
)

if exist docs (
    echo [SUCCESS] * docs\ exists
) else (
    echo [ERROR] * docs\ not found
    set VERIFICATION_FAILED=1
)

if exist src (
    echo [SUCCESS] * src\ exists
) else (
    echo [ERROR] * src\ not found
    set VERIFICATION_FAILED=1
)

echo.
echo [INFO] Checking configuration file...
if exist config.yaml (
    echo [SUCCESS] * config.yaml exists
) else (
    echo [ERROR] * config.yaml not found
    set VERIFICATION_FAILED=1
)

echo [INFO] Checking main application file...
if exist main.py (
    echo [SUCCESS] * main.py exists
) else (
    echo [ERROR] * main.py not found
    set VERIFICATION_FAILED=1
)

echo.

if !VERIFICATION_FAILED! EQU 0 (
    echo ========================================
    echo Installation Successful!
    echo ========================================
    echo.
    echo The AI Chat Agent has been successfully installed!
    echo.
    echo Next Steps:
    echo   1. Activate the virtual environment:
    echo      venv\Scripts\activate.bat
    echo.
    echo   2. Run the application:
    echo      python main.py
    echo.
    echo   3. On first launch, you'll be guided to add your first AI model configuration
    echo      ^(OpenAI, Azure OpenAI, or any OpenAPI-compatible service^)
    echo.
    echo Quick Start:
    echo   - Use the provided run script:
    echo     scripts\run.bat
    echo.
    echo Documentation:
    echo   - User Guide: docs\USER_GUIDE.md
    echo   - Developer Guide: docs\DEVELOPER_GUIDE.md
    echo   - API Documentation: docs\API.md
    echo.
    echo Happy chatting! 🚀
    echo.
) else (
    echo ========================================
    echo Installation Completed with Warnings
    echo ========================================
    echo.
    echo [WARNING] Some verification checks failed. Please review the errors above.
    echo [INFO] You may need to manually fix these issues before running the application.
    echo.
    pause
    exit /b 1
)

pause
