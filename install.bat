@echo off
chcp 65001 >nul
echo ====================================
echo   安装项目依赖
echo ====================================
echo.

echo [检查 uv]
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo uv 未安装，正在安装...
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
)

echo.
echo [1/2] 安装后端依赖...
cd backend
uv sync
cd ..

echo.
echo [2/2] 安装前端依赖...
cd frontend
call npm install
cd ..

echo.
echo ====================================
echo   依赖安装完成！
echo   运行 start.bat 启动服务
echo ====================================
pause
