#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧冰箱Agent演示脚本
"""

import os
import sys
from smart_fridge_agent import SmartFridgeAgent
from smart_fridge_agent_advanced import AdvancedSmartFridgeAgent

def demo_basic_agent():
    """演示基础版本的智慧冰箱Agent"""
    print("=== 基础版本智慧冰箱Agent演示 ===")
    
    api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    fridge = SmartFridgeAgent(api_key)
    
    # 1. 添加物品到冰箱
    print("\n1. 添加物品到冰箱")
    if os.path.exists("some_food.jpg"):
        result = fridge.add_item_to_fridge("some_food.jpg")
        print(f"添加结果: {result}")
    else:
        print("未找到some_food.jpg文件")
    
    # 2. 显示库存
    print("\n2. 查看冰箱库存")
    inventory = fridge.get_fridge_inventory()
    print(f"库存信息: {inventory}")
    
    # 3. 获取推荐
    print("\n3. 获取智能推荐")
    recommendations = fridge.get_recommendations()
    print(f"推荐信息: {recommendations}")
    
    print("\n=== 基础版本演示完成 ===\n")

def demo_advanced_agent():
    """演示高级版本的智慧冰箱Agent"""
    print("=== 高级版本智慧冰箱Agent演示 ===")
    
    api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    fridge = AdvancedSmartFridgeAgent(api_key)
    
    # 1. 使用自然语言添加物品
    print("\n1. 使用自然语言添加物品")
    if os.path.exists("some_food.jpg"):
        result = fridge.process_user_request("some_food.jpg", "请帮我将这个食物放入冰箱")
        print(f"处理结果: {result}")
    else:
        print("未找到some_food.jpg文件")
    
    # 2. 获取智能推荐
    print("\n2. 获取智能推荐")
    result = fridge.process_user_request("some_food.jpg", "请给我一些关于冰箱内容的建议")
    print(f"推荐结果: {result}")
    
    # 3. 查看库存
    print("\n3. 查看冰箱库存")
    inventory = fridge.get_fridge_inventory()
    print(f"库存信息: {inventory}")
    
    print("\n=== 高级版本演示完成 ===\n")

def interactive_demo():
    """交互式演示"""
    print("=== 交互式智慧冰箱演示 ===")
    
    api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    fridge = AdvancedSmartFridgeAgent(api_key)
    
    print("智慧冰箱Agent已启动！")
    print("可用命令：")
    print("- 'add <图片路径>': 添加物品到冰箱")
    print("- 'inventory': 查看冰箱库存")
    print("- 'recommend': 获取智能推荐")
    print("- 'quit': 退出")
    
    while True:
        try:
            command = input("\n请输入命令: ").strip()
            
            if command.lower() == 'quit':
                print("再见！")
                break
            elif command.lower() == 'inventory':
                inventory = fridge.get_fridge_inventory()
                print(f"冰箱库存: {inventory}")
            elif command.lower() == 'recommend':
                result = fridge.process_user_request("some_food.jpg", "请给我一些关于冰箱内容的建议")
                print(f"推荐结果: {result}")
            elif command.startswith('add '):
                image_path = command[4:].strip()
                if os.path.exists(image_path):
                    result = fridge.process_user_request(image_path, "请帮我将这个食物放入冰箱")
                    print(f"添加结果: {result}")
                else:
                    print(f"文件不存在: {image_path}")
            else:
                print("未知命令，请重试")
                
        except KeyboardInterrupt:
            print("\n再见！")
            break
        except Exception as e:
            print(f"发生错误: {e}")

def main():
    """主函数"""
    print("智慧冰箱Agent演示程序")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "basic":
            demo_basic_agent()
        elif mode == "advanced":
            demo_advanced_agent()
        elif mode == "interactive":
            interactive_demo()
        else:
            print("未知模式，使用默认演示")
            demo_basic_agent()
            demo_advanced_agent()
    else:
        print("运行默认演示...")
        demo_basic_agent()
        demo_advanced_agent()

if __name__ == "__main__":
    main() 