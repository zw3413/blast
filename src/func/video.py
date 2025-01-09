import cv2
import base64
import os, sys
sys.path.append(os.path.join(os.getcwd(),"src"))
from func.queue_storage import FrameQueueSingleton
import asyncio
from func.utils import temp_video_path, copy_file_non_blocking
import shutil

class Video:
    def __init__(self, video_path, output_path=None):
        print("Initializing video")
        # put video file copy to a temp folder
        self.temp_video_path = temp_video_path(video_path)
        #self.temp_video_path = '/home/elvin/blast/temp/test_20250107_1/temp/340_102.MP4'
        try:
            copy_file_non_blocking(video_path, self.temp_video_path)
            self.cap = cv2.VideoCapture(self.temp_video_path)
        except Exception as e:
            print("open video file failed.")
            print(e)
        ret, self.frame = self.cap.read()
        if not ret:
            print("Error: Cannot open video file.")
            exit()
        self.write_frame = None
        self.prev_gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        self.prev_frame = self.frame
        self.gray =None
        self.frame_count = 0
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        #self.fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.fourcc = cv2.VideoWriter_fourcc(*"avc1")
        self.visualization = None
        self.frame_queue = FrameQueueSingleton.get_queue()
        print("Video:",self.frame_queue.qsize())
        print(f"Queue ID: {id(self.frame_queue)}")
        print(f"Event loop ID: {id(asyncio.get_event_loop())}")       
        if output_path is not None:
            try:
                self.out = cv2.VideoWriter(output_path, self.fourcc, self.fps, (self.width, self.height))
            except Exception as e:
                print("initialize video out failed.")
                print(e)
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
            if self.frame_queue.qsize() < 30:
                await self.frame_queue.put(frame_base64)
                await asyncio.sleep(0.01)
            else:
                pass
                #await asyncio.sleep(0.1)
        if self.out is not None and (self.frame is not None or self.write_frame is not None):
            if self.write_frame is not None:
                self.out.write(self.write_frame)
            else:
                self.out.write(self.frame)
        if self.frame is not None:
            self.prev_frame = self.frame
        ret, self.frame = self.cap.read()
        if not ret:
            try:
                #self.out.release()
                pass
            except Exception as e:
                print(e)
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
        try:
            os.remove(self.temp_video_path)
        except Exception as e:
            print(e)