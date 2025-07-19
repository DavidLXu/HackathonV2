#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧冰箱Web界面
"""

from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime
from smart_fridge_qwen import SmartFridgeQwenAgent

app = Flask(__name__)
fridge = SmartFridgeQwenAgent()

# 食物emoji映射
FOOD_EMOJIS = {
    "苹果": "🍎",
    "香蕉": "🍌", 
    "橙子": "🍊",
    "草莓": "🍓",
    "葡萄": "🍇",
    "西瓜": "🍉",
    "牛奶": "🥛",
    "酸奶": "🥛",
    "奶酪": "🧀",
    "鸡蛋": "🥚",
    "面包": "🍞",
    "三明治": "🥪",
    "肉类": "🥩",
    "鱼类": "🐟",
    "蔬菜": "🥬",
    "胡萝卜": "🥕",
    "番茄": "🍅",
    "洋葱": "🧅",
    "土豆": "🥔",
    "青椒": "🫑",
    "黄瓜": "🥒",
    "生菜": "🥬",
    "冰淇淋": "🍦",
    "饺子": "🥟",
    "汤圆": "🥟",
    "橙汁": "🧃",
    "可乐": "🥤",
    "啤酒": "🍺",
    "巧克力": "🍫",
    "黄油": "🧈",
    "小提琴": "🎻",
    "乐器": "🎻",
    "熟食": "🍱",
    "水果": "🍎",
    "乳制品": "🥛",
    "蛋类": "🥚",
    "海鲜": "🐟",
    "饮料": "🥤",
    "零食": "🍿",
    "冷冻食品": "🧊",
    "其他": "📦"
}

def get_food_emoji(food_name, category):
    """获取食物的emoji"""
    # 优先使用具体食物名称的emoji
    if food_name in FOOD_EMOJIS:
        return FOOD_EMOJIS[food_name]
    
    # 如果没有具体食物名称，使用类别emoji
    if category in FOOD_EMOJIS:
        return FOOD_EMOJIS[category]
    
    return FOOD_EMOJIS["其他"]

def calculate_expiry_progress(expiry_date_str):
    """计算过期进度条"""
    try:
        expiry_date = datetime.fromisoformat(expiry_date_str)
        current_time = datetime.now()
        
        # 计算总保质期和剩余天数
        total_days = 7  # 假设总保质期为7天
        remaining_days = (expiry_date - current_time).days
        
        if remaining_days <= 0:
            # 已过期
            return {
                "percentage": 100,
                "status": "expired",
                "color": "red",
                "text": "已过期"
            }
        elif remaining_days <= 2:
            # 即将过期
            percentage = max(0, 100 - (remaining_days / total_days) * 100)
            return {
                "percentage": percentage,
                "status": "expiring_soon",
                "color": "orange",
                "text": f"剩余{remaining_days}天"
            }
        else:
            # 新鲜
            percentage = max(0, 100 - (remaining_days / total_days) * 100)
            return {
                "percentage": percentage,
                "status": "fresh",
                "color": "green",
                "text": f"剩余{remaining_days}天"
            }
    except:
        return {
            "percentage": 0,
            "status": "unknown",
            "color": "gray",
            "text": "未知"
        }

def get_temperature_info(level):
    """获取温度信息"""
    temperature_levels = {
        0: {"temp": 2, "name": "冷冻", "emoji": "🧊"},
        1: {"temp": 4, "name": "冷藏", "emoji": "❄️"},
        2: {"temp": 6, "name": "保鲜", "emoji": "🌡️"},
        3: {"temp": 8, "name": "保鲜", "emoji": "🌡️"},
        4: {"temp": 10, "name": "常温", "emoji": "🌡️"}
    }
    return temperature_levels.get(level, {"temp": 0, "name": "未知", "emoji": "❓"})

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/fridge-status')
def get_fridge_status():
    """获取冰箱状态API"""
    try:
        # 获取冰箱库存
        inventory_result = fridge.get_fridge_inventory()
        
        if not inventory_result["success"]:
            return jsonify({"error": "获取库存失败"})
        
        # 处理库存数据
        items = []
        for item in inventory_result["inventory"]:
            emoji = get_food_emoji(item["name"], item["category"])
            expiry_progress = calculate_expiry_progress(
                fridge.fridge_data["items"][item["item_id"]]["expiry_date"]
            )
            temp_info = get_temperature_info(item["level"])
            
            items.append({
                "id": item["item_id"],
                "name": item["name"],
                "emoji": emoji,
                "category": item["category"],
                "level": item["level"],
                "section": item["section"],
                "temp_info": temp_info,
                "days_remaining": item["days_remaining"],
                "is_expired": item["is_expired"],
                "expiry_progress": expiry_progress
            })
        
        # 获取层使用情况
        level_usage = fridge.fridge_data["level_usage"]
        
        # 计算统计信息
        total_items = len(items)
        expired_items = len([item for item in items if item["is_expired"]])
        expiring_soon = len([item for item in items if item["expiry_progress"]["status"] == "expiring_soon"])
        
        return jsonify({
            "success": True,
            "items": items,
            "level_usage": level_usage,
            "stats": {
                "total_items": total_items,
                "expired_items": expired_items,
                "expiring_soon": expiring_soon,
                "fresh_items": total_items - expired_items - expiring_soon
            },
            "temperature_levels": fridge.temperature_levels
        })
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/add-item', methods=['POST'])
def add_item():
    """添加物品API"""
    try:
        # 这里可以处理文件上传
        # 暂时返回模拟数据
        return jsonify({
            "success": True,
            "message": "物品添加成功"
        })
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/recommendations')
def get_recommendations():
    """获取推荐API"""
    try:
        recommendations = fridge.get_recommendations()
        return jsonify(recommendations)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    # 创建templates目录
    os.makedirs('templates', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=8080) 