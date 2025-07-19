# 人脸检测集成使用说明

## 概述
人脸检测功能已成功整合到 `smart_fridge_qwen.py` 中，作为接近传感器的一部分。现在人脸检测功能直接集成在冰箱Agent中，无需单独运行人脸检测进程。

## 功能特性

### 🔍 人脸检测功能
- **自动检测**: 当检测到人脸距离小于50cm时，自动触发接近传感器事件
- **防抖机制**: 3秒冷却时间，避免重复触发
- **后台监控**: 在冰箱Agent中后台运行，无需单独进程
- **容错处理**: 即使摄像头不可用，也会优雅降级

### 🌐 Web服务器集成
- **自动启动**: Web服务器启动时自动启动人脸检测监控
- **实时日志**: 在Web服务器端记录人脸检测事件
- **个性化推荐**: 根据时间、工作日/周末提供个性化建议
- **API接口**: 通过 `/api/proximity-sensor` 接口接收事件

## 启动方式

### 方式1: 直接启动Web服务器（推荐）
```bash
cd Agent
python web_interface.py
```

### 方式2: 使用Python启动脚本
```bash
python start_system.py
```

### 方式3: 使用Shell启动脚本
```bash
./start_with_venv.sh
```

### 方式4: 使用干净启动脚本（避免输出混乱）
```bash
./start_clean.sh
```

### 方式4: 使用静默启动脚本（推荐，完全避免输出混乱）
```bash
./start_silent.sh
```

## 系统组件

启动后系统包含以下组件：

1. **🌐 Web界面** (端口8080)
   - 提供Web界面和API服务
   - 记录人脸检测事件日志
   - 提供个性化推荐
   - **自动启动人脸检测监控**

2. **🔘 物理按键检测**
   - GPIO 16: 放入物品（拍照识别）
   - GPIO 17: 取出物品

3. **👤 人脸检测** (已整合到冰箱Agent中)
   - 自动检测人脸接近
   - 触发接近传感器事件
   - 后台线程运行
   - 无需单独进程

## 日志查看

### 使用日志查看工具
```bash
./view_logs.sh
```

### Web服务器日志
人脸检测事件会在Web服务器日志中显示：
```
👤 检测到人脸接近 - 触发接近传感器事件
```

### 人脸检测日志
- 成功事件: `✅ 接近传感器事件触发成功: [问候语]`
- 冷却时间: `⏰ 接近事件被忽略 - 冷却时间未到 (剩余X.X秒)`
- 连接错误: `❌ 无法连接到Web服务器: [错误信息]`

### 日志文件位置
- Web界面: `logs/web_interface.log`
- 按键检测: `logs/button.log`
- 人脸检测: `logs/face_detection.log`

## 测试验证

### 测试整合后的人脸检测功能
```bash
python test_integrated_face_detection.py
```

### 测试Web API集成
```bash
python test_face_detection_integration.py
```

## 故障排除

### 摄像头问题
如果摄像头不可用，系统会自动切换到模拟模式：
- 每30秒模拟一次人脸检测事件
- 确保系统功能正常运行

### 连接问题
- 检查Web服务器是否在端口8080运行
- 确认网络连接正常
- 查看错误日志进行调试

## 配置选项

### 人脸检测参数
- **检测距离**: 50cm（可在代码中调整）
- **冷却时间**: 3秒（可在代码中调整）
- **摄像头索引**: 0（默认）

### Web服务器参数
- **端口**: 8080
- **API端点**: `/api/proximity-sensor`
- **日志级别**: INFO

## 停止系统

按 `Ctrl+C` 停止整个系统，所有组件会自动关闭。

## 技术细节

### 人脸检测算法
- 使用OpenCV的Haar级联分类器
- 基于人脸框大小估算距离
- 支持多人脸检测

### API接口
```json
POST /api/proximity-sensor
{
  "detected": true,
  "distance": "near"
}
```

### 响应格式
```json
{
  "success": true,
  "recommendation": {
    "greeting": "下午好！",
    "main_recommendation": "下午茶时间，可以享用冰箱里的新鲜食物",
    "quick_tip": "注意检查食物保质期，避免浪费",
    "urgency_level": "low"
  },
  "time_context": "下午",
  "workday_context": "周末"
}
``` 