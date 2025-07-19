import cv2
import os
from datetime import datetime

class FaceDetector:
    def __init__(self, camera_index=0):
        # 初始化摄像头
        self.cap = cv2.VideoCapture(camera_index)
        
        # 设置摄像头参数，确保获取最新帧
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 设置缓冲区大小为1
        self.cap.set(cv2.CAP_PROP_FPS, 30)  # 设置帧率
        
        # 创建uploads目录
        self.upload_dir = "uploads"
        os.makedirs(self.upload_dir, exist_ok=True)
        
        # 测试摄像头是否可用
        ret, frame = self.cap.read()
        if not ret:
            raise Exception("无法读取摄像头")
        print("📸 摄像头初始化成功，测试读取正常")

    def detect_and_count_faces(self):
        """这里只读取视频帧并返回"""
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def capture_image(self):
        """拍照并保存图片"""
        try:
            # 清空摄像头缓冲区，确保获取最新帧
            for _ in range(5):  # 跳过前几帧，确保获取最新图像
                self.cap.grab()
            
            ret, frame = self.cap.read()
            if not ret:
                print("❌ 无法读取摄像头帧")
                return None
            
            # 生成唯一文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"captured_food_{timestamp}.jpg"
            filepath = os.path.join(self.upload_dir, filename)
            
            # 保存图片
            cv2.imwrite(filepath, frame)
            
            print(f"📸 拍照成功: {filepath}")
            print(f"📸 图片尺寸: {frame.shape}")
            return filepath
            
        except Exception as e:
            print(f"❌ 拍照失败: {e}")
            return None

    def run(self):
        """运行视频显示程序"""
        try:
            while True:
                frame = self.detect_and_count_faces()
                if frame is None:
                    break

                cv2.imshow('Video Stream', frame)

                # 按'q'键退出
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        finally:
            self.cap.release()
            cv2.destroyAllWindows()

def main():
    detector = FaceDetector(camera_index=0)
    detector.run()

if __name__ == '__main__':
    main()