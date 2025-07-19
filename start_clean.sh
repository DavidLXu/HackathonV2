#!/bin/bash
"""
干净的智慧冰箱系统启动脚本
避免输出混乱，使用日志文件
"""

# 获取脚本所在目录（项目根目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 启动智慧冰箱系统 (干净模式)..."
echo "=================================================="

# 检查虚拟环境是否存在
VENV_PATH="$HOME/env"
if [ ! -d "$VENV_PATH" ]; then
    echo "❌ 虚拟环境不存在: $VENV_PATH"
    echo "请先创建虚拟环境:"
    echo "  python -m venv ~/env"
    echo "  source ~/env/bin/activate"
    echo "  pip install flask dashscope requests RPi.GPIO"
    exit 1
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source "$HOME/env/bin/activate"

# 检查是否成功激活
if [ "$VIRTUAL_ENV" != "$HOME/env" ]; then
    echo "❌ 虚拟环境激活失败"
    exit 1
fi

echo "✅ 虚拟环境已激活: $VIRTUAL_ENV"

# 设置环境变量
echo "🔑 设置环境变量..."
export DASHSCOPE_API_KEY="sk-0419b645f1d4499da2094c863442e0db"
echo "✅ API密钥已设置"

# 创建日志目录
mkdir -p "$SCRIPT_DIR/logs"

# 启动Web界面
echo "🌐 启动Web界面..."
cd "$SCRIPT_DIR/Agent"
python web_interface.py > "$SCRIPT_DIR/logs/web_interface.log" 2>&1 &
WEB_PID=$!
echo "✅ Web界面已启动 (PID: $WEB_PID)"

# 等待Web服务器启动
echo "⏳ 等待Web服务器启动..."
for i in {1..30}; do
    if curl -s http://localhost:8080/api/fridge-status >/dev/null 2>&1; then
        echo "✅ Web服务器已就绪"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Web服务器启动超时"
        kill $WEB_PID 2>/dev/null
        exit 1
    fi
    sleep 1
done

# 启动按键检测
echo "🔘 启动按键检测..."
cd "$SCRIPT_DIR/Sensor"
python button.py > "$SCRIPT_DIR/logs/button.log" 2>&1 &
BUTTON_PID=$!
echo "✅ 按键检测已启动 (PID: $BUTTON_PID)"

# 启动人脸检测
echo "👤 启动人脸检测..."
cd "$SCRIPT_DIR/Sensor"
python start_face_detection.py > "$SCRIPT_DIR/logs/face_detection.log" 2>&1 &
FACE_PID=$!
echo "✅ 人脸检测已启动 (PID: $FACE_PID)"

# 等待所有进程稳定
echo "⏳ 等待所有进程稳定..."
sleep 5

# 检查所有进程是否还在运行
echo "🔍 检查进程状态..."
if kill -0 $WEB_PID 2>/dev/null; then
    echo "✅ Web界面运行正常"
else
    echo "❌ Web界面进程已停止"
fi

if kill -0 $BUTTON_PID 2>/dev/null; then
    echo "✅ 按键检测运行正常"
else
    echo "❌ 按键检测进程已停止"
fi

if kill -0 $FACE_PID 2>/dev/null; then
    echo "✅ 人脸检测运行正常"
else
    echo "❌ 人脸检测进程已停止"
fi

echo ""
echo "🎉 系统启动完成！"
echo "📱 Web界面: http://localhost:8080"
echo "🔘 物理按键:"
echo "   - GPIO 16 (绿色): 放入物品"
echo "   - GPIO 17 (红色): 取出物品"
echo "👤 人脸检测: 自动触发接近传感器事件"
echo ""
echo "📋 日志文件位置:"
echo "   - Web界面: logs/web_interface.log"
echo "   - 按键检测: logs/button.log"
echo "   - 人脸检测: logs/face_detection.log"
echo ""
echo "💡 查看日志: ./view_logs.sh"
echo "按 Ctrl+C 停止系统"

# 等待中断信号
trap 'echo ""; echo "🛑 正在停止系统..."; kill $WEB_PID $BUTTON_PID $FACE_PID 2>/dev/null; echo "✅ 系统已停止"; exit 0' INT TERM

# 保持运行
wait 