import json
import os
import base64
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time

class SmartFridgeAgent:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        self.fridge_data_file = "fridge_inventory.json"
        
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
    
    def identify_food_item(self, image_path: str) -> Dict:
        """使用Qwen VL识别食物种类"""
        try:
            base64_image = self.encode_image(image_path)
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "qwen-vl-plus",
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "image": base64_image
                                },
                                {
                                    "text": "请识别这张图片中的食物是什么，只回答食物名称，不要其他描述。"
                                }
                            ]
                        }
                    ]
                }
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                food_name = result["output"]["choices"][0]["message"]["content"]
                return {"success": True, "food_name": food_name.strip()}
            else:
                return {"success": False, "error": f"API调用失败: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_food_info(self, food_name: str) -> Dict:
        """获取食物信息（保质期、最佳温度等）"""
        # 模糊匹配食物名称
        for key in self.food_database.keys():
            if key in food_name or food_name in key:
                return {
                    "success": True,
                    "food_name": key,
                    "info": self.food_database[key]
                }
        
        # 如果没有找到匹配，返回默认值
        return {
            "success": True,
            "food_name": food_name,
            "info": {
                "shelf_life_days": 7,
                "optimal_temp": 4,
                "category": "其他"
            }
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
    
    def add_item_to_fridge(self, image_path: str) -> Dict:
        """添加物品到冰箱"""
        # 1. 识别食物
        identification_result = self.identify_food_item(image_path)
        if not identification_result["success"]:
            return {"success": False, "error": f"食物识别失败: {identification_result.get('error', '未知错误')}"}
        
        food_name = identification_result["food_name"]
        
        # 2. 获取食物信息
        food_info_result = self.get_food_info(food_name)
        food_info = food_info_result["info"]
        
        # 3. 找到最佳存储位置
        level, section = self.find_optimal_storage_location(food_info["optimal_temp"])
        
        if level == -1:
            return {"success": False, "error": "冰箱已满，没有可用空间"}
        
        # 4. 控制冰箱移动到指定位置
        self.lift(level)
        self.turn(section)
        self.fetch()
        
        # 5. 记录物品信息
        item_id = f"{food_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.fridge_data["items"][item_id] = {
            "name": food_name,
            "category": food_info["category"],
            "level": level,
            "section": section,
            "optimal_temp": food_info["optimal_temp"],
            "shelf_life_days": food_info["shelf_life_days"],
            "added_time": datetime.now().isoformat(),
            "expiry_date": (datetime.now() + timedelta(days=food_info["shelf_life_days"])).isoformat()
        }
        
        # 6. 更新层使用情况
        self.fridge_data["level_usage"][str(level)][str(section)] = True
        
        # 7. 保存数据
        self.save_fridge_data()
        
        return {
            "success": True,
            "item_id": item_id,
            "food_name": food_name,
            "level": level,
            "section": section,
            "message": f"已将 {food_name} 放入第 {level} 层第 {section} 扇区"
        }
    
    def get_item_from_fridge(self, item_id: str) -> Dict:
        """从冰箱取出物品"""
        if item_id not in self.fridge_data["items"]:
            return {"success": False, "error": "物品不存在"}
        
        item = self.fridge_data["items"][item_id]
        level = item["level"]
        section = item["section"]
        
        # 控制冰箱移动到指定位置
        self.lift(level)
        self.turn(section)
        self.fetch()
        
        # 更新数据
        self.fridge_data["level_usage"][str(level)][str(section)] = False
        del self.fridge_data["items"][item_id]
        self.save_fridge_data()
        
        return {
            "success": True,
            "item_name": item["name"],
            "message": f"已取出 {item['name']}"
        }
    
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
    
    def get_recommendations(self) -> Dict:
        """获取智能推荐"""
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
            "recommendations": recommendations,
            "total_recommendations": len(recommendations)
        }
    
    def auto_retrieve_item(self, recommendation_type: str, item_id: str) -> Dict:
        """根据推荐自动取出物品"""
        recommendations = self.get_recommendations()
        if not recommendations["success"]:
            return {"success": False, "error": "获取推荐失败"}
        
        # 查找对应的推荐
        target_recommendation = None
        for rec in recommendations["recommendations"]:
            if rec["type"] == recommendation_type:
                for item in rec["items"]:
                    if item["item_id"] == item_id:
                        target_recommendation = rec
                        break
                if target_recommendation:
                    break
        
        if not target_recommendation:
            return {"success": False, "error": "未找到对应的推荐物品"}
        
        # 取出物品
        return self.get_item_from_fridge(item_id)

def main():
    """主函数 - 演示智慧冰箱功能"""
    api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    fridge = SmartFridgeAgent(api_key)
    
    print("=== 智慧冰箱Agent启动 ===")
    
    # 演示添加物品
    print("\n1. 添加物品到冰箱")
    if os.path.exists("some_food.jpg"):
        result = fridge.add_item_to_fridge("some_food.jpg")
        print(f"添加结果: {result}")
    
    # 显示库存
    print("\n2. 查看冰箱库存")
    inventory = fridge.get_fridge_inventory()
    print(f"库存信息: {inventory}")
    
    # 获取推荐
    print("\n3. 获取智能推荐")
    recommendations = fridge.get_recommendations()
    print(f"推荐信息: {recommendations}")
    
    print("\n=== 智慧冰箱Agent演示完成 ===")

if __name__ == "__main__":
    main() 