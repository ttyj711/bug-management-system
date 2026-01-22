@echo off
chcp 65001 >nul
set "script_dir=%~dp0"

echo ======================================
echo         BUG管理系统一键启动脚本          
echo ======================================
echo.

REM 检查Python环境
echo [检查环境] 正在检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到Python环境，请先安装Python 3.6+
    pause
    exit /b 1
)
python --version
echo [成功] Python环境检查通过

echo.

REM 检查Node.js环境
echo [检查环境] 正在检查Node.js环境...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到Node.js环境，请先安装Node.js 16+
    pause
    exit /b 1
)
node --version
echo [成功] Node.js环境检查通过

echo.

REM 启动后端服务器
echo [启动服务] 正在启动后端Django服务器...
start "后端服务器 - Django" cmd /k "cd /d %script_dir%backend && python manage.py runserver"
echo [成功] 后端服务器已启动，访问地址：http://127.0.0.1:8000/

echo.

REM 启动前端服务器
echo [启动服务] 正在启动前端Vite服务器...
start "前端服务器 - Vite" cmd /k "cd /d %script_dir%frontend && npm run dev"
echo [成功] 前端服务器已启动，访问地址：http://localhost:5173/

echo.
echo ======================================
echo         服务启动完成！                  
echo ======================================
echo 1. 前端应用地址：http://localhost:5173/
echo 2. 后端API地址：http://127.0.0.1:8000/api/
echo 3. 请不要关闭生成的命令窗口
echo 4. 按任意键退出此窗口...
echo ======================================
pause >nul
