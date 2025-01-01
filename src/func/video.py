import cv2
import base64
from .queue_storage import frame_queue
import asyncio
class Video:
    def __init__(self, video_path, output_path=None):
        print("Initializing video")
        self.cap = cv2.VideoCapture(video_path)
        ret, self.frame = self.cap.read()
        assert ret
        self.prev_gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
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
        
    def __call__():
        pass

    def is_cap_opended(self):
        return self.cap.isOpened()
    
    async def read(self):
        if self.visualization is not None:
            _, buffer = cv2.imencode('.jpg', self.visualization)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            await frame_queue.put(frame_base64)
            if frame_queue.qsize() > 30:
                await asyncio.sleep(1)
            else:
                await asyncio.sleep(0.01)
        if self.out is not None and self.frame is not None:
            self.out.write(self.frame)
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