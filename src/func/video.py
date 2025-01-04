import cv2
import base64
from .queue_storage import frame_queue
import asyncio
class Video:
    def __init__(self, video_path, output_path=None):
        print("Initializing video")
        self.cap = cv2.VideoCapture(video_path)
        ret, self.frame = self.cap.read()
        if not ret:
            print("Error: Cannot open video file.")
            exit()
        self.write_frame = None
        self.prev_gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        self.prev_frame = self.frame
        self.gray =None
        self.frame_count = 1
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        #self.fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.fourcc = cv2.VideoWriter_fourcc(*"avc1")
        self.visualization = None
        if output_path is not None:
            self.out = cv2.VideoWriter(output_path, self.fourcc, self.fps, (self.width, self.height))
        else:
            self.out = None
        
    def __call__():
        pass

    def is_cap_opended(self):
        return self.cap.isOpened()
    
    async def read(self,enable_ws=True):
        if self.visualization is not None and enable_ws:
            _, buffer = cv2.imencode('.jpg', self.visualization)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            if frame_queue.qsize() < 30:
                await frame_queue.put(frame_base64)
            await asyncio.sleep(0.01)
        if self.out is not None and (self.frame is not None or self.write_frame is not None):
            if self.write_frame is not None:
                self.out.write(self.write_frame)
                self.write_frame = None
            else:
                self.out.write(self.frame)
        if self.frame is not None:
            self.prev_frame = self.frame
        ret, self.frame = self.cap.read()
        if not ret:
            if not self.is_cap_opended():
                self.out.release()
            return ret, self.frame
        self.frame_count += 1 
        if self.gray is not None:
            self.prev_gray= self.gray
        self.gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        return ret, self.frame
    
    def release(self):
        print("Releasing video")
        self.cap.release()
        if self.out is not None:
            self.out.release()