#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧冰箱Web界面
"""

from flask import Flask, render_template, jsonify, request, Response
import json
import os
import logging
import threading
import time
from datetime import datetime
from smart_fridge_qwen import SmartFridgeQwenAgent

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
    """计算过期进度条（反向逻辑：时间越长进度条越长）"""
    try:
        expiry_date = datetime.fromisoformat(expiry_date_str)
        current_time = datetime.now()
        
        # 计算剩余天数
        remaining_days = (expiry_date - current_time).days
        
        # 检查是否为长期保存的物品（100年后过期）
        if remaining_days > 10000:  # 超过27年的物品视为长期保存
            return {
                "percentage": 100,  # 长期保存显示满进度条
                "status": "long_term",
                "color": "green",
                "text": "长期保存"
            }
        
        # 计算总保质期和剩余天数
        total_days = 7  # 假设总保质期为7天
        
        if remaining_days <= 0:
            # 已过期：不显示进度条或显示很短的红色
            return {
                "percentage": 5,  # 显示很短的进度条
                "status": "expired",
                "color": "red",
                "text": "已过期"
            }
        elif remaining_days <= 1:
            # 即将过期：显示很短的橙色进度条
            percentage = max(5, (remaining_days / total_days) * 100)
            return {
                "percentage": percentage,
                "status": "expiring_soon",
                "color": "orange",
                "text": f"剩余{remaining_days}天"
            }
        elif remaining_days <= 3:
            # 短期：显示较短的黄色进度条
            percentage = max(10, (remaining_days / total_days) * 100)
            return {
                "percentage": percentage,
                "status": "expiring_soon",
                "color": "yellow",
                "text": f"剩余{remaining_days}天"
            }
        elif remaining_days <= 5:
            # 中期：显示中等长度的蓝色进度条
            percentage = max(30, (remaining_days / total_days) * 100)
            return {
                "percentage": percentage,
                "status": "fresh",
                "color": "blue",
                "text": f"剩余{remaining_days}天"
            }
        else:
            # 长期：显示较长的绿色进度条
            percentage = max(60, (remaining_days / total_days) * 100)
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
        0: {"temp": -18, "name": "冷冻", "emoji": "🧊"},
        1: {"temp": -5, "name": "冷冻", "emoji": "🧊"},
        2: {"temp": 2, "name": "冷藏", "emoji": "❄️"},
        3: {"temp": 6, "name": "保鲜", "emoji": "🌡️"},
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
        long_term_items = len([item for item in items if item["expiry_progress"]["status"] == "long_term"])
        fresh_items = total_items - expired_items - expiring_soon - long_term_items
        
        return jsonify({
            "success": True,
            "items": items,
            "level_usage": level_usage,
            "stats": {
                "total_items": total_items,
                "expired_items": expired_items,
                "expiring_soon": expiring_soon,
                "fresh_items": fresh_items,
                "long_term_items": long_term_items
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

# 全局变量存储最新的推荐信息
latest_recommendations = {
    "success": True,
    "recommendations": [
        {
            "type": "general",
            "title": "冰箱状态良好",
            "items": [],
            "message": "冰箱中的物品状态良好，可以正常使用。",
            "action": "继续保持良好的存储习惯"
        }
    ],
    "last_update": datetime.now()
}

# 全局变量存储用户偏好
user_preferences = {
    "fruits": True,
    "vegetables": True,
    "meat": True,
    "dairy": True,
    "grains": True,
    "seafood": True,
    "desserts": True,
    "beverages": True,
    "instruments": False,
    "tools": False
}

# 全局变量存储物理按钮状态
physical_button_status = {
    "last_button_time": 0,
    "last_button_type": None,
    "last_action_result": None
}

# 全局变量存储SSE客户端
sse_clients = []

def notify_sse_clients(event_type, data):
    """通知所有SSE客户端"""
    message = f"data: {json.dumps({'type': event_type, 'data': data})}\n\n"
    for client in sse_clients[:]:  # 复制列表避免修改时出错
        try:
            client.write(message)
            client.flush()
        except:
            sse_clients.remove(client)

@app.route('/api/recommendations')
def get_recommendations():
    """获取推荐API"""
    global latest_recommendations
    
    try:
        current_time = datetime.now()
        
        # 检查是否需要更新推荐（每分钟更新一次）
        if (latest_recommendations["last_update"] is None or 
            (current_time - latest_recommendations["last_update"]).total_seconds() > 60):
            
            # 获取新的推荐
            recommendations = fridge.get_recommendations()
            latest_recommendations = {
                "success": recommendations.get("success", False),
                "recommendations": recommendations.get("recommendations", []),
                "last_update": current_time
            }
        else:
            # 如果使用缓存，更新时间戳为当前时间（保持时间显示正确）
            latest_recommendations["last_update"] = current_time
        
        # 确保返回的数据格式正确
        if not latest_recommendations.get("success", False):
            latest_recommendations["success"] = True
            if not latest_recommendations.get("recommendations"):
                latest_recommendations["recommendations"] = [
                    {
                        "type": "general",
                        "title": "冰箱状态良好",
                        "items": [],
                        "message": "冰箱中的物品状态良好，可以正常使用。",
                        "action": "继续保持良好的存储习惯"
                    }
                ]
        
        return jsonify(latest_recommendations)
    except Exception as e:
        # 如果出现异常，返回默认推荐
        return jsonify({
            "success": True,
            "recommendations": [
                {
                    "type": "general",
                    "title": "冰箱状态良好",
                    "items": [],
                    "message": "冰箱中的物品状态良好，可以正常使用。",
                    "action": "继续保持良好的存储习惯"
                }
            ],
            "last_update": current_time
        })

@app.route('/api/proximity-sensor', methods=['POST'])
def proximity_sensor():
    """接近传感器模拟API - 由人脸检测触发"""
    try:
        # 记录人脸检测事件
        logger.info("👤 检测到人脸接近 - 触发接近传感器事件")
        
        # 获取当前时间和用户偏好
        current_time = datetime.now()
        hour = current_time.hour
        weekday = current_time.weekday()  # 0=Monday, 6=Sunday
        is_workday = weekday < 5
        
        # 构建个性化推荐提示词
        time_context = ""
        if 6 <= hour < 12:
            time_context = "早上"
        elif 12 <= hour < 18:
            time_context = "下午"
        else:
            time_context = "晚上"
        
        workday_context = "工作日" if is_workday else "周末"
        
        # 获取冰箱状态
        fridge_status = fridge.get_fridge_status()
        
        # 构建个性化推荐提示词
        prompt = f"""你是一个智慧冰箱的AI助手。检测到用户接近冰箱。

