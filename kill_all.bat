@echo off
REM ============================================
REM RPA_BOSS Project - Kill All Processes
REM ============================================

echo.
echo ============================================
echo    RPA_BOSS Process Cleanup Tool
echo ============================================
echo.

REM Show current processes
echo [1/6] Checking Python processes...
tasklist | findstr /I "python.exe"
if %ERRORLEVEL% EQU 0 (
    echo    Found Python processes
) else (
    echo    No Python processes found
)
echo.

echo [2/6] Checking Node.js processes...
tasklist | findstr /I "node.exe"
if %ERRORLEVEL% EQU 0 (
    echo    Found Node.js processes
) else (
    echo    No Node.js processes found
)
echo.

echo [3/6] Checking port usage (3000, 5678)...
netstat -ano | findstr ":3000.*LISTEN"
netstat -ano | findstr ":5678.*LISTEN"
echo.

REM Ask for confirmation
set /p confirm="Terminate all project processes? (Y/N): "
if /I not "%confirm%"=="Y" (
    echo Operation cancelled
    pause
    exit /b 0
)

echo.
echo ============================================
echo    Starting cleanup...
echo ============================================
echo.

REM Method 1: Kill all Python processes
echo [1/4] Terminating Python processes...
taskkill /F /IM python.exe /T 2>nul
if %ERRORLEVEL% EQU 0 (
    echo    OK - Python processes terminated
) else (
    echo    - No Python processes found or already terminated
)

REM Wait a bit
timeout /t 2 /nobreak >nul

REM Method 2: Kill all Node.js processes
echo [2/4] Terminating Node.js processes...
taskkill /F /IM node.exe /T 2>nul
if %ERRORLEVEL% EQU 0 (
    echo    OK - Node.js processes terminated
) else (
    echo    - No Node.js processes found or already terminated
)

REM Wait a bit
timeout /t 2 /nobreak >nul

REM Method 3: Kill processes on ports
echo [3/4] Releasing port 3000...
for /f "tokens=2" %%a in ('netstat -ano ^| findstr ":3000.*LISTEN" 2^>nul') do (
    taskkill /F /PID %%a 2>nul
)
echo    OK - Port 3000 released

REM Method 4: Release frontend port
echo [4/4] Releasing port 5678...
for /f "tokens=2" %%a in ('netstat -ano ^| findstr ":5678.*LISTEN" 2^>nul') do (
    taskkill /F /PID %%a 2>nul
)
echo    OK - Port 5678 released

echo.
echo ============================================
echo    Verifying cleanup...
echo ============================================
echo.

REM Check again
timeout /t 2 /nobreak >nul

echo Checking Python processes...
tasklist | findstr /I "python.exe"
if %ERRORLEVEL% EQU 0 (
    echo    WARNING: Python processes still running
) else (
    echo    OK - All Python processes cleaned
)
echo.

echo Checking Node.js processes...
tasklist | findstr /I "node.exe"
if %ERRORLEVEL% EQU 0 (
    echo    WARNING: Node.js processes still running
) else (
    echo    OK - All Node.js processes cleaned
)
echo.

echo Checking port usage...
netstat -ano | findstr ":3000.*LISTEN" >nul
if %ERRORLEVEL% EQU 0 (
    echo    WARNING: Port 3000 still in use
) else (
    echo    OK - Port 3000 released
)

netstat -ano | findstr ":5678.*LISTEN" >nul
if %ERRORLEVEL% EQU 0 (
    echo    WARNING: Port 5678 still in use
) else (
    echo    OK - Port 5678 released
)

echo.
echo ============================================
echo    Cleanup Complete!
echo ============================================
echo.
echo You can now restart the project:
echo   - Backend: cd backend ^&^& python -m uvicorn app.main:app --port 3000
echo   - Frontend: cd frontend ^&^& npm run dev
echo.
pause
