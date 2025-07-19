import cv2

class FaceDetector:
    def __init__(self, camera_index=0):
        # 初始化摄像头
        self.cap = cv2.VideoCapture(camera_index)

    def detect_and_count_faces(self):
        """这里只读取视频帧并返回"""
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

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