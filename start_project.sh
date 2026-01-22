#!/bin/bash

# 设置脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "======================================"
echo "         BUG管理系统一键启动脚本          "
echo "======================================"
echo ""

# 检查Python环境
echo "[检查环境] 正在检查Python环境..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "[错误] 未找到Python环境，请先安装Python 3.6+"
    exit 1
fi

$PYTHON_CMD --version
echo "[成功] Python环境检查通过"
echo ""

# 检查Node.js环境
echo "[检查环境] 正在检查Node.js环境..."
if ! command -v node &> /dev/null; then
    echo "[错误] 未找到Node.js环境，请先安装Node.js 16+"
    exit 1
fi

node --version
echo "[成功] Node.js环境检查通过"
echo ""

# 启动后端服务器
echo "[启动服务] 正在启动后端Django服务器..."
$PYTHON_CMD "$SCRIPT_DIR/backend/manage.py" runserver &
BACKEND_PID=$!
echo "[成功] 后端服务器已启动，PID: $BACKEND_PID，访问地址：http://127.0.0.1:8000/"
echo ""

# 启动前端服务器
echo "[启动服务] 正在启动前端Vite服务器..."
cd "$SCRIPT_DIR/frontend" && npm run dev &
FRONTEND_PID=$!
echo "[成功] 前端服务器已启动，PID: $FRONTEND_PID，访问地址：http://localhost:5173/"
echo ""

echo "======================================"
echo "         服务启动完成！                  "
echo "======================================"
echo "1. 前端应用地址：http://localhost:5173/"
echo "2. 后端API地址：http://127.0.0.1:8000/api/"
echo "3. 后端服务器PID: $BACKEND_PID"
echo "4. 前端服务器PID: $FRONTEND_PID"
echo "5. 按 Ctrl+C 停止所有服务..."
echo "======================================"

echo ""
echo "[提示] 正在启动浏览器访问前端应用..."
# 尝试打开浏览器（支持不同系统）
if command -v open &> /dev/null; then
    open http://localhost:5173/  # macOS
elif command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:5173/  # Linux
fi

# 等待用户中断
trap "echo '\n[提示] 正在停止所有服务...'; kill $BACKEND_PID $FRONTEND_PID; echo '所有服务已停止'; exit 0" INT

# 持续运行
echo ""
echo "[提示] 按 Ctrl+C 停止所有服务"
wait
