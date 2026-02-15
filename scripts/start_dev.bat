@echo off
echo ========================================
echo   Starting AI Educational System
echo ========================================
echo.

REM Check if .env file exists
if not exist ".env" (
    echo [WARNING] .env file not found!
    echo Creating .env from .env.example...
    copy .env.example .env
    echo.
    echo [INFO] Please edit .env file with your settings before continuing.
    echo Press any key to continue or Ctrl+C to exit and edit .env first...
    pause
)

echo Starting Backend Server...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start backend in a new window
start "AI Edu System - Backend" cmd /k "cd /d %CD% && venv\Scripts\activate.bat && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo [✓] Backend server starting at http://localhost:8000
echo.

REM Wait a bit for backend to start
timeout /t 3 /nobreak >nul

echo Starting Frontend Server...
echo.

REM Check if node_modules exists in frontend
if not exist "frontend\node_modules" (
    echo [INFO] Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
)

REM Start frontend in a new window
start "AI Edu System - Frontend" cmd /k "cd /d %CD%\frontend && npm run dev"

echo [✓] Frontend server starting at http://localhost:5173
echo.
echo ========================================
echo   ✅ Both servers are starting!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C in each window to stop the servers.
echo.
pause
