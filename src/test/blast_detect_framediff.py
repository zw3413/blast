import asyncio
import cv2
import numpy as np
import os,sys
sys.path.append(os.path.join(os.getcwd(),"src"))
from func.methods import *
from func.video import Video
from func.utils import add_suffix_to_filename

async def movediff_video(input_path, output_path=None):
    if output_path is None:
        output_path = add_suffix_to_filename(input_path, "FrameDiff")
    video = Video(input_path, output_path)
    while True:
        ret, frame = await video.read(enable_ws=False)
        if not ret:
            break
        results = calc_frame_diff(video.prev_gray, video.gray)

        mask = results > 2
        results = getDetectionsFromMask(mask)
        drawResultOnFrame(results, frame, "Diff")
        
        video.visualization = frame
        cv2.imshow('slungshot_OpticalFlow', frame)
        cv2.waitKey(1)
    video.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    path = "./temp/123/340_102_clipped_ROI_stabv.mp4"
    asyncio.run(movediff_video(path))
