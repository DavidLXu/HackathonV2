#!/usr/bin/env python3
"""
测试整合后的人脸检测功能
"""

import sys
import os
import time
import threading

# 设置环境变量
os.environ['DASHSCOPE_API_KEY'] = 'sk-0419b645f1d4499da2094c863442e0db'

# 添加Agent目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'Agent'))

from smart_fridge_qwen import SmartFridgeQwenAgent

def test_face_detection_integration():
    """测试人脸检测集成"""
    print("🧪 测试整合后的人脸检测功能...")
    print("=" * 50)
    
    # 创建冰箱Agent实例
    fridge = SmartFridgeQwenAgent()
    
    # 检查人脸检测是否启用
    if not fridge.face_detection_enabled:
        print("❌ 人脸检测功能未启用")
        return False
    
    print("✅ 人脸检测功能已启用")
    
    # 启动人脸检测监控
    print("👤 启动人脸检测监控...")
    fridge.start_face_detection_monitor()
    
    print("🔍 人脸检测监控已启动，等待检测...")
    print("💡 提示：请站在摄像头前测试人脸检测功能")
    print("⏰ 检测到人脸接近时会触发接近传感器事件")
    print("按 Ctrl+C 停止测试")
    
    try:
        # 运行一段时间进行测试
        for i in range(30):  # 运行30秒
            time.sleep(1)
            if i % 10 == 0:
                print(f"⏳ 测试进行中... ({i+1}/30秒)")
    except KeyboardInterrupt:
        print("\n🛑 用户中断测试")
    finally:
        # 停止人脸检测监控
        print("🛑 停止人脸检测监控...")
        fridge.stop_face_detection_monitor()
        print("✅ 测试完成")
    
    return True

def test_fridge_functionality():
    """测试冰箱基本功能"""
    print("\n🧪 测试冰箱基本功能...")
    print("=" * 30)
    
    fridge = SmartFridgeQwenAgent()
    
    # 测试获取冰箱状态
    try:
        status = fridge.get_fridge_status()
        print(f"✅ 冰箱状态获取成功: {len(status.get('inventory', []))} 个物品")
    except Exception as e:
        print(f"❌ 冰箱状态获取失败: {e}")
    
    # 测试获取推荐
    try:
        recommendations = fridge.get_recommendations()
        print(f"✅ 推荐功能正常: {recommendations.get('total_recommendations', 0)} 个推荐")
    except Exception as e:
        print(f"❌ 推荐功能失败: {e}")
    
    print("✅ 冰箱基本功能测试完成")

if __name__ == "__main__":
    print("🚀 开始测试整合后的人脸检测功能...")
    
    # 测试冰箱基本功能
    test_fridge_functionality()
    
    # 测试人脸检测集成
    test_face_detection_integration()
    
    print("\n🎉 所有测试完成！") 