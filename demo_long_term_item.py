#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示长期保存物品的添加
"""

from smart_fridge_qwen import SmartFridgeQwenAgent
import json

def demo_long_term_item():
    """演示添加长期保存的物品"""
    fridge = SmartFridgeQwenAgent()
    
    print("=== 长期保存物品演示 ===")
    
    # 模拟大模型返回的长期保存物品信息
    long_term_item_response = {
        "food_name": "小提琴",
        "optimal_temp": 4,
        "shelf_life_days": "长期保存",
        "category": "乐器",
        "level": 2,
        "section": 0,
        "reasoning": "小提琴属于乐器类别，最佳存储温度为4°C，适合在冷藏区保存，长期保存无保质期限制。"
    }
    
    print("大模型返回的物品信息:")
    print(json.dumps(long_term_item_response, ensure_ascii=False, indent=2))
    
    # 测试保质期解析
    shelf_life = fridge._parse_shelf_life(long_term_item_response["shelf_life_days"])
    print(f"\n保质期解析结果: {shelf_life} ({'长期保存' if shelf_life == -1 else f'{shelf_life}天'})")
    
    # 测试温度匹配
    optimal_temp = fridge._parse_temperature(long_term_item_response["optimal_temp"])
    best_level = fridge.find_best_temperature_level(optimal_temp)
    level_temp = fridge.temperature_levels[best_level]
    print(f"最佳温度: {optimal_temp}°C -> 选择层: 第{best_level}层 ({level_temp}°C)")
    
    # 模拟添加到冰箱
    print(f"\n模拟添加到冰箱:")
    print(f"- 物品: {long_term_item_response['food_name']}")
    print(f"- 类别: {long_term_item_response['category']}")
    print(f"- 存储位置: 第{best_level}层第{long_term_item_response['section']}扇区")
    print(f"- 保质期: {'长期保存' if shelf_life == -1 else f'{shelf_life}天'}")
    print(f"- 存储温度: {level_temp}°C")
    
    # 测试进度条计算
    from web_interface import calculate_expiry_progress
    from datetime import datetime, timedelta
    
    if shelf_life == -1:
        # 长期保存，设置过期时间为100年后
        expiry_date = (datetime.now() + timedelta(days=36500)).isoformat()
    else:
        expiry_date = (datetime.now() + timedelta(days=shelf_life)).isoformat()
    
    progress = calculate_expiry_progress(expiry_date)
    print(f"\n进度条信息:")
    print(f"- 状态: {progress['status']}")
    print(f"- 颜色: {progress['color']}")
    print(f"- 文本: {progress['text']}")
    print(f"- 进度: {progress['percentage']}%")

if __name__ == "__main__":
    demo_long_term_item() 