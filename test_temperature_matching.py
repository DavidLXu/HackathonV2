#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试温度匹配逻辑
"""

from smart_fridge_qwen import SmartFridgeQwenAgent

def test_temperature_matching():
    """测试温度匹配功能"""
    fridge = SmartFridgeQwenAgent()
    
    # 测试不同的最佳温度
    test_temps = [
        (-20, "冰淇淋"),
        (-10, "冷冻肉类"),
        (-5, "冷冻蔬菜"),
        (0, "冷藏肉类"),
        (2, "新鲜蔬菜"),
        (4, "牛奶"),
        (6, "熟食"),
        (8, "水果"),
        (10, "常温食品"),
        (15, "室温食品")
    ]
    
    print("=== 温度匹配测试 ===")
    print("最佳温度 -> 选择的层 -> 层温度")
    print("-" * 40)
    
    for optimal_temp, food_name in test_temps:
        best_level = fridge.find_best_temperature_level(optimal_temp)
        level_temp = fridge.temperature_levels[best_level]
        print(f"{optimal_temp:>3}°C -> 第{best_level}层 -> {level_temp}°C ({food_name})")
    
    print("\n=== 温度分区设置 ===")
    for level, temp in fridge.temperature_levels.items():
        print(f"第{level}层: {temp}°C")

if __name__ == "__main__":
    test_temperature_matching() 