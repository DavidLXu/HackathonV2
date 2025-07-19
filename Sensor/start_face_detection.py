#!/usr/bin/env python3
"""
人脸检测启动脚本
处理摄像头问题并自动重试
"""

import subprocess
import time
import signal
import sys
import os

class FaceDetectionLauncher:
    def __init__(self):
        self.process = None
        self.running = False
        self.max_retries = 3
        self.retry_count = 0
        
    def start_face_detection(self):
        """启动人脸检测"""
        try:
            # 减少输出，避免日志混乱
            # print(f"👤 启动人脸检测 (尝试 {self.retry_count + 1}/{self.max_retries})...")
            
            # 激活虚拟环境并启动人脸检测
            activate_script = os.path.expanduser('~/env/bin/activate')
            if os.path.exists(activate_script):
                cmd = f"source {activate_script} && python face_detection.py --headless"
                self.process = subprocess.Popen(
                    ['bash', '-c', cmd],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:
                self.process = subprocess.Popen(
                    ['python', 'face_detection.py', '--headless'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            
            # 减少输出，避免日志混乱
            # print(f"✅ 人脸检测已启动 (PID: {self.process.pid})")
            
            # 等待进程稳定
            time.sleep(5)
            
            # 检查进程是否还在运行
            if self.process.poll() is not None:
                # print("⚠️  人脸检测进程已停止")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ 启动人脸检测失败: {e}")
            return False
    
    def restart_face_detection(self):
        """重启人脸检测"""
        if self.process:
            self.process.terminate()
            time.sleep(2)
        
        self.retry_count += 1
        return self.start_face_detection()
    
    def run(self):
        """运行人脸检测启动器"""
        # 减少输出，避免日志混乱
        # print("🚀 人脸检测启动器启动...")
        
        # 尝试启动人脸检测
        while self.retry_count < self.max_retries:
            if self.start_face_detection():
                # print("✅ 人脸检测启动成功")
                break
            else:
                # print(f"❌ 人脸检测启动失败，尝试重启...")
                if not self.restart_face_detection():
                    # print(f"❌ 重启失败 ({self.retry_count}/{self.max_retries})")
                    pass
        
        if self.retry_count >= self.max_retries:
            # print("❌ 人脸检测启动失败，已达到最大重试次数")
            return False
        
        # 监控进程
        self.running = True
        while self.running:
            if self.process and self.process.poll() is not None:
                # print("⚠️  人脸检测进程已停止，尝试重启...")
                if not self.restart_face_detection():
                    # print("❌ 重启失败，退出")
                    break
            time.sleep(10)
        
        return True
    
    def stop(self):
        """停止人脸检测"""
        print("🛑 停止人脸检测...")
        self.running = False
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()

def signal_handler(signum, frame):
    """信号处理函数"""
    print("\n🛑 收到停止信号")
    if hasattr(signal_handler, 'launcher'):
        signal_handler.launcher.stop()
    sys.exit(0)

def main():
    """主函数"""
    launcher = FaceDetectionLauncher()
    signal_handler.launcher = launcher
    
    # 设置信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        launcher.run()
    except KeyboardInterrupt:
        print("\n🛑 用户中断")
    finally:
        launcher.stop()

if __name__ == "__main__":
    main() 