@echo off
REM ============================================
REM Quick Kill All Project Processes (No Confirmation)
REM ============================================

echo Cleaning RPA_BOSS project processes...

REM Kill all Python processes
taskkill /F /IM python.exe /T 2>nul

REM Kill all Node.js processes
taskkill /F /IM node.exe /T 2>nul

REM Wait for process release
timeout /t 3 /nobreak >nul

REM Force release ports
for /f "tokens=2" %%a in ('netstat -ano ^| findstr ":3000.*LISTEN" 2^>nul') do taskkill /F /PID %%a 2>nul
for /f "tokens=2" %%a in ('netstat -ano ^| findstr ":5678.*LISTEN" 2^>nul') do taskkill /F /PID %%a 2>nul

echo OK - Cleanup Complete!
pause
