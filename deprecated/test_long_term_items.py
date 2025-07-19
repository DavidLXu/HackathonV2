#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试长期保存物品的处理逻辑
"""

from smart_fridge_qwen import SmartFridgeQwenAgent

def test_shelf_life_parsing():
    """测试保质期解析功能"""
    fridge = SmartFridgeQwenAgent()
    
    # 测试不同的保质期输入
    test_cases = [
        ("7天", 7),
        ("30天", 30),
        ("长期", -1),
        ("永久", -1),
        ("无保质期", -1),
        ("长期保存", -1),
        ("无限期", -1),
        ("7", 7),
        ("30", 30),
        ("长期保存，无期限", -1),
        ("保质期7天", 7),
        ("可保存30天", 30),
        ("乐器，长期保存", -1),
        ("小提琴，无保质期", -1)
    ]
    
    print("=== 保质期解析测试 ===")
    print("输入 -> 解析结果")
    print("-" * 30)
    
    for input_str, expected in test_cases:
        result = fridge._parse_shelf_life(input_str)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{input_str}' -> {result} (期望: {expected})")

def test_temperature_matching_for_items():
    """测试不同物品的温度匹配"""
    fridge = SmartFridgeQwenAgent()
    
    # 测试不同物品的最佳温度
    test_items = [
        ("冰淇淋", -15, "冷冻食品"),
        ("小提琴", 4, "乐器"),
        ("苹果", 2, "水果"),
        ("牛奶", 4, "乳制品"),
        ("工具", 6, "工具"),
        ("药品", 2, "药品")
    ]
    
    print("\n=== 物品温度匹配测试 ===")
    print("物品 -> 最佳温度 -> 选择层 -> 层温度")
    print("-" * 50)
    
    for item_name, optimal_temp, category in test_items:
        best_level = fridge.find_best_temperature_level(optimal_temp)
        level_temp = fridge.temperature_levels[best_level]
        print(f"{item_name} -> {optimal_temp}°C -> 第{best_level}层 -> {level_temp}°C")

if __name__ == "__main__":
    test_shelf_life_parsing()
    test_temperature_matching_for_items() 