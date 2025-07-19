import dashscope
import json
import os
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# 设置API密钥
dashscope.api_key = 'sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

class SmartFridgeQwenAgent:
    def __init__(self):
        self.fridge_data_file = "fridge_inventory_qwen.json"
        
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
    
    def _parse_temperature(self, temp_str: str) -> int:
        """解析温度字符串，提取数字部分"""
        try:
            # 移除所有非数字字符，只保留数字
            import re
            numbers = re.findall(r'\d+', str(temp_str))
            if numbers:
                # 取第一个数字作为温度值
                return int(numbers[0])
            else:
                return 4  # 默认温度
        except:
            return 4  # 默认温度
    
    def _parse_shelf_life(self, shelf_life_str: str) -> int:
        """解析保质期字符串，提取数字部分"""
        try:
            # 移除所有非数字字符，只保留数字
            import re
            numbers = re.findall(r'\d+', str(shelf_life_str))
            if numbers:
                # 取第一个数字作为保质期天数
                return int(numbers[0])
            else:
                return 7  # 默认保质期
        except:
            return 7  # 默认保质期
    
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
            "available_sections": self.fridge_data["level_usage"]
        }
    
    def call_qwen_vl(self, image_path: str, prompt: str) -> Dict:
        """调用Qwen VL模型"""
        try:
            base64_image = self.encode_image(image_path)
            
            response = dashscope.MultiModalConversation.call(
                model='qwen-vl-plus',
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"image": f"data:image/jpeg;base64,{base64_image}"},
                            {"text": prompt}
                        ]
                    }
                ]
            )
            
            if response.status_code == 200:
                # 处理响应内容
                content = response.output.choices[0].message.content
                if isinstance(content, list):
                    # 如果是列表，取第一个文本内容
                    reply = content[0].get('text', '').strip()
                else:
                    # 如果是字符串，直接使用
                    reply = str(content).strip()
                
                return {"success": True, "response": reply}
            else:
                return {"success": False, "error": f"API调用失败: {response.status_code} - {response.message}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def add_item_to_fridge(self, image_path: str) -> Dict:
        """添加物品到冰箱 - 完全由大模型处理"""
        try:
            # 获取冰箱当前状态
            fridge_status = self.get_fridge_status()
            
            # 构建系统提示词
            system_prompt = f"""你是一个智慧冰箱的AI助手。用户要添加一个新物品到冰箱。

冰箱配置：
- 5层，每层4个扇区
- 温度分布：第0层2°C(冷冻)，第1层4°C(冷藏)，第2层6°C(冷藏)，第3层8°C(冷藏)，第4层10°C(冷藏)

当前冰箱状态：
{json.dumps(fridge_status, ensure_ascii=False, indent=2)}

你的任务：
1. 识别图片中的食物
2. 判断这种食物的最佳存储温度（2-10°C）
3. 判断这种食物的保质期天数
4. 根据最佳温度选择最合适的冰箱层
5. 在该层找到空闲的扇区
6. 返回JSON格式的结果，包含：
   - food_name: 食物名称
   - optimal_temp: 最佳存储温度
   - shelf_life_days: 保质期天数
   - category: 食物类别
   - level: 选择的层数
   - section: 选择的扇区
   - reasoning: 选择理由

请只返回JSON格式的结果，不要其他文字。"""

            # 调用大模型
            result = self.call_qwen_vl(image_path, system_prompt)
            
            if not result["success"]:
                return result
            
            # 解析大模型的JSON响应
            try:
                response_text = result["response"]
                # 提取JSON部分
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_str = response_text[start_idx:end_idx]
                    food_info = json.loads(json_str)
                    
                    # 验证必要字段
                    required_fields = ["food_name", "optimal_temp", "shelf_life_days", "category", "level", "section"]
                    for field in required_fields:
                        if field not in food_info:
                            return {"success": False, "error": f"大模型响应缺少必要字段: {field}"}
                    
                    # 验证层和扇区是否有效
                    if not (0 <= int(food_info["level"]) < self.total_levels):
                        return {"success": False, "error": f"无效的层数: {food_info['level']}"}
                    if not (0 <= int(food_info["section"]) < self.sections_per_level):
                        return {"success": False, "error": f"无效的扇区: {food_info['section']}"}
                    
                    # 检查扇区是否可用，如果被占用则寻找其他可用扇区
                    level_str = str(food_info["level"])
                    section_str = str(food_info["section"])
                    
                    # 如果大模型推荐的扇区被占用，寻找其他可用扇区
                    if self.fridge_data["level_usage"][level_str][section_str]:
                        # 首先尝试在同一层找其他扇区
                        available_section = None
                        for sec in range(self.sections_per_level):
                            if not self.fridge_data["level_usage"][level_str][str(sec)]:
                                available_section = sec
                                break
                        
                        # 如果同一层没有可用扇区，寻找其他层
                        if available_section is None:
                            for lvl in range(self.total_levels):
                                lvl_str = str(lvl)
                                for sec in range(self.sections_per_level):
                                    if not self.fridge_data["level_usage"][lvl_str][str(sec)]:
                                        food_info["level"] = lvl
                                        food_info["section"] = sec
                                        level_str = str(lvl)
                                        section_str = str(sec)
                                        available_section = sec
                                        break
                                if available_section is not None:
                                    break
                        
                        # 如果找到可用扇区，更新food_info
                        if available_section is not None:
                            food_info["level"] = int(food_info["level"])
                            food_info["section"] = available_section
                            level_str = str(food_info["level"])
                            section_str = str(available_section)
                        else:
                            return {"success": False, "error": "冰箱已满，没有可用空间"}
                    
                    # 控制冰箱移动到指定位置
                    self.lift(int(food_info["level"]))
                    self.turn(int(food_info["section"]))
                    self.fetch()
                    
                    # 记录物品信息
                    item_id = f"{food_info['food_name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    self.fridge_data["items"][item_id] = {
                        "name": food_info["food_name"],
                        "category": food_info["category"],
                        "level": int(food_info["level"]),
                        "section": int(food_info["section"]),
                        "optimal_temp": self._parse_temperature(food_info["optimal_temp"]),
                        "shelf_life_days": self._parse_shelf_life(food_info["shelf_life_days"]),
                        "added_time": datetime.now().isoformat(),
                        "expiry_date": (datetime.now() + timedelta(days=self._parse_shelf_life(food_info["shelf_life_days"]))).isoformat(),
                        "reasoning": food_info.get("reasoning", "")
                    }
                    
                    # 更新层使用情况
                    self.fridge_data["level_usage"][level_str][section_str] = True
                    
                    # 保存数据
                    self.save_fridge_data()
                    
                    return {
                        "success": True,
                        "item_id": item_id,
                        "food_name": food_info["food_name"],
                        "level": food_info["level"],
                        "section": food_info["section"],
                        "message": f"已将 {food_info['food_name']} 放入第 {food_info['level']} 层第 {food_info['section']} 扇区",
                        "reasoning": food_info.get("reasoning", "")
                    }
                    
                else:
                    return {"success": False, "error": "大模型响应格式错误，未找到JSON"}
                    
            except json.JSONDecodeError as e:
                return {"success": False, "error": f"JSON解析失败: {e}"}
            except Exception as e:
                return {"success": False, "error": f"处理大模型响应时出错: {e}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_recommendations(self) -> Dict:
        """获取智能推荐 - 完全由大模型处理"""
        try:
            # 获取冰箱当前状态
            fridge_status = self.get_fridge_status()
            
            # 构建系统提示词
            system_prompt = f"""你是一个智慧冰箱的AI助手。用户想要获取关于冰箱内容的智能推荐。

冰箱配置：
- 5层，每层4个扇区
- 温度分布：第0层2°C(冷冻)，第1层4°C(冷藏)，第2层6°C(冷藏)，第3层8°C(冷藏)，第4层10°C(冷藏)

当前冰箱状态：
{json.dumps(fridge_status, ensure_ascii=False, indent=2)}

你的任务：
分析冰箱中的物品，提供智能推荐。考虑以下因素：
1. 即将过期的物品（2天内）
2. 已过期的物品
3. 新鲜水果和蔬菜
4. 可以组合烹饪的食材
5. 营养搭配建议
6. 购物建议

请返回JSON格式的推荐结果，包含：
- recommendations: 推荐列表，每个推荐包含：
  - type: 推荐类型（expiring_soon/expired/fresh_fruits/cooking_suggestion/nutrition/shopping）
  - title: 推荐标题
  - items: 相关物品列表
  - message: 推荐信息
  - action: 建议的行动
- total_recommendations: 推荐总数

请只返回JSON格式的结果，不要其他文字。"""

            # 调用大模型
            result = self.call_qwen_vl("some_food.jpg", system_prompt)  # 使用任意图片，因为我们只需要文本分析
            
            if not result["success"]:
                return result
            
            # 解析大模型的JSON响应
            try:
                response_text = result["response"]
                # 提取JSON部分
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_str = response_text[start_idx:end_idx]
                    recommendations = json.loads(json_str)
                    
                    return {
                        "success": True,
                        "recommendations": recommendations.get("recommendations", []),
                        "total_recommendations": recommendations.get("total_recommendations", 0)
                    }
                    
                else:
                    return {"success": False, "error": "大模型响应格式错误，未找到JSON"}
                    
            except json.JSONDecodeError as e:
                return {"success": False, "error": f"JSON解析失败: {e}"}
            except Exception as e:
                return {"success": False, "error": f"处理大模型响应时出错: {e}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
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

def main():
    """主函数 - 演示智慧冰箱功能"""
    fridge = SmartFridgeQwenAgent()
    
    print("=== 智慧冰箱Qwen Agent启动 ===")
    
    # 演示添加物品
    print("\n1. 添加物品到冰箱")
    if os.path.exists("some_food.jpg"):
        result = fridge.add_item_to_fridge("some_food.jpg")
        print(f"添加结果: {result}")
    else:
        print("未找到some_food.jpg文件")
    
    # 显示库存
    print("\n2. 查看冰箱库存")
    inventory = fridge.get_fridge_inventory()
    print(f"库存信息: {inventory}")
    
    # 获取推荐
    print("\n3. 获取智能推荐")
    recommendations = fridge.get_recommendations()
    print(f"推荐信息: {recommendations}")
    
    print("\n=== 智慧冰箱Qwen Agent演示完成 ===")

if __name__ == "__main__":
    main() 