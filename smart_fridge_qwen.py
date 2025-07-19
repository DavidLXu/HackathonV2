import dashscope
import json
import os
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# 设置API密钥 - 从环境变量获取
api_key = os.getenv('DASHSCOPE_API_KEY')
if not api_key:
    raise ValueError("Please set the DASHSCOPE_API_KEY environment variable")
dashscope.api_key = api_key

class SmartFridgeQwenAgent:
    def __init__(self):
        self.fridge_data_file = "fridge_inventory_qwen.json"
        
        # 冰箱配置
        self.total_levels = 5  # 5层
        self.sections_per_level = 4  # 每层4个扇区
        self.temperature_levels = {
            0: -18,  # 最底层：-18°C (冷冻)
            1: -5,   # 第二层：-5°C (冷冻)
            2: 2,    # 第三层：2°C (冷藏)
            3: 6,    # 第四层：6°C (冷藏)
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
        """解析温度字符串，提取数字部分（包括负数）"""
        try:
            temp_str = str(temp_str).strip()
            
            # 检查是否包含负号
            is_negative = '-' in temp_str
            
            # 提取数字部分
            import re
            numbers = re.findall(r'\d+', temp_str)
            if numbers:
                # 取第一个数字作为温度值
                result = int(numbers[0])
                # 如果原字符串包含负号，则返回负数
                if is_negative:
                    result = -result
                return result
            else:
                return 4  # 默认温度
        except:
            return 4  # 默认温度
    
    def _parse_shelf_life(self, shelf_life_str: str) -> int:
        """解析保质期字符串，提取数字部分"""
        try:
            shelf_life_str_lower = str(shelf_life_str).lower()
            
            # 检查是否包含长期保存的关键词
            long_term_keywords = ['长期', '永久', '无保质期', '无期限', '长期保存', '无限期', '不限期']
            if any(keyword in shelf_life_str_lower for keyword in long_term_keywords):
                return -1  # 表示长期保存
            
            # 如果输入是纯数字，直接转换
            try:
                result = int(shelf_life_str)
                if result > 0:  # 确保是正数
                    return result
            except ValueError:
                pass
            
            # 检查是否包含"天"、"日"等时间单位
            if '天' in shelf_life_str or '日' in shelf_life_str:
                # 提取数字
                import re
                numbers = re.findall(r'\d+', str(shelf_life_str))
                if numbers:
                    return int(numbers[0])
            
            # 默认保质期
            return 7
        except:
            return 7  # 默认保质期
    
    def find_best_temperature_level(self, optimal_temp: float) -> int:
        """根据最佳温度找到最接近的温度分区"""
        min_distance = float('inf')
        best_level = 2  # 默认选择第2层（2°C）
        
        for level, temp in self.temperature_levels.items():
            distance = abs(temp - optimal_temp)
            if distance < min_distance:
                min_distance = distance
                best_level = level
        
        return best_level
    
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
            
            # 添加重试机制
            max_retries = 3
            for attempt in range(max_retries):
                try:
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
                        ],
                        timeout=30  # 增加超时时间
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
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(2 ** attempt)  # 指数退避
                        continue
                    else:
                        raise e
                        
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
- 温度分布：第0层-18°C(冷冻)，第1层-5°C(冷冻)，第2层2°C(冷藏)，第3层6°C(冷藏)，第4层10°C(冷藏)

温度选择规则：
- 水果、蔬菜、乳制品、谷物、烘焙、饮料：选择2-6°C（第2-3层）
- 肉类、海鲜：选择-5°C（第1层）
- 冰淇淋、冷冻食品：选择-18°C（第0层）
- 其他：选择2-6°C（第2-3层）
- 非食物物品（乐器、工具等）：选择2-6°C（第2-3层）

保质期规则：
- 水果：3-7天
- 蔬菜：5-10天
- 肉类：7-30天
- 乳制品：7-14天
- 谷物：3-7天
- 海鲜：3-7天
- 烘焙：3-7天
- 饮料：7-14天
- 其他：5-10天
- 非食物物品（乐器、工具等）：长期保存

当前冰箱状态：
{json.dumps(fridge_status, ensure_ascii=False, indent=2)}

你的任务：
1. 识别图片中的物品（可能是食物或非食物）
2. 判断这种物品的最佳存储温度（-18°C到10°C之间）
3. 判断这种物品的保质期：
   - 如果是食物，返回具体的保质期天数（如：7、30等数字）
   - 如果是非食物（如乐器、工具等），返回"长期"
