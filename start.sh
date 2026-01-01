#!/bin/bash

# EmailHandler - 邮件认证框架快速启动

echo ""
echo "==============================================="
echo "   EmailHandler - 邮件认证框架"
echo "==============================================="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到 Python 3"
    echo "请先安装 Python 3.9+"
    exit 1
fi

# 检查依赖
echo "[检查] 依赖..."
python3 -c "import requests; import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[安装] 依赖..."
    pip install -r requirements.txt
fi

echo "[OK] 依赖检查通过"
echo ""

# 显示选项
echo "[选项]:"
echo "  1. 启动邮件接收服务"
echo "  2. 启动验证工具"
echo "  3. 快速演示"
echo ""

read -p "请输入选择 (1/2/3): " choice

case $choice in
    1)
        echo ""
        echo "[启动] 邮件接收服务..."
        echo ""
        python3 email_receiver.py
        ;;
    2)
        echo ""
        echo "[启动] 验证工具..."
        echo ""
        python3 verify.py
        ;;
    3)
        echo ""
        echo "[启动] 快速演示..."
        echo ""
        python3 quickstart.py
        ;;
    *)
        echo "[错误] 无效选择"
        exit 1
        ;;
esac
