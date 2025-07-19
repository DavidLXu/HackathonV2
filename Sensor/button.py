#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import RPi.GPIO as GPIO
import logging
import requests
import json
import os

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
        
        # 设置GPIO为输入，启用内部下拉电阻
        GPIO.setup(self.GPIO_16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.GPIO_17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
        # 设置事件检测
        GPIO.add_event_detect(self.GPIO_16, GPIO.RISING, callback=self._button16_callback, bouncetime=200)
        GPIO.add_event_detect(self.GPIO_17, GPIO.RISING, callback=self._button17_callback, bouncetime=200)
        
        logger.info("GPIO初始化完成")
        logger.info(f"按键16 (GPIO{self.GPIO_16}): 放入物品")
        logger.info(f"按键17 (GPIO{self.GPIO_17}): 取出物品")
        logger.info(f"Web服务器地址: {self.web_server_url}")

    def _button16_callback(self, channel):
        """GPIO16按键回调函数 - 放入物品"""
        logger.info("按键16被按下 - 触发放入物品功能")
        self._trigger_place_item()

    def _button17_callback(self, channel):
        """GPIO17按键回调函数 - 取出物品"""
        logger.info("按键17被按下 - 触发取出物品功能")
        self._trigger_take_out_item()

    def _trigger_place_item(self):
        """触发放入物品功能"""
        try:
            # 调用物理按键API
            response = requests.post(
                f"{self.web_server_url}/api/physical-button",
                json={"button_type": "place"},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    logger.info(f"放入物品功能触发成功: {data.get('message')}")
                else:
                    logger.error(f"放入物品功能触发失败: {data.get('error')}")
            else:
                logger.error(f"Web服务器响应异常: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"无法连接到Web服务器: {e}")
            logger.info("请确保Web服务器正在运行: python web_interface.py")

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