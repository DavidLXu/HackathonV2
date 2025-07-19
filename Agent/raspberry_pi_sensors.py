#!/usr/bin/env python3
"""
树莓派传感器接口模块
集成接近传感器、放入/取出按钮等外设
"""

import time
import threading
from typing import Callable, Optional
from enum import Enum

class SensorState(Enum):
    """传感器状态枚举"""
    IDLE = "idle"
    DETECTED = "detected"
    PRESSED = "pressed"
    RELEASED = "released"

class ProximitySensor:
    """接近传感器类"""
    
    def __init__(self, pin: int, threshold: float = 10.0):
        """
        初始化接近传感器
        
        Args:
            pin: GPIO引脚号
            threshold: 检测阈值（厘米）
        """
        self.pin = pin
        self.threshold = threshold
        self.current_state = SensorState.IDLE
        self.last_detection_time = 0
        self.callback = None
        
        # 模拟传感器状态（实际使用时替换为GPIO代码）
        self._distance = 100.0  # 默认距离100cm
        self._is_detecting = False
        
    def read_distance(self) -> float:
        """读取距离值（厘米）"""
        # 这里应该调用实际的GPIO代码
        # 例如：return self._read_ultrasonic_distance()
        return self._distance
    
    def is_object_detected(self) -> bool:
        """检测是否有物体接近"""
        distance = self.read_distance()
        return distance < self.threshold
    
    def set_callback(self, callback: Callable[[SensorState], None]):
        """设置状态变化回调函数"""
        self.callback = callback
    
    def start_monitoring(self):
        """开始监控传感器状态"""
        def monitor():
            while True:
                old_state = self.current_state
                
                if self.is_object_detected():
                    if self.current_state == SensorState.IDLE:
                        self.current_state = SensorState.DETECTED
                        self.last_detection_time = time.time()
                        if self.callback:
                            self.callback(SensorState.DETECTED)
                else:
                    if self.current_state == SensorState.DETECTED:
                        self.current_state = SensorState.IDLE
                        if self.callback:
                            self.callback(SensorState.IDLE)
                
                time.sleep(0.1)  # 100ms检测间隔
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    # 模拟方法（用于测试）
    def simulate_object_approach(self, distance: float):
        """模拟物体接近"""
        self._distance = distance
    
    def simulate_object_leave(self):
        """模拟物体离开"""
        self._distance = 100.0

class ButtonSensor:
    """按钮传感器类"""
    
    def __init__(self, pin: int, button_type: str = "put_in"):
        """
        初始化按钮传感器
        
        Args:
            pin: GPIO引脚号
            button_type: 按钮类型 ("put_in" 或 "take_out")
        """
        self.pin = pin
        self.button_type = button_type
        self.current_state = SensorState.IDLE
        self.callback = None
        self.last_press_time = 0
        
        # 模拟按钮状态
        self._is_pressed = False
        
    def read_button_state(self) -> bool:
        """读取按钮状态"""
        # 这里应该调用实际的GPIO代码
        # 例如：return GPIO.input(self.pin) == GPIO.LOW
        return self._is_pressed
    
    def set_callback(self, callback: Callable[[SensorState, str], None]):
        """设置按钮回调函数"""
        self.callback = callback
    
    def start_monitoring(self):
        """开始监控按钮状态"""
        def monitor():
            while True:
                old_state = self.current_state
                
                if self.read_button_state():
                    if self.current_state == SensorState.IDLE:
                        self.current_state = SensorState.PRESSED
                        self.last_press_time = time.time()
                        if self.callback:
                            self.callback(SensorState.PRESSED, self.button_type)
                else:
                    if self.current_state == SensorState.PRESSED:
                        self.current_state = SensorState.RELEASED
                        if self.callback:
                            self.callback(SensorState.RELEASED, self.button_type)
                        time.sleep(0.1)  # 防抖
                        self.current_state = SensorState.IDLE
                
                time.sleep(0.05)  # 50ms检测间隔
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    # 模拟方法（用于测试）
    def simulate_press(self):
        """模拟按下按钮"""
        self._is_pressed = True
    
    def simulate_release(self):
        """模拟释放按钮"""
        self._is_pressed = False

class SensorManager:
    """传感器管理器"""
    
    def __init__(self):
        """初始化传感器管理器"""
        self.proximity_sensor = ProximitySensor(pin=18)  # GPIO18
        self.put_in_button = ButtonSensor(pin=23, button_type="put_in")  # GPIO23
        self.take_out_button = ButtonSensor(pin=24, button_type="take_out")  # GPIO24
        
        self.sensor_callbacks = []
        self.is_monitoring = False
        
    def add_sensor_callback(self, callback: Callable[[str, SensorState], None]):
        """添加传感器回调函数"""
        self.sensor_callbacks.append(callback)
    
    def _handle_proximity_change(self, state: SensorState):
        """处理接近传感器状态变化"""
        for callback in self.sensor_callbacks:
            callback("proximity", state)
    
    def _handle_button_change(self, state: SensorState, button_type: str):
        """处理按钮状态变化"""
        for callback in self.sensor_callbacks:
            callback(button_type, state)
    
    def start_monitoring(self):
        """开始监控所有传感器"""
        if self.is_monitoring:
            return
        
        # 设置回调函数
        self.proximity_sensor.set_callback(self._handle_proximity_change)
        self.put_in_button.set_callback(self._handle_button_change)
        self.take_out_button.set_callback(self._handle_button_change)
        
        # 启动监控
        self.proximity_sensor.start_monitoring()
        self.put_in_button.start_monitoring()
        self.take_out_button.start_monitoring()
        
        self.is_monitoring = True
        print("🔍 传感器监控已启动")
    
    def stop_monitoring(self):
        """停止监控所有传感器"""
        self.is_monitoring = False
        print("🔍 传感器监控已停止")
    
    def get_sensor_status(self) -> dict:
        """获取所有传感器状态"""
        return {
            "proximity": {
                "state": self.proximity_sensor.current_state.value,
                "distance": self.proximity_sensor.read_distance(),
                "detected": self.proximity_sensor.is_object_detected()
            },
            "put_in_button": {
                "state": self.put_in_button.current_state.value,
                "pressed": self.put_in_button.read_button_state()
            },
            "take_out_button": {
                "state": self.take_out_button.current_state.value,
                "pressed": self.take_out_button.read_button_state()
            }
        }

# 测试代码
if __name__ == "__main__":
    def sensor_callback(sensor_type: str, state: SensorState):
        print(f"🔔 {sensor_type}: {state.value}")
    
    manager = SensorManager()
    manager.add_sensor_callback(sensor_callback)
    manager.start_monitoring()
    
    print("🧪 传感器测试模式")
    print("模拟接近传感器检测...")
    
    # 模拟测试
    time.sleep(2)
    manager.proximity_sensor.simulate_object_approach(5.0)  # 物体接近
    time.sleep(3)
    manager.proximity_sensor.simulate_object_leave()  # 物体离开
    
    print("模拟按钮按下...")
    time.sleep(1)
    manager.put_in_button.simulate_press()  # 按下放入按钮
    time.sleep(1)
    manager.put_in_button.simulate_release()  # 释放按钮
    
    time.sleep(2)
    print("测试完成") 