4. 根据最佳温度选择最合适的冰箱层
5. 在该层找到空闲的扇区
6. 返回JSON格式的结果，包含：
   - food_name: 物品名称
   - optimal_temp: 最佳存储温度（数字，包括负数）
   - shelf_life_days: 保质期天数（数字，如7、30等，非食物返回"长期"）
   - category: 物品类别
   - level: 选择的层数
   - section: 选择的扇区
   - reasoning: 选择理由

重要提示：
- 食物分类：请在以下分类中选择最合适的：
  * 水果：苹果、橙子、香蕉、葡萄、草莓等
  * 蔬菜：胡萝卜、土豆、洋葱、菠菜、芹菜等
  * 肉类：牛肉、猪肉、鸡肉、鱼肉等
  * 乳制品：牛奶、鸡蛋、奶酪、酸奶等
  * 谷物：面包、米饭、面条、麦片、三明治、汉堡、披萨、寿司等
  * 海鲜：鱼、虾、蟹、贝类等
  * 烘焙：蛋糕、饼干、面包、巧克力、冰淇淋等
  * 饮料：果汁、可乐、啤酒等
  * 其他：如果找不到对应分类，选择"其他"

分类优先级：
- 三明治、汉堡、披萨、寿司等主食类食物优先分类为"谷物"
- 只有真正的非食物（乐器、工具、书籍等）才分类为"非食物"
- 食物都有保质期，非食物才是长期保存

重要：
1. 请确保选择的层温度与物品的最佳存储温度匹配，水果蔬菜不要放在冷冻层！
2. 保质期必须是具体的数字天数，不要写"7天"、"30天"，直接写数字7、30
3. 只有非食物物品才返回"长期"
4. 如果目标层满了，系统会自动选择温度最接近的其他层

