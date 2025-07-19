#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧冰箱Agent测试脚本
"""

import os
import json
from datetime import datetime, timedelta
from smart_fridge_agent import SmartFridgeAgent

def test_basic_functions():
    """测试基础功能"""
    print("=== 测试基础功能 ===")
    
    # 初始化Agent（使用测试API密钥）
    api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    fridge = SmartFridgeAgent(api_key)
    
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
    
    # 测试食物数据库
    print("\n3. 测试食物数据库")
    test_foods = ["苹果", "牛奶", "肉类", "未知食物"]
    for food in test_foods:
        info = fridge.get_food_info(food)
        print(f"{food}: {info}")
    
    # 测试存储位置查找
    print("\n4. 测试存储位置查找")
    test_temps = [2, 4, 6, 8, 10]
    for temp in test_temps:
        level, section = fridge.find_optimal_storage_location(temp)
        print(f"最佳温度 {temp}°C -> 层 {level}, 扇区 {section}")
    
    print("\n=== 基础功能测试完成 ===")

def test_inventory_management():
    """测试库存管理"""
    print("\n=== 测试库存管理 ===")
    
    api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    fridge = SmartFridgeAgent(api_key)
    
    # 模拟添加一些物品
    print("\n1. 模拟添加物品")
    
    # 清空现有数据
    fridge.fridge_data = fridge.initialize_fridge_data()
    
    # 添加测试物品
    test_items = [
        {"name": "苹果", "category": "水果", "optimal_temp": 4, "shelf_life_days": 14},
        {"name": "牛奶", "category": "乳制品", "optimal_temp": 4, "shelf_life_days": 7},
        {"name": "肉类", "category": "肉类", "optimal_temp": 2, "shelf_life_days": 3}
    ]
    
    for i, item in enumerate(test_items):
        item_id = f"{item['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}"
        level, section = fridge.find_optimal_storage_location(item["optimal_temp"])
        
        fridge.fridge_data["items"][item_id] = {
            "name": item["name"],
            "category": item["category"],
            "level": level,
            "section": section,
            "optimal_temp": item["optimal_temp"],
            "shelf_life_days": item["shelf_life_days"],
            "added_time": datetime.now().isoformat(),
            "expiry_date": (datetime.now() + timedelta(days=item["shelf_life_days"])).isoformat()
        }
        
        fridge.fridge_data["level_usage"][str(level)][str(section)] = True
        print(f"添加 {item['name']} 到第 {level} 层第 {section} 扇区")
    
    # 保存数据
    fridge.save_fridge_data()
    
    # 查看库存
    print("\n2. 查看库存")
    inventory = fridge.get_fridge_inventory()
    print(f"库存信息: {json.dumps(inventory, ensure_ascii=False, indent=2)}")
    
    # 获取推荐
    print("\n3. 获取推荐")
    recommendations = fridge.get_recommendations()
    print(f"推荐信息: {json.dumps(recommendations, ensure_ascii=False, indent=2)}")
    
    print("\n=== 库存管理测试完成 ===")

def test_error_handling():
    """测试错误处理"""
    print("\n=== 测试错误处理 ===")
    
    api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    fridge = SmartFridgeAgent(api_key)
    
    # 测试无效的层索引
    print("\n1. 测试无效层索引")
    fridge.lift(10)  # 应该打印错误信息
    
    # 测试无效的扇区索引
    print("\n2. 测试无效扇区索引")
    fridge.turn(5)  # 应该打印错误信息
    
    # 测试不存在的图片文件
    print("\n3. 测试不存在的图片文件")
    result = fridge.add_item_to_fridge("nonexistent.jpg")
    print(f"结果: {result}")
    
    print("\n=== 错误处理测试完成 ===")

def main():
    """主测试函数"""
    print("智慧冰箱Agent测试程序")
    print("=" * 50)
    
    try:
        # 运行各项测试
        test_basic_functions()
        test_inventory_management()
        test_error_handling()
        
        print("\n" + "=" * 50)
        print("所有测试完成！")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 