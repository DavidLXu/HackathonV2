#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示增强的推荐界面功能
"""

import requests
import json
from datetime import datetime

def demo_enhanced_recommendations():
    """演示增强的推荐功能"""
    base_url = "http://localhost:8080"
    
    print("=== 增强推荐界面演示 ===")
    
    # 1. 获取推荐数据
    print("\n1. 获取推荐数据")
    try:
        response = requests.get(f"{base_url}/api/recommendations")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 推荐获取成功")
            print(f"   推荐数量: {len(data.get('recommendations', []))}")
            
            # 显示每个推荐的详细信息
            for i, rec in enumerate(data.get('recommendations', []), 1):
                print(f"\n   推荐{i}: {rec.get('title')}")
                print(f"     类型: {rec.get('type')}")
                print(f"     消息: {rec.get('message')}")
                print(f"     行动: {rec.get('action')}")
                
                # 显示物品emoji
                items = rec.get('items', [])
                if items:
                    print(f"     物品数量: {len(items)}")
                    print(f"     物品列表:")
                    for item in items[:5]:  # 只显示前5个
                        emoji = get_food_emoji(item.get('name', ''), item.get('category', ''))
                        print(f"       {emoji} {item.get('name')} ({item.get('category')})")
                    if len(items) > 5:
                        print(f"       ... 还有{len(items)-5}个物品")
        else:
            print(f"❌ 推荐获取失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 推荐获取异常: {e}")
    
    # 2. 测试接近传感器
    print("\n2. 测试接近传感器")
    try:
        response = requests.post(f"{base_url}/api/proximity-sensor")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 接近传感器响应成功")
            
            recommendation = data.get('recommendation', {})
            print(f"   问候: {recommendation.get('greeting')}")
            print(f"   主要推荐: {recommendation.get('main_recommendation')}")
            print(f"   快速提示: {recommendation.get('quick_tip')}")
            print(f"   紧急程度: {recommendation.get('urgency_level')}")
        else:
            print(f"❌ 接近传感器失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 接近传感器异常: {e}")
    
    # 3. 显示当前时间建议
    print("\n3. 当前时间建议")
    current_hour = datetime.now().hour
    if current_hour < 12:
        print("   🌅 早上建议:")
        print("      - 建议食用新鲜水果补充维生素")
        print("      - 搭配蛋白质，营养更均衡")
        print("      - 苹果富含纤维，是早餐的好选择")
    elif current_hour < 18:
        print("   ☀️ 下午建议:")
        print("      - 下午茶时间，可以享用冰箱里的新鲜食物")
        print("      - 注意检查食物保质期，避免浪费")
        print("      - 可以制作简单的三明治或沙拉")
    else:
        print("   🌙 晚上建议:")
        print("      - 建议整理冰箱，为明天做准备")
        print("      - 清理即将过期的食物")
        print("      - 可以列出明天的购物清单")
    
    # 4. 显示推荐分类说明
    print("\n4. 推荐分类说明")
    categories = [
        ("⚠️", "即将过期物品", "提醒用户尽快处理"),
        ("✅", "新鲜物品", "显示可放心食用的物品"),
        ("🔄", "长期保存物品", "显示无需担心过期的物品"),
        ("💡", "一般建议", "当没有特殊情况时的友好提示")
    ]
    
    for icon, name, desc in categories:
        print(f"   {icon} {name}: {desc}")

def get_food_emoji(food_name, category):
    """获取食物的emoji"""
    food_emojis = {
        "苹果": "🍎", "香蕉": "🍌", "橙子": "🍊", "葡萄": "🍇", "草莓": "🍓",
        "牛奶": "🥛", "鸡蛋": "🥚", "面包": "🍞", "米饭": "🍚", "面条": "🍜",
        "牛肉": "🥩", "猪肉": "🥩", "鸡肉": "🍗", "鱼": "🐟", "虾": "🦐",
        "蔬菜": "🥬", "胡萝卜": "🥕", "土豆": "🥔", "洋葱": "🧅", "大蒜": "🧄",
        "三明治": "🥪", "汉堡": "🍔", "披萨": "🍕", "寿司": "🍣", "沙拉": "🥗",
        "冰淇淋": "🍦", "蛋糕": "🍰", "巧克力": "🍫", "糖果": "🍬", "饼干": "🍪",
        "咖啡": "☕", "茶": "🍵", "果汁": "🧃", "可乐": "🥤", "啤酒": "🍺",
        "小提琴": "🎻", "口琴": "🎵", "吉他": "🎸", "钢琴": "🎹", "鼓": "🥁"
    }
    
    # 先按名称匹配
    if food_name in food_emojis:
        return food_emojis[food_name]
    
    # 按类别匹配
    category_emojis = {
        "水果": "🍎", "蔬菜": "🥬", "肉类": "🥩", "乳制品": "🥛", "谷物": "🍞",
        "海鲜": "🐟", "甜点": "🍰", "饮料": "🥤", "乐器": "🎵", "工具": "🔧"
    }
    
    if category in category_emojis:
        return category_emojis[category]
    
    # 默认emoji
    return "📦"

if __name__ == "__main__":
    demo_enhanced_recommendations()
    print("\n=== 演示完成 ===")
    print("\n💡 提示：")
    print("   - 在Web界面中，推荐卡片会显示物品的emoji")
    print("   - 鼠标悬停在emoji上会有放大效果")
    print("   - 时间建议会根据当前时间自动显示")
    print("   - 推荐分类说明帮助用户理解不同类型的推荐") 