温度选择优先级：
- 水果、蔬菜、乳制品、谷物、烘焙、饮料、其他：优先选择2-6°C（第2-3层），绝对不要选择-18°C或-5°C
- 肉类、海鲜：优先选择-5°C（第1层），其次选择-18°C（第0层）
- 冷冻食品：选择-18°C（第0层）

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
                    
                    # 使用最佳温度找到最合适的层
                    optimal_temp = self._parse_temperature(food_info["optimal_temp"])
                    best_level = self.find_best_temperature_level(optimal_temp)
                    food_info["level"] = best_level
                    
                    # 验证温度匹配是否合理
                    actual_temp = self.temperature_levels[best_level]
                    temp_diff = abs(optimal_temp - actual_temp)
                    
                    # 如果温度差异太大，重新选择更合适的层
                    if temp_diff > 10:  # 如果温度差异超过10度
                        print(f"警告：物品最佳温度{optimal_temp}°C与选择层温度{actual_temp}°C差异过大")
                        # 重新寻找更合适的层
                        for level, temp in self.temperature_levels.items():
                            if abs(temp - optimal_temp) <= 5:  # 寻找温度差异在5度以内的层
                                best_level = level
                                food_info["level"] = level
                                print(f"重新选择第{level}层，温度{temp}°C")
                                break
                    
                    # 验证扇区是否有效
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
                        
                        # 如果同一层没有可用扇区，寻找温度最接近的其他层
                        if available_section is None:
                            optimal_temp = self._parse_temperature(food_info["optimal_temp"])
                            best_alternative_level = None
                            min_temp_diff = float('inf')
                            
                            # 寻找温度最接近的可用层
                            for lvl in range(self.total_levels):
                                lvl_str = str(lvl)
                                lvl_temp = self.temperature_levels[lvl]
                                temp_diff = abs(optimal_temp - lvl_temp)
                                
                                # 检查该层是否有可用扇区
                                for sec in range(self.sections_per_level):
                                    if not self.fridge_data["level_usage"][lvl_str][str(sec)]:
                                        # 如果温度差异更小，选择这个层
                                        if temp_diff < min_temp_diff:
                                            min_temp_diff = temp_diff
                                            best_alternative_level = lvl
                                            best_alternative_section = sec
                                        break
                            
                            # 如果找到了合适的替代层
                            if best_alternative_level is not None:
                                food_info["level"] = best_alternative_level
                                food_info["section"] = best_alternative_section
                                level_str = str(best_alternative_level)
                                section_str = str(best_alternative_section)
                                available_section = best_alternative_section
                                
                                # 记录选择理由
                                original_level = int(food_info.get("original_level", food_info["level"]))
                                original_temp = self.temperature_levels[original_level]
                                alternative_temp = self.temperature_levels[best_alternative_level]
                                food_info["reasoning"] = f"{food_info.get('reasoning', '')} 原计划放在第{original_level}层({original_temp}°C)，但该层已满，选择温度最接近的第{best_alternative_level}层({alternative_temp}°C)。"
                            else:
                                available_section = None
                        
                        # 如果找到可用扇区，更新food_info
                        if available_section is not None:
                            food_info["level"] = int(food_info["level"])
                            food_info["section"] = available_section
                            level_str = str(food_info["level"])
                            section_str = str(available_section)
                        else:
                            # 冰箱满了，提醒大模型重新规划
                            return {
                                "success": False, 
                                "error": "冰箱已满，没有可用空间。建议：1. 清理过期物品 2. 重新整理冰箱空间 3. 考虑取出一些不常用的物品"
                            }
                    
                    # 控制冰箱移动到指定位置
                    self.lift(int(food_info["level"]))
                    self.turn(int(food_info["section"]))
                    self.fetch()
                    
                    # 记录物品信息
                    item_id = f"{food_info['food_name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    shelf_life_days = self._parse_shelf_life(food_info["shelf_life_days"])
                    
                    # 处理长期保存的物品
                    if shelf_life_days == -1:
                        # 长期保存，设置过期时间为很久以后
                        expiry_date = (datetime.now() + timedelta(days=36500)).isoformat()  # 100年后
                    else:
                        expiry_date = (datetime.now() + timedelta(days=shelf_life_days)).isoformat()
                    
                    self.fridge_data["items"][item_id] = {
                        "name": food_info["food_name"],
                        "category": food_info["category"],
                        "level": int(food_info["level"]),
                        "section": int(food_info["section"]),
                        "optimal_temp": self._parse_temperature(food_info["optimal_temp"]),
                        "shelf_life_days": shelf_life_days,
                        "added_time": datetime.now().isoformat(),
                        "expiry_date": expiry_date,
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
- 温度分布：第0层-18°C(冷冻)，第1层-5°C(冷冻)，第2层2°C(冷藏)，第3层6°C(冷藏)，第4层10°C(冷藏)

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
                # 如果API调用失败，使用模拟数据
                return self._generate_mock_recommendations(fridge_status)
            
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
                    # 如果JSON解析失败，使用模拟数据
                    return self._generate_mock_recommendations(fridge_status)
                    
            except json.JSONDecodeError as e:
                # 如果JSON解析失败，使用模拟数据
                return self._generate_mock_recommendations(fridge_status)
            except Exception as e:
                # 如果处理失败，使用模拟数据
                return self._generate_mock_recommendations(fridge_status)
                
        except Exception as e:
            # 如果完全失败，使用模拟数据
            return self._generate_mock_recommendations(self.get_fridge_status())
    
    def _generate_mock_recommendations(self, fridge_status: Dict) -> Dict:
        """生成模拟推荐数据"""
        recommendations = []
        
        # 分析冰箱中的物品
        inventory = fridge_status.get("inventory", [])
        expiring_items = []
        fresh_items = []
        long_term_items = []
        
        for item in inventory:
            if item.get("is_expired", False):
                expiring_items.append(item)
            elif item.get("days_remaining", 0) <= 2:
                expiring_items.append(item)
            elif item.get("expiry_progress", {}).get("status") == "long_term":
                long_term_items.append(item)
            else:
                fresh_items.append(item)
        
        # 生成推荐
        if expiring_items:
            recommendations.append({
                "type": "expiring_soon",
                "title": f"即将过期的物品 ({len(expiring_items)}个)",
                "items": expiring_items,
                "message": f"有{len(expiring_items)}个物品即将过期，建议尽快食用或处理。",
                "action": "立即检查并处理过期物品"
            })
        
        if fresh_items:
            recommendations.append({
                "type": "fresh_fruits",
                "title": "新鲜物品",
                "items": fresh_items,
                "message": f"冰箱中有{len(fresh_items)}个新鲜物品，可以放心食用。",
                "action": "享受新鲜食物"
            })
        
        if long_term_items:
            recommendations.append({
                "type": "long_term",
                "title": "长期保存物品",
                "items": long_term_items,
                "message": f"有{len(long_term_items)}个物品可以长期保存，无需担心过期。",
                "action": "妥善保管长期物品"
            })
        
        # 如果没有特殊推荐，添加一般性建议
        if not recommendations:
            recommendations.append({
                "type": "general",
                "title": "冰箱状态良好",
                "items": [],
                "message": "冰箱中的物品状态良好，可以正常使用。",
                "action": "继续保持良好的存储习惯"
            })
        
        return {
            "success": True,
            "recommendations": recommendations,
            "total_recommendations": len(recommendations)
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