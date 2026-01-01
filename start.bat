@echo off
REM EmailHandler - 邮件认证框架快速启动

setlocal enabledelayedexpansion

echo.
echo ===============================================
echo   EmailHandler - 邮件认证框架
echo ===============================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python
    echo 请先安装 Python 3.9+
    pause
    exit /b 1
)

REM 检查依赖
echo [检查] 依赖...
python -c "import requests; import flask" >nul 2>&1
if errorlevel 1 (
    echo [安装] 依赖...
    pip install -r requirements.txt
)

echo [OK] 依赖检查通过
echo.

REM 显示选项
echo [选项]:
echo   1. 启动邮件接收服务
echo   2. 启动验证工具
echo   3. 快速演示
echo.

set /p choice="请输入选择 (1/2/3): "

if "%choice%"=="1" (
    echo.
    echo [启动] 邮件接收服务...
    echo.
    python email_receiver.py
) else if "%choice%"=="2" (
    echo.
    echo [启动] 验证工具...
    echo.
    python verify.py
) else if "%choice%"=="3" (
    echo.
    echo [启动] 快速演示...
    echo.
    python quickstart.py
) else (
    echo [错误] 无效选择
    pause
    exit /b 1
)

pause
