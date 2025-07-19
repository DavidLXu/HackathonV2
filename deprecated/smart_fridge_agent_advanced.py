import json
import os
import base64
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time

class AdvancedSmartFridgeAgent:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        self.fridge_data_file = "fridge_inventory_advanced.json"
        
        # 冰箱配置
        self.total_levels = 5  # 5层
        self.sections_per_level = 4  # 每层4个扇区
        self.temperature_levels = {
            0: 2,    # 最底层：2°C (冷冻)
            1: 4,    # 第二层：4°C (冷藏)
            2: 6,    # 第三层：6°C (冷藏)
            3: 8,    # 第四层：8°C (冷藏)
            4: 10    # 最顶层：10°C (冷藏)
        }
        
        # 加载冰箱数据
        self.fridge_data = self.load_fridge_data()
        
        # 物品保质期和最佳温度数据库
        self.food_database = {
            "苹果": {"shelf_life_days": 14, "optimal_temp": 4, "category": "水果"},
            "香蕉": {"shelf_life_days": 7, "optimal_temp": 8, "category": "水果"},
            "橙子": {"shelf_life_days": 21, "optimal_temp": 4, "category": "水果"},
            "牛奶": {"shelf_life_days": 7, "optimal_temp": 4, "category": "乳制品"},
            "酸奶": {"shelf_life_days": 14, "optimal_temp": 4, "category": "乳制品"},
            "鸡蛋": {"shelf_life_days": 30, "optimal_temp": 4, "category": "蛋类"},
            "面包": {"shelf_life_days": 7, "optimal_temp": 4, "category": "面包"},
            "蔬菜": {"shelf_life_days": 7, "optimal_temp": 4, "category": "蔬菜"},
            "肉类": {"shelf_life_days": 3, "optimal_temp": 2, "category": "肉类"},
            "鱼类": {"shelf_life_days": 2, "optimal_temp": 2, "category": "海鲜"},
            "奶酪": {"shelf_life_days": 21, "optimal_temp": 4, "category": "乳制品"},
            "黄油": {"shelf_life_days": 30, "optimal_temp": 4, "category": "乳制品"},
            "番茄": {"shelf_life_days": 7, "optimal_temp": 8, "category": "蔬菜"},
            "胡萝卜": {"shelf_life_days": 14, "optimal_temp": 4, "category": "蔬菜"},
            "洋葱": {"shelf_life_days": 30, "optimal_temp": 8, "category": "蔬菜"},
            "土豆": {"shelf_life_days": 30, "optimal_temp": 8, "category": "蔬菜"},
            "青椒": {"shelf_life_days": 7, "optimal_temp": 8, "category": "蔬菜"},
            "黄瓜": {"shelf_life_days": 7, "optimal_temp": 8, "category": "蔬菜"},
            "生菜": {"shelf_life_days": 7, "optimal_temp": 4, "category": "蔬菜"},
            "草莓": {"shelf_life_days": 5, "optimal_temp": 4, "category": "水果"},
            "葡萄": {"shelf_life_days": 7, "optimal_temp": 4, "category": "水果"},
            "西瓜": {"shelf_life_days": 7, "optimal_temp": 8, "category": "水果"},
            "橙汁": {"shelf_life_days": 7, "optimal_temp": 4, "category": "饮料"},
            "可乐": {"shelf_life_days": 30, "optimal_temp": 4, "category": "饮料"},
            "啤酒": {"shelf_life_days": 30, "optimal_temp": 4, "category": "饮料"},
            "巧克力": {"shelf_life_days": 180, "optimal_temp": 8, "category": "零食"},
            "冰淇淋": {"shelf_life_days": 30, "optimal_temp": 2, "category": "冷冻食品"},
            "饺子": {"shelf_life_days": 7, "optimal_temp": 2, "category": "冷冻食品"},
            "汤圆": {"shelf_life_days": 30, "optimal_temp": 2, "category": "冷冻食品"}
        }
    
    def load_fridge_data(self) -> Dict:
        """加载冰箱库存数据"""
        if os.path.exists(self.fridge_data_file):
            try:
                with open(self.fridge_data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self.initialize_fridge_data()
        else:
            return self.initialize_fridge_data()
    
    def initialize_fridge_data(self) -> Dict:
        """初始化冰箱数据结构"""
        data = {
            "items": {},
            "level_usage": {},
            "last_update": datetime.now().isoformat()
        }
        
        # 初始化每层的使用情况
        for level in range(self.total_levels):
            data["level_usage"][str(level)] = {
                str(section): False for section in range(self.sections_per_level)
            }
        
        return data
    
    def save_fridge_data(self):
        """保存冰箱数据"""
        self.fridge_data["last_update"] = datetime.now().isoformat()
        with open(self.fridge_data_file, 'w', encoding='utf-8') as f:
            json.dump(self.fridge_data, f, ensure_ascii=False, indent=2)
    
    def lift(self, level_index: int):
        """控制圆形平台上升到指定层"""
        if 0 <= level_index < self.total_levels:
            print(f"reached level {level_index}")
            return True
        else:
            print(f"Invalid level index: {level_index}")
            return False
    
    def turn(self, section_index: int):
        """控制圆形平台旋转到指定扇区"""
        if 0 <= section_index < self.sections_per_level:
            print(f"turned to section {section_index}")
            return True
        else:
            print(f"Invalid section index: {section_index}")
            return False
    
    def fetch(self):
        """控制机械臂取物"""
        print("fetched object")
        return True
    
    def encode_image(self, image_path: str) -> str:
        """将图片编码为base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def get_fridge_status(self) -> Dict:
        """获取冰箱当前状态"""
        current_time = datetime.now()
        inventory = []
        
        for item_id, item in self.fridge_data["items"].items():
            expiry_date = datetime.fromisoformat(item["expiry_date"])
            days_remaining = (expiry_date - current_time).days
            
            inventory.append({
                "item_id": item_id,
                "name": item["name"],
                "category": item["category"],
                "level": item["level"],
                "section": item["section"],
                "days_remaining": max(0, days_remaining),
                "is_expired": days_remaining < 0,
                "optimal_temp": item["optimal_temp"]
            })
        
        return {
            "inventory": inventory,
            "total_items": len(inventory),
            "temperature_levels": self.temperature_levels,
            "food_database": self.food_database
        }
    
    def call_qwen_with_functions(self, image_path: str, user_message: str) -> Dict:
        """使用Qwen VL的function calling能力"""
        try:
            base64_image = self.encode_image(image_path)
            fridge_status = self.get_fridge_status()
            
            # 定义可用的函数
            functions = [
                {
                    "name": "lift",
                    "description": "控制圆形平台上升到指定层",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "level_index": {
                                "type": "integer",
                                "description": "目标层数 (0-4)",
                                "minimum": 0,
                                "maximum": 4
                            }
                        },
                        "required": ["level_index"]
                    }
                },
                {
                    "name": "turn",
                    "description": "控制圆形平台旋转到指定扇区",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "section_index": {
                                "type": "integer",
                                "description": "目标扇区 (0-3)",
                                "minimum": 0,
                                "maximum": 3
                            }
                        },
                        "required": ["section_index"]
                    }
                },
                {
                    "name": "fetch",
                    "description": "控制机械臂取物",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "add_item_to_fridge",
                    "description": "将识别到的物品添加到冰箱",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "food_name": {
                                "type": "string",
                                "description": "食物名称"
                            },
                            "optimal_temp": {
                                "type": "integer",
                                "description": "最佳存储温度"
                            },
                            "shelf_life_days": {
                                "type": "integer",
                                "description": "保质期天数"
                            },
                            "category": {
                                "type": "string",
                                "description": "食物类别"
                            }
                        },
                        "required": ["food_name", "optimal_temp", "shelf_life_days", "category"]
                    }
                },
                {
                    "name": "get_recommendations",
                    "description": "获取智能推荐",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            ]
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 构建系统提示词
            system_prompt = f"""你是一个智慧冰箱的AI助手。你的任务是帮助用户管理冰箱中的食物。

冰箱配置：
- 5层，每层4个扇区
- 温度分布：第0层2°C(冷冻)，第1层4°C(冷藏)，第2层6°C(冷藏)，第3层8°C(冷藏)，第4层10°C(冷藏)

当前冰箱状态：
{json.dumps(fridge_status, ensure_ascii=False, indent=2)}

食物数据库：
{json.dumps(self.food_database, ensure_ascii=False, indent=2)}

你的职责：
1. 识别用户放入的食物图片
2. 根据食物的最佳存储温度，选择合适的冰箱层和扇区
3. 控制冰箱的机械臂进行取放操作
4. 提供智能推荐，包括即将过期的食物、新鲜水果、烹饪建议等
5. 维护冰箱库存记录

请根据用户的需求和图片内容，调用相应的函数来完成任务。"""
            
            payload = {
                "model": "qwen-vl-plus",
                "input": {
                    "messages": [
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "image": base64_image
                                },
                                {
                                    "text": user_message
                                }
                            ]
                        }
                    ],
                    "functions": functions,
                    "function_call": "auto"
                }
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                return {"success": True, "result": result}
            else:
                return {"success": False, "error": f"API调用失败: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def process_user_request(self, image_path: str, user_message: str) -> Dict:
        """处理用户请求"""
        # 调用Qwen VL进行智能处理
        qwen_result = self.call_qwen_with_functions(image_path, user_message)
        
        if not qwen_result["success"]:
            return qwen_result
        
        result = qwen_result["result"]
        
        # 处理function calling结果
        if "output" in result and "choices" in result["output"]:
            choice = result["output"]["choices"][0]
            
            if "message" in choice and "function_call" in choice["message"]:
                function_call = choice["message"]["function_call"]
                function_name = function_call["name"]
                arguments = json.loads(function_call["arguments"])
                
                # 执行对应的函数
                if function_name == "lift":
                    return self.execute_lift(arguments)
                elif function_name == "turn":
                    return self.execute_turn(arguments)
                elif function_name == "fetch":
                    return self.execute_fetch()
                elif function_name == "add_item_to_fridge":
                    return self.execute_add_item(arguments)
                elif function_name == "get_recommendations":
                    return self.execute_get_recommendations()
                else:
                    return {"success": False, "error": f"未知函数: {function_name}"}
            else:
                # 返回文本回复
                return {
                    "success": True,
                    "type": "text_response",
                    "message": choice["message"]["content"]
                }
        
        return {"success": False, "error": "无法解析API响应"}
    
    def execute_lift(self, arguments: Dict) -> Dict:
        """执行lift函数"""
        level_index = arguments.get("level_index")
        success = self.lift(level_index)
        return {
            "success": success,
            "action": "lift",
            "level": level_index,
            "message": f"平台已移动到第 {level_index} 层"
        }
    
    def execute_turn(self, arguments: Dict) -> Dict:
        """执行turn函数"""
        section_index = arguments.get("section_index")
        success = self.turn(section_index)
        return {
            "success": success,
            "action": "turn",
            "section": section_index,
            "message": f"平台已旋转到第 {section_index} 扇区"
        }
    
    def execute_fetch(self) -> Dict:
        """执行fetch函数"""
        success = self.fetch()
        return {
            "success": success,
            "action": "fetch",
            "message": "机械臂已完成取物操作"
        }
    
    def execute_add_item(self, arguments: Dict) -> Dict:
        """执行add_item_to_fridge函数"""
        food_name = arguments.get("food_name")
        optimal_temp = arguments.get("optimal_temp")
        shelf_life_days = arguments.get("shelf_life_days")
        category = arguments.get("category")
        
        # 找到最佳存储位置
        level, section = self.find_optimal_storage_location(optimal_temp)
        
        if level == -1:
            return {"success": False, "error": "冰箱已满，没有可用空间"}
        
        # 控制冰箱移动到指定位置
        self.lift(level)
        self.turn(section)
        self.fetch()
        
        # 记录物品信息
        item_id = f"{food_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.fridge_data["items"][item_id] = {
            "name": food_name,
            "category": category,
            "level": level,
            "section": section,
            "optimal_temp": optimal_temp,
            "shelf_life_days": shelf_life_days,
            "added_time": datetime.now().isoformat(),
            "expiry_date": (datetime.now() + timedelta(days=shelf_life_days)).isoformat()
        }
        
        # 更新层使用情况
        self.fridge_data["level_usage"][str(level)][str(section)] = True
        
        # 保存数据
        self.save_fridge_data()
        
        return {
            "success": True,
            "action": "add_item",
            "item_id": item_id,
            "food_name": food_name,
            "level": level,
            "section": section,
            "message": f"已将 {food_name} 放入第 {level} 层第 {section} 扇区"
        }
    
    def execute_get_recommendations(self) -> Dict:
        """执行get_recommendations函数"""
        inventory_result = self.get_fridge_inventory()
        if not inventory_result["success"]:
            return inventory_result
        
        inventory = inventory_result["inventory"]
        recommendations = []
        
        # 推荐即将过期的物品
        expiring_soon = [item for item in inventory if 0 <= item["days_remaining"] <= 2]
        if expiring_soon:
            recommendations.append({
                "type": "expiring_soon",
                "title": "即将过期的物品",
                "items": expiring_soon,
                "message": "以下物品即将过期，建议尽快食用"
            })
        
        # 推荐已过期的物品
        expired = [item for item in inventory if item["is_expired"]]
        if expired:
            recommendations.append({
                "type": "expired",
                "title": "已过期的物品",
                "items": expired,
                "message": "以下物品已过期，建议丢弃"
            })
        
        # 推荐新鲜水果
        fresh_fruits = [item for item in inventory 
                       if item["category"] == "水果" and item["days_remaining"] > 3]
        if fresh_fruits:
            recommendations.append({
                "type": "fresh_fruits",
                "title": "新鲜水果",
                "items": fresh_fruits,
                "message": "冰箱里有新鲜水果，可以享用"
            })
        
        # 推荐适合烹饪的食材组合
        vegetables = [item for item in inventory if item["category"] == "蔬菜"]
        meats = [item for item in inventory if item["category"] == "肉类"]
        
        if vegetables and meats:
            recommendations.append({
                "type": "cooking_suggestion",
                "title": "烹饪建议",
                "items": vegetables + meats,
                "message": "您有蔬菜和肉类，可以制作美味的菜肴"
            })
        
        return {
            "success": True,
            "action": "get_recommendations",
            "recommendations": recommendations,
            "total_recommendations": len(recommendations)
        }
    
    def find_optimal_storage_location(self, optimal_temp: int) -> Tuple[int, int]:
        """根据最佳温度找到最优存储位置"""
        # 找到温度最接近的层
        best_level = min(self.temperature_levels.keys(), 
                        key=lambda x: abs(self.temperature_levels[x] - optimal_temp))
        
        # 在该层找到空闲的扇区
        level_str = str(best_level)
        if level_str in self.fridge_data["level_usage"]:
            for section in range(self.sections_per_level):
                if not self.fridge_data["level_usage"][level_str][str(section)]:
                    return best_level, section
        
        # 如果最优层没有空间，寻找其他层
        for level in range(self.total_levels):
            level_str = str(level)
            if level_str in self.fridge_data["level_usage"]:
                for section in range(self.sections_per_level):
                    if not self.fridge_data["level_usage"][level_str][str(section)]:
                        return level, section
        
        return -1, -1  # 没有可用空间
    
    def get_fridge_inventory(self) -> Dict:
        """获取冰箱库存"""
        current_time = datetime.now()
        inventory = []
        
        for item_id, item in self.fridge_data["items"].items():
            expiry_date = datetime.fromisoformat(item["expiry_date"])
            days_remaining = (expiry_date - current_time).days
            
            inventory.append({
                "item_id": item_id,
                "name": item["name"],
                "category": item["category"],
                "level": item["level"],
                "section": item["section"],
                "days_remaining": max(0, days_remaining),
                "is_expired": days_remaining < 0
            })
        
        return {
            "success": True,
            "inventory": inventory,
            "total_items": len(inventory)
        }

def main():
    """主函数 - 演示高级智慧冰箱功能"""
    api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    fridge = AdvancedSmartFridgeAgent(api_key)
    
    print("=== 高级智慧冰箱Agent启动 ===")
    
    # 演示添加物品
    print("\n1. 添加物品到冰箱")
    if os.path.exists("some_food.jpg"):
        result = fridge.process_user_request("some_food.jpg", "请帮我将这个食物放入冰箱")
        print(f"处理结果: {result}")
    
    # 获取推荐
    print("\n2. 获取智能推荐")
    result = fridge.process_user_request("some_food.jpg", "请给我一些关于冰箱内容的建议")
    print(f"推荐结果: {result}")
    
    print("\n=== 高级智慧冰箱Agent演示完成 ===")

if __name__ == "__main__":
    main() 