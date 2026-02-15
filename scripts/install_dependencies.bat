@echo off
echo ========================================
echo   Installing Python Dependencies
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ from python.org
    pause
    exit /b 1
)

echo [✓] Python is installed
python --version
echo.

REM Check if pip is available
pip --version >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] pip is not installed!
    pause
    exit /b 1
)

echo [✓] pip is available
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Create virtual environment
echo ========================================
echo   Creating Virtual Environment
echo ========================================
echo.

if exist "venv" (
    echo [INFO] Virtual environment already exists. Skipping creation.
) else (
    echo Creating virtual environment...
    python -m venv venv
    echo [✓] Virtual environment created
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install requirements
echo ========================================
echo   Installing Requirements
echo ========================================
echo This may take 5-10 minutes...
echo.

pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to install requirements!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Installing PyTorch with CUDA Support
echo ========================================
echo.

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

if %errorlevel% neq 0 (
    echo [WARNING] Failed to install PyTorch with CUDA. Installing CPU version...
    pip install torch torchvision torchaudio
)

echo.
echo ========================================
echo   ✅ Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Copy .env.example to .env
echo 2. Run setup_ollama.bat to install the LLM
echo 3. Run start_dev.bat to start the application
echo.
pause
