@echo off
REM ============================================
REM RPA_BOSS Project - Start All Services (No Cleanup)
REM ============================================

echo.
echo ============================================
echo    RPA_BOSS Project Start Script
echo ============================================
echo.

REM Check if ports are in use
echo Checking port availability...
netstat -ano | findstr ":3000.*LISTEN" >nul
if %ERRORLEVEL% EQU 0 (
    echo WARNING: Port 3000 is already in use!
    echo Please run kill_all.bat to clean processes first
    pause
    exit /b 1
)

netstat -ano | findstr ":5678.*LISTEN" >nul
if %ERRORLEVEL% EQU 0 (
    echo WARNING: Port 5678 is already in use!
    echo Please run kill_all.bat to clean processes first
    pause
    exit /b 1
)

echo OK - Port check passed
echo.

REM Start backend
echo [1/2] Starting backend service (port 3000)...
cd /d "%~dp0backend"
start "RPA_BOSS Backend" cmd /k "python -m uvicorn app.main:app --host 0.0.0.0 --port 3000"
echo OK - Backend service started
echo.

REM Wait for backend startup
echo Waiting for backend service to be ready...
timeout /t 5 /nobreak >nul

REM Start frontend
echo [2/2] Starting frontend service (port 5678)...
cd /d "%~dp0frontend"
start "RPA_BOSS Frontend" cmd /k "npm run dev"
echo OK - Frontend service started
echo.

echo ============================================
echo    All Services Started!
echo ============================================
echo.
echo Service URLs:
echo   - Backend API:  http://localhost:3000
echo   - API Docs:     http://localhost:3000/docs
echo   - Frontend UI:  http://localhost:5678
echo   - Log Stats:    http://localhost:3000/api/logs/stats
echo.
echo Tip: Closing this window will not affect services
echo.