当前时间：{time_context} ({workday_context})
冰箱状态：{json.dumps(fridge_status, ensure_ascii=False, indent=2)}

请根据以下因素提供个性化推荐：
1. 当前时间（{time_context}）
2. 工作日/周末（{workday_context}）
3. 即将过期的食物
4. 营养搭配建议
5. 烹饪建议

请返回简洁的JSON格式推荐，包含：
- greeting: 问候语
- main_recommendation: 主要推荐
- quick_tip: 快速提示
- urgency_level: 紧急程度（low/medium/high）

请只返回JSON格式，不要其他文字。"""

        # 使用最新的推荐信息
        global latest_recommendations
        
        # 确保有最新的推荐信息
        if (latest_recommendations["last_update"] is None or 
            (current_time - latest_recommendations["last_update"]).total_seconds() > 60):
            # 强制更新推荐
            recommendations = fridge.get_recommendations()
            latest_recommendations = {
                "success": recommendations.get("success", False),
                "recommendations": recommendations.get("recommendations", []),
                "last_update": current_time
            }
        
        # 根据最新推荐生成个性化建议
        if latest_recommendations["success"] and latest_recommendations["recommendations"]:
            # 从推荐中提取信息
            expiring_items = []
            fresh_items = []
            long_term_items = []
            
            for rec in latest_recommendations["recommendations"]:
                if rec.get("type") == "expiring_soon":
                    expiring_items.extend(rec.get("items", []))
                elif rec.get("type") == "fresh_fruits":
                    fresh_items.extend(rec.get("items", []))
                elif rec.get("type") == "long_term":
                    long_term_items.extend(rec.get("items", []))
            
            # 根据时间生成个性化问候和建议
            current_hour = current_time.hour
            if current_hour < 12:
                greeting = "早上好！"
                if expiring_items:
                    main_recommendation = f"有{len(expiring_items)}个物品即将过期，建议优先食用"
                    urgency_level = "high"
                elif fresh_items:
                    main_recommendation = "冰箱里有新鲜水果，是早餐的好选择"
                    urgency_level = "low"
                else:
                    main_recommendation = "冰箱状态良好，可以开始新的一天"
                    urgency_level = "low"
                quick_tip = "建议搭配水果和蛋白质，营养更均衡"
                
            elif current_hour < 18:
                greeting = "下午好！"
                if expiring_items:
                    main_recommendation = f"有{len(expiring_items)}个物品需要尽快处理"
                    urgency_level = "medium"
                else:
                    main_recommendation = "下午茶时间，可以享用冰箱里的新鲜食物"
                    urgency_level = "low"
                quick_tip = "注意检查食物保质期，避免浪费"
                
            else:
                greeting = "晚上好！"
                if expiring_items:
                    main_recommendation = f"有{len(expiring_items)}个物品明天可能过期"
                    urgency_level = "high"
                else:
                    main_recommendation = "冰箱状态良好，可以安心休息"
                    urgency_level = "low"
                quick_tip = "建议整理冰箱，为明天做准备"
        else:
            # 如果没有推荐信息，使用默认建议
            if current_hour < 12:
                greeting = "早上好！"
                main_recommendation = "建议食用新鲜水果补充维生素"
                quick_tip = "苹果富含纤维，是早餐的好选择"
                urgency_level = "low"
            elif current_hour < 18:
                greeting = "下午好！"
                main_recommendation = "三明治即将过期，建议尽快食用"
                quick_tip = "可以搭配水果制作营养午餐"
                urgency_level = "medium"
            else:
                greeting = "晚上好！"
                main_recommendation = "注意检查过期食物"
                quick_tip = "建议清理即将过期的食物"
                urgency_level = "high"
        
        recommendation = {
            "greeting": greeting,
            "main_recommendation": main_recommendation,
            "quick_tip": quick_tip,
            "urgency_level": urgency_level
        }
        
        return jsonify({
            "success": True,
            "recommendation": recommendation,
            "time_context": time_context,
            "workday_context": workday_context
        })
            
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/place-item', methods=['POST'])
def place_item():
    """放置物品API"""
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": "没有上传文件"
            })
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "没有选择文件"
            })
        
        # 保存上传的文件
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # 生成唯一文件名
        import uuid
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        image_path = os.path.join(upload_dir, unique_filename)
        
        # 保存文件
        file.save(image_path)
        
        # 调用冰箱Agent添加物品
        result = fridge.add_item_to_fridge(image_path)
        
        # 更新物理按钮状态
        global physical_button_status
        physical_button_status["last_action_result"] = result
        
        # 通知SSE客户端操作完成
        notify_sse_clients('action_completed', result)
        
        # 调试：不清理临时文件，保留图片用于检查
        logger.info(f"🔍 保留临时图片文件用于调试: {image_path}")
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/take-out', methods=['POST'])
def take_out():
    """取出物品API"""
    try:
        data = request.get_json()
        item_id = data.get('item_id')
        
        if not item_id:
            return jsonify({
                "success": False,
                "error": "缺少物品ID"
            })
        
        # 调用冰箱Agent取出物品
        result = fridge.get_item_from_fridge(item_id)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/physical-button-status', methods=['GET'])
def get_physical_button_status():
    """获取物理按钮状态API"""
    global physical_button_status
    return jsonify({
        "success": True,
        "last_button_time": physical_button_status["last_button_time"],
        "last_button_type": physical_button_status["last_button_type"],
        "last_action_result": physical_button_status["last_action_result"],
        "button_type": physical_button_status["last_button_type"],
        "action_result": physical_button_status["last_action_result"]
    })

@app.route('/api/events')
def sse():
    """Server-Sent Events端点"""
    def generate():
        # 发送连接确认
        yield f"data: {json.dumps({'type': 'connected', 'data': {'message': 'SSE连接已建立'}})}\n\n"
        
        # 将客户端添加到列表
        sse_clients.append(request.environ['wsgi.input'].stream)
        
        try:
            while True:
                # 保持连接活跃
                yield f"data: {json.dumps({'type': 'ping', 'data': {'timestamp': time.time()}})}\n\n"
                time.sleep(30)  # 每30秒发送一次ping
        except:
            # 客户端断开连接
            if request.environ['wsgi.input'].stream in sse_clients:
                sse_clients.remove(request.environ['wsgi.input'].stream)
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/physical-button', methods=['POST'])
def physical_button():
    """物理按键API - 处理物理按键触发"""
    global physical_button_status
    
    try:
        data = request.get_json()
        button_type = data.get('button_type')  # 'place' 或 'take_out'
        
        # 更新物理按钮状态
        import time
        physical_button_status["last_button_time"] = int(time.time() * 1000)
        physical_button_status["last_button_type"] = button_type
        
        # 通知SSE客户端按钮被按下
        notify_sse_clients('button_pressed', {
            'button_type': button_type,
            'timestamp': physical_button_status["last_button_time"]
        })
        
        if button_type == 'place':
            # 处理放入物品
            logger.info("物理按键触发：放入物品")
            
            # 获取冰箱状态
            inventory_result = fridge.get_fridge_inventory()
            if not inventory_result["success"]:
                return jsonify({
                    "success": False,
                    "error": "获取冰箱状态失败"
                })
            
            # 检查冰箱是否已满
            total_items = inventory_result["total_items"]
            max_capacity = 20  # 假设最大容量为20个物品
            
            if total_items >= max_capacity:
                return jsonify({
                    "success": False,
                    "message": "冰箱已满，请先清理一些物品",
                    "action": "place_item",
                    "current_items": total_items,
                    "max_capacity": max_capacity
                })
            
            # 更新物理按钮状态
            physical_button_status["last_action_result"] = {
                "success": True,
                "message": "请将要放入的物品放在摄像头前，系统将自动识别并存储",
                "action": "place_item",
                "current_items": total_items,
                "max_capacity": max_capacity,
                "available_space": max_capacity - total_items
            }
            
            # 返回放入物品的指导信息
            return jsonify({
                "success": True,
                "message": "请将要放入的物品放在摄像头前，系统将自动识别并存储",
                "action": "place_item",
                "current_items": total_items,
                "max_capacity": max_capacity,
                "available_space": max_capacity - total_items
            })
            
        elif button_type == 'take_out':
            # 处理取出物品
            logger.info("物理按键触发：取出物品")
            
            # 获取冰箱状态
            inventory_result = fridge.get_fridge_inventory()
            if not inventory_result["success"]:
                return jsonify({
                    "success": False,
                    "error": "获取冰箱状态失败"
                })
            
            # 查找即将过期的物品
            expiring_items = []
            expired_items = []
            fresh_items = []
            
            for item in inventory_result["inventory"]:
                if item.get("is_expired"):
                    expired_items.append(item)
                elif item.get("days_remaining", 0) <= 2:
                    expiring_items.append(item)
                else:
                    fresh_items.append(item)
            
            # 优先取出已过期的物品
            if expired_items:
                item_to_take = expired_items[0]
                result = fridge.get_item_from_fridge(item_to_take["item_id"])
                
                # 更新物理按钮状态
                action_result = {
                    "success": True,
                    "message": f"已取出已过期的物品：{item_to_take['name']}",
                    "action": "take_out_item",
                    "item": item_to_take,
                    "priority": "expired",
                    "result": result
                }
                physical_button_status["last_action_result"] = action_result
                
                # 通知SSE客户端操作完成
                notify_sse_clients('action_completed', action_result)
                
                return jsonify(action_result)
            
            # 其次取出即将过期的物品
            elif expiring_items:
                item_to_take = expiring_items[0]
                result = fridge.get_item_from_fridge(item_to_take["item_id"])
                
                # 更新物理按钮状态
                physical_button_status["last_action_result"] = {
                    "success": True,
                    "message": f"已取出即将过期的物品：{item_to_take['name']}（剩余{item_to_take['days_remaining']}天）",
                    "action": "take_out_item",
                    "item": item_to_take,
                    "priority": "expiring_soon",
                    "result": result
                }
                
                return jsonify({
                    "success": True,
                    "message": f"已取出即将过期的物品：{item_to_take['name']}（剩余{item_to_take['days_remaining']}天）",
                    "action": "take_out_item",
                    "item": item_to_take,
                    "priority": "expiring_soon",
                    "result": result
                })
            
            # 如果没有过期或即将过期的物品，取出最老的物品
            elif fresh_items:
                # 按添加时间排序，取出最老的物品
                fresh_items.sort(key=lambda x: x.get("added_time", ""))
                item_to_take = fresh_items[0]
                result = fridge.get_item_from_fridge(item_to_take["item_id"])
                
                # 更新物理按钮状态
                physical_button_status["last_action_result"] = {
                    "success": True,
                    "message": f"已取出物品：{item_to_take['name']}（剩余{item_to_take['days_remaining']}天）",
                    "action": "take_out_item",
                    "item": item_to_take,
                    "priority": "oldest",
                    "result": result
                }
                
                return jsonify({
                    "success": True,
                    "message": f"已取出物品：{item_to_take['name']}（剩余{item_to_take['days_remaining']}天）",
                    "action": "take_out_item",
                    "item": item_to_take,
                    "priority": "oldest",
                    "result": result
                })
            
            else:
                # 更新物理按钮状态
                physical_button_status["last_action_result"] = {
                    "success": True,
                    "message": "冰箱中没有物品需要取出",
                    "action": "take_out_item",
                    "item": None,
                    "priority": "empty"
                }
                
                return jsonify({
                    "success": True,
                    "message": "冰箱中没有物品需要取出",
                    "action": "take_out_item",
                    "item": None,
                    "priority": "empty"
                })
        else:
            return jsonify({
                "success": False,
                "error": "无效的按键类型"
            })
            
    except Exception as e:
        logger.error(f"物理按键处理失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/user-preferences', methods=['GET', 'POST'])
def user_preferences_api():
    """用户偏好设置API"""
    global user_preferences
    
    if request.method == 'GET':
        return jsonify({
            "success": True,
            "preferences": user_preferences
        })
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            user_preferences.update(data)
            return jsonify({
                "success": True,
                "message": "偏好设置已更新",
                "preferences": user_preferences
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

@app.route('/api/time-advice', methods=['GET'])
def get_time_advice():
    """获取基于大模型的时间建议"""
    try:
        current_time = datetime.now()
        hour = current_time.hour
        weekday = current_time.weekday()
        is_workday = weekday < 5
        
        # 获取冰箱状态
        fridge_status = fridge.get_fridge_status()
        
        # 构建时间建议提示词
        time_context = ""
        if 6 <= hour < 12:
            time_context = "早上"
        elif 12 <= hour < 18:
            time_context = "下午"
        else:
            time_context = "晚上"
        
        workday_context = "工作日" if is_workday else "周末"
        
        # 构建大模型提示词
        system_prompt = f"""你是一个智慧冰箱的AI助手。用户想要获取基于当前时间和冰箱内容的个性化时间建议。

