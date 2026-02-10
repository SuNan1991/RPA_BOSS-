@echo off
REM ============================================
REM RPA_BOSS Project - Restart All Services
REM ============================================

echo.
echo ============================================
echo    RPA_BOSS Project Restart Script
echo ============================================
echo.

REM Step 1: Kill existing processes
echo [1/3] Cleaning existing processes...
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM node.exe /T 2>nul
timeout /t 3 /nobreak >nul
echo OK - Process cleanup complete
echo.

REM Step 2: Start backend
echo [2/3] Starting backend service (port 3000)...
cd /d "%~dp0backend"
start "RPA_BOSS Backend" cmd /k "python -m uvicorn app.main:app --host 0.0.0.0 --port 3000"
echo OK - Backend service started
echo.

REM Wait for backend startup
echo Waiting for backend service to start...
timeout /t 5 /nobreak >nul

REM Step 3: Start frontend
echo [3/3] Starting frontend service (port 5678)...
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
echo Press any key to close this window...
pause >nul
