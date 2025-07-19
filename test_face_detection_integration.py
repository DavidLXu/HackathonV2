#!/usr/bin/env python3
"""
测试人脸检测与Web服务器集成
"""

import requests
import time
import json

def test_face_detection_integration():
    """测试人脸检测集成"""
    print("🧪 测试人脸检测与Web服务器集成...")
    
    # 测试接近传感器API
    try:
        response = requests.post(
            'http://localhost:8080/api/proximity-sensor',
            json={"detected": True, "distance": "near"},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 接近传感器API测试成功")
            print(f"   问候语: {data['recommendation']['greeting']}")
            print(f"   主要建议: {data['recommendation']['main_recommendation']}")
            print(f"   快速提示: {data['recommendation']['quick_tip']}")
            print(f"   紧急程度: {data['recommendation']['urgency_level']}")
        else:
            print(f"❌ 接近传感器API测试失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    # 测试冰箱状态API
    try:
        response = requests.get('http://localhost:8080/api/fridge-status', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 冰箱状态API测试成功")
            print(f"   物品数量: {len(data.get('items', []))}")
        else:
            print(f"❌ 冰箱状态API测试失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def simulate_face_detection_events():
    """模拟人脸检测事件"""
    print("\n🔍 模拟人脸检测事件...")
    
    for i in range(3):
        print(f"   触发第 {i+1} 次人脸检测事件...")
        
        try:
            response = requests.post(
                'http://localhost:8080/api/proximity-sensor',
                json={"detected": True, "distance": "near"},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 事件 {i+1} 成功: {data['recommendation']['greeting']}")
            else:
                print(f"   ❌ 事件 {i+1} 失败: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 事件 {i+1} 异常: {e}")
        
        time.sleep(2)  # 等待2秒再触发下一次

if __name__ == "__main__":
    print("🚀 开始测试人脸检测集成...")
    print("=" * 50)
    
    # 基础API测试
    test_face_detection_integration()
    
    # 模拟人脸检测事件
    simulate_face_detection_events()
    
    print("\n🎉 测试完成！")
    print("💡 提示: 现在可以运行 start_with_venv.sh 来启动完整系统") 