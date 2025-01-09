
import asyncio
import os, sys
sys.path.append(os.path.join(os.getcwd(),"src"))
from lib.ByteTrack.yolox.tracker.byte_tracker import BYTETracker
from func.utils import add_suffix_to_filename
from func.methods import *
from func.video import Video
from func.PanZoomWindow import PanZoomWindow
import numpy as np
import cv2
from PIL import Image

# Initialize ByteTrack with configuration
class TrackerConfig:
    def __init__(self):
        self.track_thresh = 0.5     # Detection confidence threshold
        self.track_buffer = 300      # Frames to keep lost tracks
        self.match_thresh = 0.8     # Matching threshold
        self.mot20 = True          # Use MOT20 settings for evaluation

tracker_cfg = TrackerConfig()

tracker = BYTETracker(tracker_cfg)

async def track_ByteTrack(input_path, output_path=None):
    if output_path is None:
        output_path = add_suffix_to_filename(input_path, "ByteTrack_preecc")
    video = Video(input_path, output_path)
    while True:
        ret, frame = await video.read(enable_ws=False)
        if not ret:
            break
        results = calc_frame_diff(video.prev_gray, video.gray)
        min_speed =2 # pixel diff between frames
        mask = results > min_speed
        detections = getDetectionsFromMask(mask)
        detections = np.array(detections)
        #drawResultOnFrame(detections, frame, "Diff")
        try:
            detections = np.array(detections)
            if video.prev_gray is not None:
                ecc_refine_bbox_multiprocessing(video.prev_gray, video.gray, detections)
            tracks = tracker.update(detections,(video.width,video.height), (video.width, video.height) )
            # min_frames= 10
            # valid_tracks = [track for track in tracks if track.frame_id >= min_frames]
            
            if video.prev_gray is not None:
                #detections = ecc_refine_bbox_multiprocessing(video.prev_gray, video.gray, detections)
                remove_track_ids = ecc_refine_bytetrack_multiprocessing(video.prev_gray, video.gray, tracks)
                
            if remove_track_ids.size > 0 :
                filtered_tracks = [track for track in tracks if track.track_id in remove_track_ids]
                print(remove_track_ids, filtered_tracks[0].tlwh)
            draw_tracks_ByteTrack(frame, tracks)
        except Exception as e:
            print(e)        
        video.visualization = frame
        cv2.imshow('SORT Tracking', frame)
        cv2.waitKey(1)
    video.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    path = "./temp/123/340_102_clipped_ROI_stabv.mp4"
    asyncio.run(track_ByteTrack(path))