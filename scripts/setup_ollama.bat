@echo off
echo ========================================
echo   AI Educational System - Ollama Setup
echo ========================================
echo.

REM Check if Ollama is installed
where ollama >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Ollama is not installed!
    echo.
    echo Please download and install Ollama from:
    echo https://ollama.com/download
    echo.
    echo After installation, run this script again.
    pause
    exit /b 1
)

echo [✓] Ollama is installed
echo.

echo ========================================
echo   Pulling Qwen 2.5 14B Model
echo ========================================
echo This may take 10-20 minutes depending on your internet speed...
echo Model size: ~8GB
echo.

ollama pull qwen2.5:14b

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to pull model!
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Testing Ollama
echo ========================================
echo.

ollama run qwen2.5:14b "Hello, respond with 'Working!' if you can see this."

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Model test failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   ✅ SUCCESS! Ollama is ready!
echo ========================================
echo.
echo Model: Qwen 2.5 14B
echo Status: Running
echo API: http://localhost:11434
echo.
echo You can now proceed to run the application.
echo.
pause
