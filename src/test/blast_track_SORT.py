
import os, sys
sys.path.append(os.path.join(os.getcwd(),"src"))
from func.methods import calc_frame_diff, extract_object, draw_tracks
from func.video import Video
from lib.sort import Sort  # SORT library
import cv2
import numpy as np

tracker = Sort(max_age=30, min_hits=3, iou_threshold=0.3)

# Function to simulate object detection (replace with actual detections)
def detect_objects(frame):
    # Example detections for demonstration: [x1, y1, x2, y2, confidence]
    detections = [
        [100, 150, 200, 250, 0.9],  # Object 1
        [300, 350, 400, 450, 0.85]  # Object 2
    ]
    return np.array(detections)

# Load video
video_path = "./temp/340_102_clipped_StabilizeV_ROI_StablizeV.mp4"  # Replace with your video path
output_path = "./temp/blast_track_SORT.mp4"
video = Video(video_path, output_path)

while video.is_cap_opended():
    ret, frame = video.read()
    if not ret:
        break

    results = calc_frame_diff(video.prev_gray, video.gray)
    detections = extract_object(results,1,20)

    try:
        tracks = tracker.update(detections)
        draw_tracks(frame,tracks)
    except Exception as e:
        print(e)

    # Display the frame
    cv2.imshow("SORT Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    video.out.write(frame)
    video.frame = frame

cv2.destroyAllWindows()
