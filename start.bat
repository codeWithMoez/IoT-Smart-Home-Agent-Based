@echo off
REM ============================================================================
REM IoT Smart Home Agent-Based System - Universal Setup & Run Script (Windows)
REM ============================================================================

setlocal enabledelayedexpansion

REM Check command
if "%1"=="" goto usage
if "%1"=="setup" goto setup
if "%1"=="run" goto run
if "%1"=="stop" goto stop
goto usage

REM ============================================================================
REM SETUP
REM ============================================================================
:setup
echo.
echo ============================================
echo  IoT Smart Home Setup
echo ============================================
echo.

echo [*] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed. Please install Python 3.11+ first.
    exit /b 1
)
python --version
echo [OK] Python found

echo [*] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed. Please install Node.js 18+ first.
    exit /b 1
)
node --version
echo [OK] Node.js found

echo [*] Checking npm...
npm --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] npm is not installed. Please install npm first.
    exit /b 1
)
npm --version
echo [OK] npm found

REM Check for .env file
if not exist ".env" (
    echo [WARNING] .env file not found. Creating from template...
    if exist ".env.example" (
        copy .env.example .env
        echo [WARNING] Please edit .env and add your OpenAI API key!
        echo OPENAI_API_KEY=sk-your-key-here
    ) else (
        echo [ERROR] .env.example not found!
        exit /b 1
    )
)

echo.
echo ============================================
echo  Installing Backend Dependencies
echo ============================================
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [*] Creating Python virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
)

REM Activate virtual environment and install dependencies
echo [*] Installing Python packages...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt >nul 2>&1
echo [OK] Backend dependencies installed

echo.
echo ============================================
echo  Installing Mobile Dependencies
echo ============================================
echo.

cd mobile
echo [*] Installing npm packages...
call npm install --legacy-peer-deps >nul 2>&1
echo [OK] Mobile dependencies installed
cd ..

echo.
echo [OK] Setup complete!
echo.
goto end

REM ============================================================================
REM RUN
REM ============================================================================
:run
echo.
echo ============================================
echo  Starting IoT Smart Home System
echo ============================================
echo.

echo [*] Cleaning up existing processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo.
echo ============================================
echo  Starting Backend Server
echo ============================================
echo.

echo [*] Starting backend (http://localhost:8000)...
call venv\Scripts\activate.bat
start /B python -m backend.main > backend.log 2>&1

echo [*] Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

REM Check if backend is running
curl -s http://localhost:8000/api/v1/health >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Backend failed to start. Check backend.log
    exit /b 1
)

echo [OK] Backend is responding!
echo [*] API: http://localhost:8000
echo [*] Docs: http://localhost:8000/docs

echo.
echo ============================================
echo  Starting Mobile App
echo ============================================
echo.

echo [*] Starting Expo development server...
echo [*] Scan the QR code with Expo Go app on your phone
echo [*] Or press 'w' to open in web browser
echo.

cd mobile
call npm start
goto end

REM ============================================================================
REM STOP
REM ============================================================================
:stop
echo.
echo ============================================
echo  Stopping Services
echo ============================================
echo.

echo [*] Stopping backend...
taskkill /F /IM python.exe >nul 2>&1

echo [*] Stopping mobile...
taskkill /F /IM node.exe >nul 2>&1

echo [OK] All services stopped
goto end

REM ============================================================================
REM USAGE
REM ============================================================================
:usage
echo.
echo ============================================
echo  IoT Smart Home Agent-Based System
echo ============================================
echo.
echo Usage: %0 {setup^|run^|stop}
echo.
echo Commands:
echo   setup  - Install all dependencies (first time only)
echo   run    - Start backend and mobile app
echo   stop   - Stop all running services
echo.
echo Quick start:
echo   1. %0 setup    # Install dependencies
echo   2. Edit .env and add your OpenAI API key
echo   3. %0 run      # Start the system
echo.
exit /b 1

:end
endlocal
