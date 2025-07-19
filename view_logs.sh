#!/bin/bash
"""
日志查看脚本
可以查看各个组件的日志
"""

# 获取脚本所在目录（项目根目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGS_DIR="$SCRIPT_DIR/logs"

echo "📋 日志查看工具"
echo "=================="

# 检查日志目录是否存在
if [ ! -d "$LOGS_DIR" ]; then
    echo "❌ 日志目录不存在: $LOGS_DIR"
    echo "请先启动系统: ./start_with_venv.sh"
    exit 1
fi

# 显示可用的日志文件
echo "可用的日志文件:"
ls -la "$LOGS_DIR"/*.log 2>/dev/null | while read file; do
    filename=$(basename "$file")
    size=$(du -h "$file" | cut -f1)
    echo "  - $filename ($size)"
done

echo ""
echo "选择要查看的日志:"
echo "1) Web界面日志"
echo "2) 按键检测日志"
echo "3) 人脸检测日志"
echo "4) 所有日志 (实时)"
echo "5) 退出"
echo ""

read -p "请输入选择 (1-5): " choice

case $choice in
    1)
        echo "📱 查看Web界面日志..."
        tail -f "$LOGS_DIR/web_interface.log"
        ;;
    2)
        echo "🔘 查看按键检测日志..."
        tail -f "$LOGS_DIR/button.log"
        ;;
    3)
        echo "👤 查看人脸检测日志..."
        tail -f "$LOGS_DIR/face_detection.log"
        ;;
    4)
        echo "📋 查看所有日志 (实时)..."
        echo "按 Ctrl+C 退出"
        echo ""
        # 使用multitail查看多个日志文件
        if command -v multitail >/dev/null 2>&1; then
            multitail -e "Web界面" "$LOGS_DIR/web_interface.log" -e "按键检测" "$LOGS_DIR/button.log" -e "人脸检测" "$LOGS_DIR/face_detection.log"
        else
            # 如果没有multitail，使用简单的tail
            tail -f "$LOGS_DIR"/*.log
        fi
        ;;
    5)
        echo "退出"
        exit 0
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac 