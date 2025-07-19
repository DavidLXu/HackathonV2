#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧冰箱Qwen Agent演示脚本
"""

import os
import json
from smart_fridge_qwen import SmartFridgeQwenAgent

def demo_qwen_agent():
    """演示基于Qwen VL的智慧冰箱Agent"""
    print("=== 智慧冰箱Qwen Agent演示 ===")
    
    # 初始化Agent
    fridge = SmartFridgeQwenAgent()
    
    # 1. 添加物品到冰箱
    print("\n1. 添加物品到冰箱")
    if os.path.exists("some_food.jpg"):
        result = fridge.add_item_to_fridge("some_food.jpg")
        print(f"添加结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    else:
        print("未找到some_food.jpg文件")
    
    # 2. 显示库存
    print("\n2. 查看冰箱库存")
    inventory = fridge.get_fridge_inventory()
    print(f"库存信息: {json.dumps(inventory, ensure_ascii=False, indent=2)}")
    
    # 3. 获取推荐
    print("\n3. 获取智能推荐")
    recommendations = fridge.get_recommendations()
    print(f"推荐信息: {json.dumps(recommendations, ensure_ascii=False, indent=2)}")
    
    print("\n=== 智慧冰箱Qwen Agent演示完成 ===")

def interactive_demo():
    """交互式演示"""
    print("=== 交互式智慧冰箱Qwen演示 ===")
    
    fridge = SmartFridgeQwenAgent()
    
    print("智慧冰箱Qwen Agent已启动！")
    print("可用命令：")
    print("- 'add <图片路径>': 添加物品到冰箱")
    print("- 'inventory': 查看冰箱库存")
    print("- 'recommend': 获取智能推荐")
    print("- 'status': 查看冰箱状态")
    print("- 'quit': 退出")
    
    while True:
        try:
            command = input("\n请输入命令: ").strip()
            
            if command.lower() == 'quit':
                print("再见！")
                break
            elif command.lower() == 'inventory':
                inventory = fridge.get_fridge_inventory()
                print(f"冰箱库存: {json.dumps(inventory, ensure_ascii=False, indent=2)}")
            elif command.lower() == 'status':
                status = fridge.get_fridge_status()
                print(f"冰箱状态: {json.dumps(status, ensure_ascii=False, indent=2)}")
            elif command.lower() == 'recommend':
                result = fridge.get_recommendations()
                print(f"推荐结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            elif command.startswith('add '):
                image_path = command[4:].strip()
                if os.path.exists(image_path):
                    result = fridge.add_item_to_fridge(image_path)
                    print(f"添加结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
                else:
                    print(f"文件不存在: {image_path}")
            else:
                print("未知命令，请重试")
                
        except KeyboardInterrupt:
            print("\n再见！")
            break
        except Exception as e:
            print(f"发生错误: {e}")

def test_basic_functions():
    """测试基础功能"""
    print("=== 测试基础功能 ===")
    
    fridge = SmartFridgeQwenAgent()
    
    # 测试冰箱控制函数
    print("\n1. 测试冰箱控制函数")
    print("测试lift函数:")
    fridge.lift(2)
    print("测试turn函数:")
    fridge.turn(1)
    print("测试fetch函数:")
    fridge.fetch()
    
    # 测试数据管理
    print("\n2. 测试数据管理")
    print(f"当前冰箱数据: {fridge.fridge_data}")
    
    # 测试状态获取
    print("\n3. 测试状态获取")
    status = fridge.get_fridge_status()
    print(f"冰箱状态: {json.dumps(status, ensure_ascii=False, indent=2)}")
    
    print("\n=== 基础功能测试完成 ===")

def main():
    """主函数"""
    print("智慧冰箱Qwen Agent演示程序")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "basic":
            test_basic_functions()
        elif mode == "demo":
            demo_qwen_agent()
        elif mode == "interactive":
            interactive_demo()
        else:
            print("未知模式，使用默认演示")
            demo_qwen_agent()
    else:
        print("运行默认演示...")
        demo_qwen_agent()

if __name__ == "__main__":
    import sys
    main() 