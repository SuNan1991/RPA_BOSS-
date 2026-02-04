@echo off
chcp 65001 >nul
echo ====================================
echo   BOSS直聘自动化招聘系统 (uv)
echo ====================================
echo.

echo [1/2] 启动后端服务...
cd backend
start "BOSS RPA Backend" uv run python -m app.main
timeout /t 3 >nul

echo [2/2] 启动前端服务...
cd ..\frontend
start "BOSS RPA Frontend" npm run dev

echo.
echo ====================================
echo   服务启动成功！
echo   后端地址: http://localhost:8000
echo   前端地址: http://localhost:5173
echo   API文档: http://localhost:8000/docs
echo ====================================
pause
