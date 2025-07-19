#!/usr/bin/env python3
"""
智慧冰箱系统启动脚本
同时启动Web界面和物理按键检测
"""

import subprocess
import time
import signal
import sys
import os
import requests
import threading

class SmartFridgeSystem:
    def __init__(self):
        self.web_process = None
        self.button_process = None
        self.face_detection_process = None
        self.running = False
        
    def start_web_interface(self):
        """启动Web界面"""
        try:
            print("🌐 启动Web界面...")
            # 切换到Agent目录
            agent_dir = os.path.join(os.path.dirname(__file__), 'Agent')
            
            # 激活虚拟环境并启动Web界面
            activate_script = os.path.expanduser('~/env/bin/activate')
            if os.path.exists(activate_script):
                # 使用bash激活虚拟环境并运行
                cmd = f"source {activate_script} && cd {agent_dir} && python web_interface.py"
                self.web_process = subprocess.Popen(
                    ['bash', '-c', cmd],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:
                # 如果没有虚拟环境，直接运行
                self.web_process = subprocess.Popen(
                    ['python', 'web_interface.py'],
                    cwd=agent_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            
            print(f"✅ Web界面已启动 (PID: {self.web_process.pid})")
            return True
        except Exception as e:
            print(f"❌ 启动Web界面失败: {e}")
            return False
    
    def start_button_detector(self):
        """启动按键检测"""
        try:
            print("🔘 启动按键检测...")
            
            # 激活虚拟环境并启动按键检测
            activate_script = os.path.expanduser('~/env/bin/activate')
            if os.path.exists(activate_script):
                # 使用bash激活虚拟环境并运行
                cmd = f"source {activate_script} && cd Sensor && python button.py"
                self.button_process = subprocess.Popen(
                    ['bash', '-c', cmd],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:
                # 如果没有虚拟环境，直接运行
                self.button_process = subprocess.Popen(
                    ['python', 'button.py'],
                    cwd='Sensor',
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            
            print(f"✅ 按键检测已启动 (PID: {self.button_process.pid})")
            return True
        except Exception as e:
            print(f"❌ 启动按键检测失败: {e}")
            return False
    
    def start_face_detection(self):
        """启动人脸检测"""
        try:
            print("👤 启动人脸检测...")
            
            # 激活虚拟环境并启动人脸检测
            activate_script = os.path.expanduser('~/env/bin/activate')
            if os.path.exists(activate_script):
                # 使用bash激活虚拟环境并运行
                cmd = f"source {activate_script} && cd Sensor && python face_detection.py --headless"
                self.face_detection_process = subprocess.Popen(
                    ['bash', '-c', cmd],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:
                # 如果没有虚拟环境，直接运行
                self.face_detection_process = subprocess.Popen(
                    ['python', 'face_detection.py', '--headless'],
                    cwd='Sensor',
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            
            print(f"✅ 人脸检测已启动 (PID: {self.face_detection_process.pid})")
            
            # 等待进程稳定
            time.sleep(3)
            
            # 检查进程是否还在运行
            if self.face_detection_process.poll() is not None:
                print("⚠️  人脸检测进程已停止，尝试重启...")
                return self.restart_face_detection()
            
            return True
        except Exception as e:
            print(f"❌ 启动人脸检测失败: {e}")
            return False
    
    def restart_face_detection(self):
        """重启人脸检测"""
        try:
            if self.face_detection_process:
                self.face_detection_process.terminate()
                time.sleep(1)
            
            # 重新启动
            activate_script = os.path.expanduser('~/env/bin/activate')
            if os.path.exists(activate_script):
                cmd = f"source {activate_script} && cd Sensor && python face_detection.py --headless"
                self.face_detection_process = subprocess.Popen(
                    ['bash', '-c', cmd],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:
                self.face_detection_process = subprocess.Popen(
                    ['python', 'face_detection.py', '--headless'],
                    cwd='Sensor',
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            
            print(f"✅ 人脸检测已重启 (PID: {self.face_detection_process.pid})")
            return True
        except Exception as e:
            print(f"❌ 重启人脸检测失败: {e}")
            return False
    
    def wait_for_web_server(self, timeout=30):
        """等待Web服务器启动"""
        print("⏳ 等待Web服务器启动...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get('http://localhost:8080/api/fridge-status', timeout=2)
                if response.status_code == 200:
                    print("✅ Web服务器已就绪")
                    return True
            except:
                pass
            time.sleep(1)
        
        print("❌ Web服务器启动超时")
        return False
    
    def monitor_processes(self):
        """监控进程状态"""
        while self.running:
            # 检查Web进程
            if self.web_process and self.web_process.poll() is not None:
                print("⚠️  Web界面进程已停止")
                self.web_process = None
            
            # 检查按键进程
            if self.button_process and self.button_process.poll() is not None:
                print("⚠️  按键检测进程已停止")
                self.button_process = None
            
            # 检查人脸检测进程
            if self.face_detection_process and self.face_detection_process.poll() is not None:
                print("⚠️  人脸检测进程已停止，尝试重启...")
                if self.restart_face_detection():
                    print("✅ 人脸检测重启成功")
                else:
                    print("❌ 人脸检测重启失败")
            
            time.sleep(5)
    
    def start(self):
        """启动整个系统"""
        print("🚀 启动智慧冰箱系统...")
        print("=" * 50)
        
        # 启动Web界面
        if not self.start_web_interface():
            return False
        
        # 等待Web服务器启动
        if not self.wait_for_web_server():
            return False
        
        # 启动按键检测
        if not self.start_button_detector():
            return False
        
        # 启动人脸检测
        if not self.start_face_detection():
            return False
        
        self.running = True
        
        # 启动监控线程
        monitor_thread = threading.Thread(target=self.monitor_processes, daemon=True)
        monitor_thread.start()
        
        print("\n🎉 系统启动完成！")
        print("📱 Web界面: http://localhost:8080")
        print("🔘 物理按键:")
        print("   - GPIO 16 (绿色): 放入物品")
        print("   - GPIO 17 (红色): 取出物品")
        print("👤 人脸检测: 自动触发接近传感器事件")
        print("\n按 Ctrl+C 停止系统")
        
        return True
    
    def stop(self):
        """停止系统"""
        print("\n🛑 正在停止系统...")
        self.running = False
        
        # 停止人脸检测
        if self.face_detection_process:
            print("🛑 停止人脸检测...")
            self.face_detection_process.terminate()
            try:
                self.face_detection_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.face_detection_process.kill()
        
        # 停止按键检测
        if self.button_process:
            print("🛑 停止按键检测...")
            self.button_process.terminate()
            try:
                self.button_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.button_process.kill()
        
        # 停止Web界面
        if self.web_process:
            print("🛑 停止Web界面...")
            self.web_process.terminate()
            try:
                self.web_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.web_process.kill()
        
        print("✅ 系统已停止")

def signal_handler(signum, frame):
    """信号处理函数"""
    print("\n🛑 收到停止信号")
    if hasattr(signal_handler, 'system'):
        signal_handler.system.stop()
    sys.exit(0)

def main():
    """主函数"""
    system = SmartFridgeSystem()
    signal_handler.system = system
    
    # 设置信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        if system.start():
            # 保持运行
            while system.running:
                time.sleep(1)
        else:
            print("❌ 系统启动失败")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 用户中断")
    finally:
        system.stop()

if __name__ == "__main__":
    main() 