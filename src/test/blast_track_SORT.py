
import asyncio
import os, sys
sys.path.append(os.path.join(os.getcwd(),"src"))
from func.methods import *
from func.video import Video
from func.utils import add_suffix_to_filename
from lib.sort import Sort  # SORT library
import cv2
import numpy as np

tracker = Sort(max_age=100, min_hits=5, iou_threshold=0.1)

async def track_SORT(input_path, output_path=None):
    if output_path is None:
        output_path = add_suffix_to_filename(input_path, "TrackSORT")
    video = Video(input_path, output_path)
    while True:
        ret, frame = await video.read(enable_ws=False)
        if not ret:
            break
        results = calc_frame_diff(video.prev_gray, video.gray)

        mask = results > 2
        detections = getDetectionsFromMask(mask)
        drawResultOnFrame(detections, frame, "Diff")
        try:
            tracks = tracker.update(np.array(detections))
            draw_tracks(frame, tracks)
        except Exception as e:
            print(e)        
        video.visualization = frame
        cv2.imshow('SORT Tracking', frame)
        cv2.waitKey(1)
    video.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    path = "./temp/123/340_102_clipped_ROI_stabv.mp4"
    asyncio.run(track_SORT(path))