# 智慧冰箱物理按键与Web界面整合系统

## 系统概述

这个系统将物理按键（GPIO 16和17）与Web界面整合在一起，实现了完整的智慧冰箱控制功能。

### 功能特性

- **物理按键控制**：GPIO 16用于放入物品，GPIO 17用于取出物品
- **Web界面管理**：现代化的Web界面用于查看冰箱状态和管理物品
- **智能推荐**：基于保质期和用户偏好提供智能推荐
- **实时监控**：实时监控冰箱状态和物品保质期

## 硬件连接

### 按键连接
- **GPIO 16 (绿色按键)**：连接到3.3V和GPIO 16，用于触发放入物品功能
- **GPIO 17 (红色按键)**：连接到3.3V和GPIO 17，用于触发取出物品功能

### 连接图
```
Raspberry Pi GPIO:
┌─────────┬─────────┐
│ GPIO 16 │ 绿色按键 │ 放入物品
├─────────┼─────────┤
│ GPIO 17 │ 红色按键 │ 取出物品
└─────────┴─────────┘
```

## 软件架构

### 文件结构
```
HackathonV2/
├── Agent/
│   ├── web_interface.py      # Web界面服务器
│   ├── smart_fridge_qwen.py  # 智慧冰箱Agent
│   └── templates/
│       └── index.html        # Web界面模板
└── Sensor/
    ├── button.py             # 物理按键检测
    ├── start_system.py       # 系统启动脚本
    └── README_INTEGRATION.md # 本文件
```

### 系统组件

1. **Web界面服务器** (`web_interface.py`)
   - 提供RESTful API接口
   - 处理冰箱状态查询
   - 管理物品放入/取出
   - 提供智能推荐

2. **物理按键检测** (`button.py`)
   - 监听GPIO 16和17的按键事件
   - 调用Web API触发相应功能
   - 提供详细的日志记录

3. **系统启动脚本** (`start_system.py`)
   - 同时启动Web界面和按键检测
   - 监控进程状态
   - 提供优雅的启动和停止

## 安装和运行

### 1. 安装依赖

```bash
# 安装Web界面依赖
cd Agent
pip install flask dashscope requests

# 安装按键检测依赖
cd ../Sensor
pip install RPi.GPIO requests
```

### 2. 设置环境变量

```bash
# 设置DashScope API密钥
export DASHSCOPE_API_KEY="your_api_key_here"
```

### 3. 运行系统

#### 方法一：使用虚拟环境启动脚本（推荐）
```bash
# 在项目根目录下运行
./start_with_venv.sh
```

#### 方法二：使用Python启动脚本
```bash
# 在项目根目录下运行
python start_system.py
```

#### 方法三：手动激活虚拟环境
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

## API接口

### 物理按键API
```
POST /api/physical-button
Content-Type: application/json

{
    "button_type": "place" | "take_out"
}
```

### 响应格式
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

## 日志和调试

### 按键检测日志
```bash
# 查看按键检测日志
tail -f /var/log/button_detector.log
```

### Web界面日志
```bash
# 查看Web界面日志
tail -f /var/log/web_interface.log
```

### 常见问题

#### 1. GPIO权限问题
```bash
# 添加用户到gpio组
sudo usermod -a -G gpio $USER
# 重新登录或重启
```

#### 2. Web服务器无法访问
```bash
# 检查端口是否被占用
sudo netstat -tlnp | grep 8080
# 检查防火墙设置
sudo ufw status
```

#### 3. 按键无响应
```bash
# 检查GPIO状态
gpio readall
# 检查按键连接
gpio -g read 16
gpio -g read 17
```

## 扩展功能

### 1. 摄像头集成
可以在放入物品时自动拍照并识别：
```python
# 在button.py中添加摄像头功能
import cv2

def take_photo():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite('item_photo.jpg', frame)
    cap.release()
```

### 2. 语音提示
可以添加语音提示功能：
```python
# 使用espeak进行语音提示
import subprocess

def speak_message(message):
    subprocess.run(['espeak', message])
```

### 3. LED指示灯
可以添加LED指示灯显示系统状态：
```python
# 添加LED控制
GPIO.setup(18, GPIO.OUT)  # LED引脚
GPIO.output(18, GPIO.HIGH)  # 点亮LED
```

## 故障排除

### 启动问题
1. **Web服务器启动失败**：检查端口8080是否被占用
2. **按键检测启动失败**：检查GPIO权限和连接
3. **API调用失败**：检查网络连接和API密钥

### 运行问题
1. **按键无响应**：检查硬件连接和GPIO设置
2. **Web界面无法访问**：检查防火墙和网络设置
3. **系统卡顿**：检查系统资源和进程状态

## 维护和更新

### 定期维护
- 检查日志文件大小
- 清理临时文件
- 更新依赖包

### 系统更新
```bash
# 更新代码
git pull

# 更新依赖
pip install -r requirements.txt

# 重启系统
python start_system.py
```

## 技术支持

如果遇到问题，请检查：
1. 硬件连接是否正确
2. 软件依赖是否完整
3. 环境变量是否正确设置
4. 系统权限是否足够

更多信息请参考项目文档或联系技术支持。 