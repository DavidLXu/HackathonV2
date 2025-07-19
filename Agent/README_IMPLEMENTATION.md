# 智慧冰箱Agent实现

## 项目概述

本项目实现了一个智能化的冰箱管理系统，包含以下核心功能：

1. **冰箱控制**：控制圆形平台的升降、旋转和取物操作
2. **图像识别**：使用Qwen VL模型识别食物种类
3. **智能存储**：根据食物特性自动选择最佳存储位置
4. **库存管理**：维护冰箱物品的详细信息
5. **智能推荐**：基于保质期和用户偏好提供推荐

## 文件结构

```
HackathonV2/
├── README.md                    # 原始需求文档
├── README_IMPLEMENTATION.md     # 实现说明文档
├── smart_fridge_agent.py        # 基础版本智慧冰箱Agent
├── smart_fridge_agent_advanced.py # 高级版本（使用function calling）
├── demo.py                      # 演示脚本
├── requirements.txt              # 项目依赖
├── some_food.jpg               # 测试图片
└── fridge_inventory.json       # 冰箱库存数据（运行时生成）
```

## 核心功能实现

### 1. 冰箱控制函数

```python
def lift(level_index: int):      # 控制平台升降
def turn(section_index: int):    # 控制平台旋转
def fetch():                     # 控制机械臂取物
```

### 2. 图像识别与物品管理

- 使用Qwen VL模型识别食物图片
- 根据食物数据库获取保质期和最佳存储温度
- 自动选择最优存储位置

### 3. 智能推荐系统

- 即将过期物品提醒
- 已过期物品警告
- 新鲜水果推荐
- 烹饪建议（蔬菜+肉类组合）

### 4. 温度分层管理

- 第0层：2°C (冷冻)
- 第1层：4°C (冷藏)
- 第2层：6°C (冷藏)
- 第3层：8°C (冷藏)
- 第4层：10°C (冷藏)

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行演示

```bash
# 运行默认演示
python demo.py

# 运行基础版本演示
python demo.py basic

# 运行高级版本演示
python demo.py advanced

# 运行交互式演示
python demo.py interactive
```

### 3. 直接运行Agent

```bash
# 运行基础版本
python smart_fridge_agent.py

# 运行高级版本
python smart_fridge_agent_advanced.py
```

## API配置

项目使用Qwen VL模型进行图像识别，需要配置API密钥：

```python
api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

## 使用示例

### 基础版本使用

```python
from smart_fridge_agent import SmartFridgeAgent

# 初始化Agent
fridge = SmartFridgeAgent(api_key)

# 添加物品到冰箱
result = fridge.add_item_to_fridge("some_food.jpg")

# 查看库存
inventory = fridge.get_fridge_inventory()

# 获取推荐
recommendations = fridge.get_recommendations()
```

### 高级版本使用

```python
from smart_fridge_agent_advanced import AdvancedSmartFridgeAgent

# 初始化Agent
fridge = AdvancedSmartFridgeAgent(api_key)

# 使用自然语言交互
result = fridge.process_user_request("some_food.jpg", "请帮我将这个食物放入冰箱")
```

## 数据存储

冰箱库存数据保存在JSON文件中：

- 基础版本：`fridge_inventory.json`
- 高级版本：`fridge_inventory_advanced.json`

数据包含：
- 物品详细信息（名称、类别、位置、保质期等）
- 各层扇区使用情况
- 最后更新时间

## 食物数据库

系统内置了常见食物的数据库，包含：

- 保质期天数
- 最佳存储温度
- 食物类别

支持的食物类型：
- 水果（苹果、香蕉、橙子等）
- 乳制品（牛奶、酸奶、奶酪等）
- 蔬菜（番茄、胡萝卜、洋葱等）
- 肉类和海鲜
- 饮料和零食
- 冷冻食品

## 智能推荐算法

### 1. 过期提醒
- 即将过期（2天内）：建议尽快食用
- 已过期：建议丢弃

### 2. 新鲜推荐
- 新鲜水果：推荐享用
- 新鲜蔬菜：推荐烹饪

### 3. 烹饪建议
- 蔬菜+肉类组合：推荐制作菜肴

## 技术特点

### 1. 模块化设计
- 基础版本：简单直接的API调用
- 高级版本：使用function calling实现智能交互

### 2. 智能存储策略
- 根据食物最佳温度自动选择存储层
- 考虑冰箱空间利用率
- 避免食物交叉污染

### 3. 实时监控
- 自动计算剩余保质期
- 实时更新库存状态
- 智能提醒系统

### 4. 用户友好
- 自然语言交互
- 直观的操作反馈
- 详细的错误处理

## 扩展功能

### 1. 可以添加的功能
- 用户偏好设置
- 购物清单生成
- 营养分析
- 食谱推荐
- 多用户支持

### 2. 硬件集成
- 实际冰箱控制接口
- 传感器数据读取
- 摄像头实时监控

### 3. 云端功能
- 数据同步
- 远程控制
- 智能学习

## 注意事项

1. **API限制**：注意Qwen VL API的调用限制和费用
2. **图片质量**：确保图片清晰以提高识别准确率
3. **数据备份**：定期备份冰箱库存数据
4. **隐私保护**：注意图片数据的隐私保护

## 故障排除

### 常见问题

1. **API调用失败**
   - 检查API密钥是否正确
   - 确认网络连接正常
   - 检查API配额是否充足

2. **图片识别失败**
   - 确保图片格式支持（JPG、PNG等）
   - 检查图片是否清晰
   - 尝试重新上传图片

3. **数据保存失败**
   - 检查文件权限
   - 确认磁盘空间充足
   - 检查JSON格式是否正确

## 贡献指南

欢迎提交Issue和Pull Request来改进项目！

## 许可证

本项目采用MIT许可证。 