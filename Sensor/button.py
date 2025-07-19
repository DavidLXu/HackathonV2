#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import RPi.GPIO as GPIO
import logging
import requests
import json
import os
import sys
import cv2

# 添加当前目录到Python路径，以便导入internal_camera
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from internal_camera import FaceDetector

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ButtonDetector:
    def __init__(self, web_server_url="http://localhost:8080"):
        # 设置GPIO模式为BCM
        GPIO.setmode(GPIO.BCM)
        
        # 定义GPIO引脚
        self.GPIO_16 = 16 # 绿色按键 - 放入物品
        self.GPIO_17 = 17 # 红色按键 - 取出物品
        
        # Web服务器URL
        self.web_server_url = web_server_url
        
        # 防抖变量
        self.last_button_time = 0
        self.button_cooldown = 0.5  # 0.5秒冷却时间
        
        # 初始化摄像头
        try:
            self.camera = FaceDetector(camera_index=0)
            logger.info("摄像头初始化成功")
        except Exception as e:
            logger.error(f"摄像头初始化失败: {e}")
            self.camera = None
        
        # 设置GPIO为输入，启用内部下拉电阻
        GPIO.setup(self.GPIO_16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.GPIO_17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
        # 设置事件检测，减少防抖时间
        GPIO.add_event_detect(self.GPIO_16, GPIO.RISING, callback=self._button16_callback, bouncetime=200)
        GPIO.add_event_detect(self.GPIO_17, GPIO.RISING, callback=self._button17_callback, bouncetime=200)
        
        logger.info("GPIO初始化完成")
        logger.info(f"按键16 (GPIO{self.GPIO_16}): 放入物品（拍照识别）")
        logger.info(f"按键17 (GPIO{self.GPIO_17}): 取出物品")
        logger.info(f"Web服务器地址: {self.web_server_url}")

    def _button16_callback(self, channel):
        """GPIO16按键回调函数 - 放入物品"""
        current_time = time.time()
        
        # 防抖检查
        if current_time - self.last_button_time < self.button_cooldown:
            logger.warning(f"按键16被忽略 - 冷却时间未到 (剩余{self.button_cooldown - (current_time - self.last_button_time):.1f}秒)")
            return
        
        self.last_button_time = current_time
        logger.info("按键16被按下 - 触发放入物品功能")
        self._trigger_place_item()

    def _button17_callback(self, channel):
        """GPIO17按键回调函数 - 取出物品"""
        current_time = time.time()
        
        # 防抖检查
        if current_time - self.last_button_time < self.button_cooldown:
            logger.warning(f"按键17被忽略 - 冷却时间未到 (剩余{self.button_cooldown - (current_time - self.last_button_time):.1f}秒)")
            return
        
        self.last_button_time = current_time
        logger.info("按键17被按下 - 触发取出物品功能")
        self._trigger_take_out_item()

    def _trigger_place_item(self):
        """触发放入物品功能 - 拍照并识别"""
        try:
            # 检查摄像头是否可用
            if self.camera is None:
                logger.error("摄像头不可用，无法拍照")
                return
            
            # 拍照
            logger.info("📸 正在拍照...")
            
            # 重新初始化摄像头以确保获取最新图像
            try:
                self.camera.cap.release()
                time.sleep(0.1)  # 短暂等待
                self.camera.cap = cv2.VideoCapture(0)
                self.camera.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                time.sleep(0.5)  # 等待摄像头稳定
                logger.info("📸 摄像头重新初始化完成")
            except Exception as e:
                logger.warning(f"📸 摄像头重新初始化失败: {e}")
            
            image_path = self.camera.capture_image()
            
            if image_path is None:
                logger.error("拍照失败")
                return
            
            logger.info(f"📸 拍照成功: {image_path}")
            
            # 检查图片文件是否存在和大小
            if os.path.exists(image_path):
                file_size = os.path.getsize(image_path)
                logger.info(f"📸 图片文件大小: {file_size} 字节")
                if file_size < 1000:
                    logger.warning("⚠️ 图片文件太小，可能拍摄失败")
            else:
                logger.error("❌ 图片文件不存在")
                return
            
            # 调用放入物品API，上传拍照的图片
            with open(image_path, 'rb') as image_file:
                files = {'file': (os.path.basename(image_path), image_file, 'image/jpeg')}
                
                response = requests.post(
                    f"{self.web_server_url}/api/place-item",
                    files=files,
                    timeout=30
                )
            
            # 调试：不清理临时图片文件，保留用于检查
            logger.info(f"🔍 保留临时图片文件用于调试: {image_path}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    logger.info(f"放入物品功能触发成功: {data.get('message')}")
                    if data.get("food_name"):
                        logger.info(f"识别到的物品: {data.get('food_name')}")
                else:
                    logger.error(f"放入物品功能触发失败: {data.get('error')}")
            else:
                logger.error(f"Web服务器响应异常: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"无法连接到Web服务器: {e}")
            logger.info("请确保Web服务器正在运行: python web_interface.py")
        except Exception as e:
            logger.error(f"放入物品功能出错: {e}")

    def _trigger_take_out_item(self):
        """触发取出物品功能"""
        try:
            # 调用物理按键API
            response = requests.post(
                f"{self.web_server_url}/api/physical-button",
                json={"button_type": "take_out"},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    logger.info(f"取出物品功能触发成功: {data.get('message')}")
                    if data.get("item"):
                        logger.info(f"取出的物品: {data.get('item', {}).get('name', '未知')}")
                else:
                    logger.error(f"取出物品功能触发失败: {data.get('error')}")
            else:
                logger.error(f"Web服务器响应异常: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"无法连接到Web服务器: {e}")
            logger.info("请确保Web服务器正在运行: python web_interface.py")



    def run(self):
        """运行程序，等待按键事件"""
        try:
            logger.info("程序开始运行，等待按键按下...")
            logger.info("按 Ctrl+C 退出程序")
            
            # 保持程序运行
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("程序被用户中断")
        except Exception as e:
            logger.error(f"发生错误: {str(e)}")
        finally:
            self.cleanup()

    def cleanup(self):
        """清理GPIO资源"""
        GPIO.cleanup()
        logger.info("GPIO资源已清理")

if __name__ == "__main__":
    # 检查Web服务器是否运行
    web_server_url = "http://localhost:8080"
    
    try:
        response = requests.get(f"{web_server_url}/api/fridge-status", timeout=3)
        if response.status_code == 200:
            logger.info("Web服务器连接正常")
        else:
            logger.warning("Web服务器响应异常，但继续运行")
    except requests.exceptions.RequestException:
        logger.warning("无法连接到Web服务器，请确保运行: python web_interface.py")
        logger.info("按键功能将无法正常工作，但程序会继续运行")
    
    detector = ButtonDetector(web_server_url)
    detector.run()           