# 智慧冰箱系统

## 项目概述

这是一个完整的智慧冰箱管理系统，集成了物理按键控制、Web界面管理和智能推荐功能。

### 主要功能

- **物理按键控制**：GPIO 16用于放入物品，GPIO 17用于取出物品
- **Web界面管理**：现代化的Web界面用于查看冰箱状态和管理物品
- **智能推荐**：基于保质期和用户偏好提供智能推荐
- **实时监控**：实时监控冰箱状态和物品保质期

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv env

# 激活虚拟环境
source env/bin/activate

# 安装依赖
pip install flask dashscope requests RPi.GPIO
```

### 2. 设置环境变量

```bash
# 设置DashScope API密钥
export DASHSCOPE_API_KEY="your_api_key_here"
```

### 3. 启动系统

#### 方法一：使用虚拟环境启动脚本（推荐）
```bash
./start_with_venv.sh
```

#### 方法二：使用Python启动脚本
```bash
python start_system.py
```

#### 方法三：手动启动
```bash
# 激活虚拟环境
source env/bin/activate

# 启动Web界面
cd Agent
python web_interface.py &

# 启动按键检测
cd Sensor
python button.py
```

### 4. 访问系统

- **Web界面**：http://localhost:8080
- **物理按键**：
  - GPIO 16 (绿色)：放入物品
  - GPIO 17 (红色)：取出物品

## 项目结构

```
HackathonV2/
├── README.md                    # 项目说明
├── start_system.py              # Python启动脚本
├── start_with_venv.sh           # Bash启动脚本（推荐）
├── env/                         # 虚拟环境
├── Agent/                       # Web界面和智能Agent
│   ├── web_interface.py         # Web服务器
│   ├── smart_fridge_qwen.py     # 智慧冰箱Agent
│   └── templates/               # Web界面模板
└── Sensor/                      # 传感器和物理控制
    ├── button.py                # 物理按键检测
    ├── step.py                  # ESP32串口通信
    └── README_INTEGRATION.md    # 详细使用说明
```

## 硬件连接

### 按键连接
- **GPIO 16 (绿色按键)**：连接到3.3V和GPIO 16，用于触发放入物品功能
- **GPIO 17 (红色按键)**：连接到3.3V和GPIO 17，用于触发取出物品功能

### ESP32串口连接
- **串口**：连接到 `/dev/ttyAMA0` (硬件串口)
- **波特率**：115200

## 功能说明

### 物理按键功能

#### GPIO 16 (绿色按键) - 放入物品
- 按下按键后触发放入物品功能
- 系统会检查Web服务器状态
- 记录操作日志
- 可以扩展为拍照识别功能

#### GPIO 17 (红色按键) - 取出物品
- 按下按键后自动取出即将过期的物品
- 优先取出过期或即将过期的物品
- 显示取出的物品信息
- 更新冰箱库存状态

### Web界面功能

#### 主要功能
- **实时监控**：显示冰箱内所有物品状态
- **智能推荐**：基于保质期提供推荐
- **物品管理**：添加和取出物品
- **保质期管理**：可视化显示物品保质期

#### 操作按钮
- **接近传感器**：模拟用户接近，提供个性化推荐
- **放入物品**：上传图片并自动识别存储
- **取出物品**：高亮显示推荐物品
- **偏好设置**：设置用户偏好

## 故障排除

### 常见问题

1. **虚拟环境问题**
   ```bash
   # 重新创建虚拟环境
   rm -rf env
   python -m venv env
   source env/bin/activate
   pip install flask dashscope requests RPi.GPIO
   ```

2. **GPIO权限问题**
   ```bash
   # 添加用户到gpio组
   sudo usermod -a -G gpio $USER
   # 重新登录或重启
   ```

3. **Web服务器无法访问**
   ```bash
   # 检查端口是否被占用
   sudo netstat -tlnp | grep 8080
   # 检查防火墙设置
   sudo ufw status
   ```

4. **按键无响应**
   ```bash
   # 检查GPIO状态
   gpio readall
   # 检查按键连接
   gpio -g read 16
   gpio -g read 17
   ```

### 环境测试

运行环境测试脚本：
```bash
cd Sensor
python test_env.py
```

## 开发说明

### 扩展功能

1. **摄像头集成**：在放入物品时自动拍照并识别
2. **语音提示**：添加语音提示功能
3. **LED指示灯**：添加LED指示灯显示系统状态

### API接口

#### 物理按键API
```
POST /api/physical-button
Content-Type: application/json

{
    "button_type": "place" | "take_out"
}
```

#### 响应格式
```json
{
    "success": true,
    "message": "操作成功",
    "action": "place_item" | "take_out_item",
    "item": {
        "id": "item_id",
        "name": "物品名称",
        "category": "物品类别"
    }
}
```

## 技术支持

如果遇到问题，请检查：
1. 硬件连接是否正确
2. 软件依赖是否完整
3. 环境变量是否正确设置
4. 系统权限是否足够

更多详细信息请参考 `Sensor/README_INTEGRATION.md`。 