当前时间：{time_context} ({workday_context})
用户偏好：{json.dumps(user_preferences, ensure_ascii=False, indent=2)}
冰箱状态：{json.dumps(fridge_status, ensure_ascii=False, indent=2)}

请根据以下因素提供个性化时间建议：
1. 当前时间段（{time_context}）
2. 工作日/周末（{workday_context}）
3. 用户的食物偏好
4. 冰箱中的物品状态
5. 即将过期的食物
6. 营养搭配建议
7. 烹饪建议

请返回JSON格式的时间建议，包含：
- greeting: 问候语
- main_advice: 主要建议
- nutrition_tips: 营养提示（2-3条）
- cooking_suggestions: 烹饪建议（2-3条）
- urgency_level: 紧急程度（low/medium/high）

请只返回JSON格式的结果，不要其他文字。"""

        # 调用大模型获取时间建议
        result = fridge.call_qwen_vl("some_food.jpg", system_prompt)
        
        if result["success"]:
            try:
                response_text = result["response"]
                # 提取JSON部分
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_str = response_text[start_idx:end_idx]
                    time_advice = json.loads(json_str)
                    
                    return jsonify({
                        "success": True,
                        "time_advice": time_advice,
                        "time_context": time_context,
                        "workday_context": workday_context
                    })
                else:
                    # 如果大模型调用失败，使用默认建议
                    return get_default_time_advice(time_context, workday_context)
                    
            except json.JSONDecodeError:
                # 如果JSON解析失败，使用默认建议
                return get_default_time_advice(time_context, workday_context)
        else:
            # 如果API调用失败，使用默认建议
            return get_default_time_advice(time_context, workday_context)
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

def get_default_time_advice(time_context, workday_context):
    """获取默认时间建议"""
    if time_context == "早上":
        advice = {
            "greeting": "早上好！",
            "main_advice": "建议食用新鲜水果补充维生素",
            "nutrition_tips": [
                "🍎 苹果富含纤维，是早餐的好选择",
                "🥛 搭配蛋白质，营养更均衡",
                "🥚 鸡蛋提供优质蛋白质"
            ],
            "cooking_suggestions": [
                "可以制作水果沙拉",
                "搭配牛奶和谷物",
                "准备简单的三明治"
            ],
            "urgency_level": "low"
        }
    elif time_context == "下午":
        advice = {
            "greeting": "下午好！",
            "main_advice": "下午茶时间，可以享用冰箱里的新鲜食物",
            "nutrition_tips": [
                "☕ 可以搭配茶或咖啡",
                "🍎 水果是下午茶的好选择",
                "🥪 简单的三明治或沙拉"
            ],
            "cooking_suggestions": [
                "制作简单的三明治",
                "准备水果拼盘",
                "可以尝试小点心"
            ],
            "urgency_level": "medium"
        }
    else:
        advice = {
            "greeting": "晚上好！",
            "main_advice": "建议整理冰箱，为明天做准备",
            "nutrition_tips": [
                "🌙 注意检查食物保质期",
                "🧹 清理即将过期的食物",
                "📝 可以列出明天的购物清单"
            ],
            "cooking_suggestions": [
                "准备明天的早餐",
                "整理冰箱物品",
                "计划明天的菜单"
            ],
            "urgency_level": "high"
        }
    
    return jsonify({
        "success": True,
        "time_advice": advice,
        "time_context": time_context,
        "workday_context": workday_context
    })

if __name__ == '__main__':
    # 创建templates目录
    os.makedirs('templates', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=8080) 