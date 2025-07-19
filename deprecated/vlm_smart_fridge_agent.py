import json
import os
import datetime
import base64
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import dashscope
from dashscope import MultiModalConversation

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set your DashScope API Key here
dashscope.api_key = 'sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

class TemperatureZone(Enum):
    FREEZER = "freezer"  # 冷冻层 (-18°C)
    COLD = "cold"        # 冷藏层 (0-4°C)
    COOL = "cool"        # 保鲜层 (4-8°C)
    ROOM = "room"        # 常温层 (8-15°C)

@dataclass
class FoodItem:
    name: str
    category: str
    storage_time: datetime.datetime
    expiry_days: int
    level: int
    section: int
    temperature_zone: TemperatureZone
    quantity: str = "1"
    notes: str = ""

class VLMSmartFridgeAgent:
    def __init__(self, storage_file: str = "fridge_inventory.json"):
        self.storage_file = storage_file
        self.inventory: Dict[str, FoodItem] = {}
        self.user_preferences: Dict[str, List[str]] = {}
        self.load_inventory()
        
        # 冰箱配置
        self.total_levels = 5
        self.sections_per_level = 4
        self.temperature_zones = {
            0: TemperatureZone.FREEZER,   # 底层冷冻
            1: TemperatureZone.COLD,      # 冷藏
            2: TemperatureZone.COLD,      # 冷藏
            3: TemperatureZone.COOL,      # 保鲜
            4: TemperatureZone.ROOM       # 顶层常温
        }
        
        # 食品保质期数据库
        self.food_expiry_database = {
            "milk": 7,
            "yogurt": 14,
            "cheese": 21,
            "eggs": 21,
            "meat": 3,
            "fish": 2,
            "vegetables": 7,
            "fruits": 5,
            "bread": 7,
            "leftovers": 3,
            "sauce": 30,
            "condiments": 90,
            "frozen_food": 180,
            "ice_cream": 30,
            "beverages": 7,
            "default": 7
        }

    def load_inventory(self):
        """从文件加载库存信息"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.inventory = {}
                    for item_id, item_data in data.get('inventory', {}).items():
                        item_data['storage_time'] = datetime.datetime.fromisoformat(item_data['storage_time'])
                        item_data['temperature_zone'] = TemperatureZone(item_data['temperature_zone'])
                        self.inventory[item_id] = FoodItem(**item_data)
                    self.user_preferences = data.get('user_preferences', {})
            except Exception as e:
                logger.error(f"加载库存文件失败: {e}")
                self.inventory = {}
                self.user_preferences = {}

    def save_inventory(self):
        """保存库存信息到文件"""
        try:
            data = {
                'inventory': {},
                'user_preferences': self.user_preferences
            }
            for item_id, item in self.inventory.items():
                item_dict = asdict(item)
                item_dict['storage_time'] = item.storage_time.isoformat()
                item_dict['temperature_zone'] = item.temperature_zone.value
                data['inventory'][item_id] = item_dict
            
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存库存文件失败: {e}")

    def encode_image_to_base64(self, image_path: str) -> str:
        """将图片编码为base64格式"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"图片编码失败: {e}")
            return ""

    def identify_food_from_image_vlm(self, image_path: str) -> Tuple[str, str]:
        """
        使用Qwen VLM从图像识别食品类型
        """
        try:
            # 编码图片
            base64_image = self.encode_image_to_base64(image_path)
            if not base64_image:
                raise Exception("图片编码失败")

            # 构建VLM请求
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "image": f"data:image/jpeg;base64,{base64_image}"
                        },
                        {
                            "text": """请识别这张图片中的食品。请只返回食品的名称，不要包含其他描述。
                            
                            可能的食品类型包括：
                            - milk (牛奶)
                            - yogurt (酸奶)
                            - cheese (奶酪)
                            - eggs (鸡蛋)
                            - meat (肉类)
                            - fish (鱼类)
                            - vegetables (蔬菜)
                            - fruits (水果)
                            - bread (面包)
                            - leftovers (剩菜)
                            - sauce (酱料)
                            - condiments (调味品)
                            - frozen_food (冷冻食品)
                            - ice_cream (冰淇淋)
                            - beverages (饮料)
                            
                            如果图片中没有食品或无法识别，请返回 "unknown"。
                            请只返回食品的英文名称，不要包含其他内容。"""
                        }
                    ]
                }
            ]

            # 调用Qwen VLM
            response = MultiModalConversation.call(
                model='qwen-vl-plus',
                messages=messages
            )

            if response.status_code == 200:
                # 处理响应内容
                content = response.output.choices[0].message.content
                if isinstance(content, list):
                    # 如果是列表，取第一个文本内容
                    identified_food = content[0].get('text', '').strip().lower()
                else:
                    # 如果是字符串，直接使用
                    identified_food = str(content).strip().lower()
                
                logger.info(f"VLM识别结果: {identified_food}")
                
                # 清理识别结果，只保留食品名称
                food_name = self._clean_food_name(identified_food)
                category = self._get_food_category(food_name)
                
                return food_name, category
            else:
                logger.error(f"VLM调用失败: {response.message}")
                return "unknown", "other"
                
        except Exception as e:
            logger.error(f"图像识别失败: {e}")
            return "unknown", "other"

    def _clean_food_name(self, vlm_response: str) -> str:
        """清理VLM返回的食品名称"""
        # 移除常见的无关词汇
        response = vlm_response.lower().strip()
        
        # 直接匹配已知食品类型
        known_foods = list(self.food_expiry_database.keys())
        for food in known_foods:
            if food in response:
                return food
        
        # 处理一些常见的变体
        food_mapping = {
            "酸奶": "yogurt",
            "牛奶": "milk",
            "奶酪": "cheese",
            "鸡蛋": "eggs",
            "肉类": "meat",
            "鱼类": "fish",
            "蔬菜": "vegetables",
            "水果": "fruits",
            "面包": "bread",
            "剩菜": "leftovers",
            "酱料": "sauce",
            "调味品": "condiments",
            "冷冻食品": "frozen_food",
            "冰淇淋": "ice_cream",
            "饮料": "beverages"
        }
        
        for chinese, english in food_mapping.items():
            if chinese in response:
                return english
        
        return "unknown"

    def _get_food_category(self, food_name: str) -> str:
        """根据食品名称确定类别"""
        categories = {
            "dairy": ["milk", "yogurt", "cheese"],
            "protein": ["meat", "fish", "eggs"],
            "produce": ["vegetables", "fruits"],
            "grains": ["bread"],
            "frozen": ["frozen_food", "ice_cream"],
            "beverages": ["beverages"],
            "condiments": ["sauce", "condiments"],
            "leftovers": ["leftovers"]
        }
        
        for category, foods in categories.items():
            if food_name in foods:
                return category
        return "other"

    def find_optimal_storage_location(self, food_name: str, category: str) -> Tuple[int, int]:
        """找到最佳的存储位置"""
        # 根据食品类型确定温度区域
        if category in ["frozen"]:
            target_level = 0  # 冷冻层
        elif category in ["dairy", "protein"]:
            target_level = 1  # 冷藏层
        elif category in ["produce"]:
            target_level = 3  # 保鲜层
        elif category in ["grains", "beverages"]:
            target_level = 4  # 常温层
        else:
            target_level = 2  # 默认冷藏

        # 找到该层可用的扇区
        for section in range(self.sections_per_level):
            if not self._is_section_occupied(target_level, section):
                return target_level, section
        
        # 如果目标层满了，找其他层
        for level in range(self.total_levels):
            for section in range(self.sections_per_level):
                if not self._is_section_occupied(level, section):
                    return level, section
        
        raise Exception("冰箱已满，无法存储新物品")

    def _is_section_occupied(self, level: int, section: int) -> bool:
        """检查指定扇区是否被占用"""
        for item in self.inventory.values():
            if item.level == level and item.section == section:
                return True
        return False

    def add_food_item(self, food_name: str = None, image_path: str = None) -> str:
        """添加新的食品到冰箱"""
        if image_path:
            food_name, category = self.identify_food_from_image_vlm(image_path)
            print(f"识别到的食品: {food_name}, 类别: {category}")
            exit()
            if food_name == "unknown":
                raise Exception("无法识别图片中的食品")
        elif food_name:
            category = self._get_food_category(food_name)
        else:
            raise Exception("必须提供食品名称或图片路径")
        
        # 找到存储位置
        level, section = self.find_optimal_storage_location(food_name, category)
        
        # 创建食品项目
        item_id = f"{food_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        expiry_days = self.food_expiry_database.get(food_name, self.food_expiry_database["default"])
        
        food_item = FoodItem(
            name=food_name,
            category=category,
            storage_time=datetime.datetime.now(),
            expiry_days=expiry_days,
            level=level,
            section=section,
            temperature_zone=self.temperature_zones[level]
        )
        
        self.inventory[item_id] = food_item
        self.save_inventory()
        
        # 自动存储到指定位置
        self.lift(level)
        self.turn(section)
        self.fetch()
        
        logger.info(f"已添加 {food_name} 到第{level}层第{section}扇区")
        return item_id

    def remove_food_item(self, item_id: str) -> bool:
        """移除食品项目"""
        if item_id in self.inventory:
            item = self.inventory[item_id]
            self.lift(item.level)
            self.turn(item.section)
            self.fetch()
            
            del self.inventory[item_id]
            self.save_inventory()
            logger.info(f"已移除 {item.name}")
            return True
        return False

    def get_expiring_foods(self, days_threshold: int = 3) -> List[Tuple[str, FoodItem]]:
        """获取即将过期的食品"""
        expiring_foods = []
        current_time = datetime.datetime.now()
        
        for item_id, item in self.inventory.items():
            expiry_date = item.storage_time + datetime.timedelta(days=item.expiry_days)
            days_until_expiry = (expiry_date - current_time).days
            
            if days_until_expiry <= days_threshold:
                expiring_foods.append((item_id, item))
        
        return sorted(expiring_foods, key=lambda x: x[1].storage_time + datetime.timedelta(days=x[1].expiry_days))

    def get_recommendations(self, user_preferences: List[str] = None) -> List[Tuple[str, FoodItem, str]]:
        """根据用户偏好和保质期提供推荐"""
        recommendations = []
        current_time = datetime.datetime.now()
        
        # 获取即将过期的食品
        expiring_foods = self.get_expiring_foods(2)
        for item_id, item in expiring_foods:
            recommendations.append((item_id, item, f"即将过期（{item.name}）"))
        
        # 根据用户偏好推荐
        if user_preferences:
            for preference in user_preferences:
                for item_id, item in self.inventory.items():
                    if preference.lower() in item.name.lower() or preference.lower() in item.category.lower():
                        expiry_date = item.storage_time + datetime.timedelta(days=item.expiry_days)
                        days_until_expiry = (expiry_date - current_time).days
                        if days_until_expiry > 0:
                            recommendations.append((item_id, item, f"根据偏好推荐（{item.name}）"))
        
        return recommendations[:5]  # 最多返回5个推荐

    def get_inventory_summary(self) -> Dict:
        """获取库存摘要"""
        summary = {
            "total_items": len(self.inventory),
            "by_category": {},
            "by_level": {},
            "expiring_soon": len(self.get_expiring_foods(3))
        }
        
        for item in self.inventory.values():
            # 按类别统计
            if item.category not in summary["by_category"]:
                summary["by_category"][item.category] = 0
            summary["by_category"][item.category] += 1
            
            # 按层统计
            if item.level not in summary["by_level"]:
                summary["by_level"][item.level] = 0
            summary["by_level"][item.level] += 1
        
        return summary

    # 冰箱控制函数
    def lift(self, level_index: int):
        """控制圆形平台上升到指定层"""
        if 0 <= level_index < self.total_levels:
            print(f"reached level {level_index}")
            logger.info(f"平台上升到第{level_index}层")
        else:
            logger.error(f"无效的层数: {level_index}")

    def turn(self, section_index: int):
        """控制圆形平台旋转到指定扇区"""
        if 0 <= section_index < self.sections_per_level:
            print(f"turned to section {section_index}")
            logger.info(f"平台旋转到第{section_index}扇区")
        else:
            logger.error(f"无效的扇区: {section_index}")

    def fetch(self):
        """控制机械臂取物"""
        print("fetched object")
        logger.info("机械臂完成取物操作")

    def auto_retrieve_item(self, item_id: str) -> bool:
        """自动取物功能"""
        if item_id in self.inventory:
            item = self.inventory[item_id]
            self.lift(item.level)
            self.turn(item.section)
            self.fetch()
            
            # 取出后从库存中移除
            del self.inventory[item_id]
            self.save_inventory()
            logger.info(f"已取出并移除 {item.name}")
            return True
        return False

    def set_user_preferences(self, preferences: List[str]):
        """设置用户偏好"""
        self.user_preferences["food_preferences"] = preferences
        self.save_inventory()

    def get_user_preferences(self) -> List[str]:
        """获取用户偏好"""
        return self.user_preferences.get("food_preferences", [])

# 使用示例
if __name__ == "__main__":
    # 创建VLM智能冰箱Agent
    fridge = VLMSmartFridgeAgent()
    
    # 设置用户偏好
    fridge.set_user_preferences(["milk", "fruits", "vegetables"])
    
    # 使用图片添加食品
    try:
        item_id = fridge.add_food_item(image_path="some_fruits.jpg")
        print(f"成功添加食品，ID: {item_id}")
    except Exception as e:
        print(f"添加食品失败: {e}")
    
    # 获取推荐
    recommendations = fridge.get_recommendations()
    print("推荐食品:")
    for item_id, item, reason in recommendations:
        print(f"- {item.name}: {reason}")
    
    # 获取库存摘要
    summary = fridge.get_inventory_summary()
    print(f"\n库存摘要: {summary}") 