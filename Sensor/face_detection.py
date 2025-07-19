import cv2
import numpy as np
import serial
import requests
import logging
import time

class FaceDetector:
    def __init__(self, camera_index=0, serial_port='/dev/tty', baud_rate=9600, web_server_url="http://localhost:8080"):
        # 初始化摄像头
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            print(f"❌ 无法打开摄像头 {camera_index}")
            self.cap = None
        else:
            print(f"✅ 摄像头 {camera_index} 初始化成功")
        
        # 加载人脸检测器
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        # 假设的参考距离和对应的人脸框大小（需要根据实际情况校准）
        self.REFERENCE_FACE_WIDTH = 150  # 像素
        self.REFERENCE_DISTANCE = 50  # 厘米
        
        # Web服务器URL
        self.web_server_url = web_server_url
        
        # 防抖变量
        self.last_event_time = 0
        self.event_cooldown = 3.0  # 3秒冷却时间
        
        # 配置日志 - 只记录错误
        logging.basicConfig(
            level=logging.ERROR,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # 初始化串口
        try:
            self.serial_port = serial.Serial(serial_port, baud_rate)
            # 减少输出，避免日志混乱
            # print(f"串口 {serial_port} 已成功打开")
        except Exception as e:
            print(f"串口打开失败：{str(e)}")
            self.serial_port = None

    def estimate_distance(self, face_width):
        """根据人脸框宽度估算距离"""
        # 使用简单的反比例关系估算距离
        distance = (self.REFERENCE_FACE_WIDTH * self.REFERENCE_DISTANCE) / face_width
        return distance

    def send_serial_event(self):
        """通过串口发送事件字符串"""
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.write(b'event_camera')
                # 减少输出，避免日志混乱
                # print("已发送事件信号")
            except Exception as e:
                print(f"发送串口数据失败：{str(e)}")
    
    def send_web_event(self):
        """通过Web API发送接近传感器事件"""
        current_time = time.time()
        
        # 防抖检查
        if current_time - self.last_event_time < self.event_cooldown:
            # 减少输出，避免日志混乱
            # print(f"⏰ 接近事件被忽略 - 冷却时间未到 (剩余{self.event_cooldown - (current_time - self.last_event_time):.1f}秒)")
            return
        
        self.last_event_time = current_time
        
        try:
            # 调用接近传感器API
            response = requests.post(
                f"{self.web_server_url}/api/proximity-sensor",
                json={"detected": True, "distance": "near"},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                # 减少输出，避免日志混乱
                # print(f"✅ 接近传感器事件触发成功: {data.get('recommendation', {}).get('greeting', '')}")
            else:
                self.logger.error(f"Web服务器响应异常: {response.status_code}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"无法连接到Web服务器: {e}")
        except Exception as e:
            self.logger.error(f"发送Web事件失败: {e}")

    def detect_and_count_faces(self):
        """检测人脸并估算距离"""
        if self.cap is None:
            return None
            
        ret, frame = self.cap.read()
        if not ret:
            return None

        # 转换为灰度图
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 检测人脸
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        # 检查是否需要发送事件
        if len(faces) >= 1:
            for (x, y, w, h) in faces:
                distance = self.estimate_distance(w)
                if distance <= 50:  # 当有任何一个人脸距离小于等于50厘米时
                    self.send_serial_event()  # 保留串口事件
                    self.send_web_event()     # 发送Web事件
                    break

        # 在图像上标记人脸并显示距离
        for (x, y, w, h) in faces:
            # 绘制人脸框
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # 估算距离
            distance = self.estimate_distance(w)
            
            # 显示距离信息
            distance_text = f'距离: {distance:.1f}cm'
            cv2.putText(frame, distance_text, (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # 显示人脸计数
        count_text = f'检测到的人脸数: {len(faces)}'
        cv2.putText(frame, count_text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        return frame

    def run(self, headless=False):
        """运行人脸检测程序"""
        try:
            # 如果没有摄像头，模拟检测事件
            if self.cap is None:
                print("⚠️  摄像头不可用，将模拟人脸检测事件")
                while True:
                    # 模拟每30秒触发一次接近事件
                    time.sleep(30)
                    print("🔍 模拟人脸检测事件...")
                    self.send_web_event()
            else:
                while True:
                    frame = self.detect_and_count_faces()
                    if frame is None:
                        break

                    if not headless:
                        cv2.imshow('Face Detection', frame)
                        # 按'q'键退出
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                    else:
                        # 无头模式，只进行检测，不显示窗口
                        time.sleep(0.1)  # 短暂休眠以减少CPU使用

        finally:
            if self.cap is not None:
                self.cap.release()
            if not headless:
                cv2.destroyAllWindows()
            if self.serial_port:
                self.serial_port.close()

def main():
    # 创建检测器实例（可以通过参数指定摄像头索引和串口设置）
    detector = FaceDetector(
        camera_index=0, 
        serial_port='/dev/tty', 
        baud_rate=9600,
        web_server_url="http://localhost:8080"
    )
    
    # 检查是否在无头模式下运行
    import sys
    headless = '--headless' in sys.argv
    
    if headless:
        # 减少输出，避免日志混乱
        # print("🔍 启动无头模式人脸检测...")
        detector.run(headless=True)
    else:
        print("🔍 启动GUI模式人脸检测...")
        detector.run(headless=False)

if __name__ == '__main__':
    main()