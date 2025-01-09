from .video import Video
from vidstab import VidStab
from .utils import add_suffix_to_filename
import cv2
import sys, os
sys.path.append(os.path.join(os.getcwd(),"src"))
from lib.ByteTrack.yolox.tracker.byte_tracker import BYTETracker
from func.YamlParser import YamlParser
from app.schemas import *
from .methods import *
from .roi import *
import json
from pathlib import Path
from strongsort.strong_sort import StrongSORT
import torch
import traceback

async def slungshot(input_path, output_path , options ):
    DetectAlgo = options['algorithm_detect']
    TrackAlgo = options["algorithm_track"]
    
    # if method == 'optical_flow':
    #     if output_path is None:
    #         output_path = add_suffix_to_filename(input_path, "SlungshotOpticalFlow")
    await slungshot_execute(input_path,output_path, DetectAlgo, TrackAlgo)

async def slungshot_execute(input_path, output_path, DetectAlgo, TrackAlgo):
    output_path = add_suffix_to_filename(output_path, DetectAlgo)
    output_path = add_suffix_to_filename(output_path, TrackAlgo)
    file_path = Path(output_path)
    # Replace suffix with a new one
    csv_output_file = file_path.with_suffix(".csv")
    json_output_file = file_path.with_suffix(".json")
    video = Video(input_path, output_path)
    imgHSV = np.zeros_like(video.frame)
    imgHSV[:, :, 1] = 255
    tracking_results = []
    tracker = None 
    #ByteTrack configuration
    class ByteTrackerConfig:
        def __init__(self):
            self.track_thresh = 0.5     # Detection confidence threshold
            self.track_buffer = 300      # Frames to keep lost tracks
            self.match_thresh = 0.8     # Matching threshold
            self.mot20 = True          # Use MOT20 settings for evaluation
    ByteTrack_cfg = ByteTrackerConfig()
    #strongSORT configuration
    tracker_config = "config/strongsort.yaml"
    cfg = YamlParser()
    cfg.merge_from_file(tracker_config)
    reid_weights = Path("weights/osnet_x0_25_msmt17.pt") 
    device = 'cuda'
    while video.is_cap_opended():
        try:
            ret, frame = await video.read()
            if not ret:
                break
            detections = None
            if DetectAlgo == 'FrameDiff':
                detections = detect_by_frame_diff(video.prev_gray, video.gray)
            elif DetectAlgo == 'OpticalFlow':
                detections = detect_by_optical_flow(video.prev_gray, video.gray)
            else:
                raise Exception("DetectAlgo is not available :"+ DetectAlgo)
            
            if TrackAlgo == "ByteTrack":
                if tracker is None :
                    tracker = BYTETracker(ByteTrack_cfg)
                if len(detections)>0:
                    tracks = tracker.update(np.array(detections),(video.width,video.height), (video.width, video.height) )
                    append_track_result_ByteTrack(tracking_results, tracks, video.frame_count)
                    draw_tracks_ByteTrack(frame,tracks)
            elif TrackAlgo == 'StrongSORT':
                if tracker is None :
                    tracker = StrongSORT(
                        reid_weights,
                        torch.device(device),
                        False,
                        max_dist = cfg.strongsort.max_dist,
                        max_iou_distance = cfg.strongsort.max_iou_dist,
                        max_age = cfg.strongsort.max_age,
                        #max_unmatched_preds = cfg.strongsort.max_unmatched_preds,
                        n_init = cfg.strongsort.n_init,
                        nn_budget = cfg.strongsort.nn_budget,
                        mc_lambda = cfg.strongsort.mc_lambda,
                        ema_alpha=cfg.strongsort.ema_alpha,
                    )
                if video.prev_frame is not None and frame is not None:
                    tracker.tracker.camera_update(video.prev_frame, frame) 
                if len(detections)>0:    
                    array2_tiled = np.tile([16], (len(detections), 1))
                    dets = np.hstack((detections,array2_tiled))
                    tensor = torch.from_numpy(np.array(dets))
                    if tensor.shape[0] > 0:
                        outputs = tracker.update(tensor,frame)
                        if len(outputs) > 0:
                            tracks = outputs[:, :6]    
                            append_track_result_strongSORT(tracking_results, outputs, video.frame_count)
                            draw_tracks_strongSORT(frame, tracks)
            elif TrackAlgo == 'DISABLE':
                drawResultOnFrame( detections, frame, DetectAlgo)
            else :
                raise Exception("TrackAlgo is not available :"+ TrackAlgo)
            video.visualization = frame
        except Exception as e:
            print(traceback.format_exc())
            print(e)
            raise e
    video.release()
    if len(tracking_results) > 0:
        save_to_csv(tracking_results, csv_output_file)
        save_to_json(tracking_results, json_output_file)


async def slungshot_OpticalFlow(input_path, output_path):
    video = Video(input_path, output_path)
    imgHSV = np.zeros_like(video.frame)
    imgHSV[:, :, 1] = 255
    while video.is_cap_opended():
        ret, frame = await video.read()
        if not ret:
            break
        flow = calc_optical_flow(video.prev_gray, video.gray)
        mag, ang = cv2.cartToPolar(flow[:, :, 0], flow[:, :, 1])
        # OpenCV H is [0,180] so divid by 2
        imgHSV[:, :, 0] = ang * 180 / np.pi / 2
        normalizedMag = normalize_magnitude(mag)
        imgHSV[:, :, 2] = normalizedMag
        img_BGR = cv2.cvtColor(imgHSV, cv2.COLOR_HSV2BGR)
        img_show = img_BGR + frame
        video.visualization = img_show
    video.release()
    
async def stabilize_vidstab(input_path, output_path):
    video = Video(input_path, output_path)
    stabilizer = VidStab()
    while video.is_cap_opended():
        ret, frame = await video.read()
        if not ret:
            break
        stabilized_frame = stabilizer.stabilize_frame(
            input_frame=frame, smoothing_window=30
        )
        if stabilized_frame is None:
            break
        if stabilized_frame is not None and stabilized_frame.sum() > 0:
            video.visualization = stabilized_frame
    video.release()
    cv2.destroyAllWindows()


async def crop_roi(input_path, output_path, shape, withROI=None):
    print(withROI)
    print(shape)
    if not withROI:
        video = Video(input_path, output_path)
        x = shape[0]["x"]
        y = shape[0]["y"]
        w = shape[0]["w"]
        h = shape[0]["h"]
        video.out = cv2.VideoWriter(output_path, video.fourcc, video.fps, (w, h))
        while True:
            ret, frame = await video.read()
            if not ret:
                break
            cropped_frame = frame[y : y + h, x : x + w].copy()
            video.visualization = cropped_frame
            video.write_frame = cropped_frame
        video.release()
        cv2.destroyAllWindows()
    else:
        s = shape[0]
        bbox = [s['x'],s['y'],s['x']+s['w'],s['y']+s['h']]
        await roi_video(input_path, output_path, bbox)
    print("crop finished")

async def set_pixel(input_path, output_path):
    geo_coords = []
    pixel_coords = []
    all_geo_coords = []
    drillholes = process_file(input_path)
    
    for drill_hole in drillholes:
        if(drill_hole.pixel_x is not None and drill_hole.pixel_x >0 and drill_hole.pixel_y is not None and drill_hole.pixel_y >0):
            pixel_coords.append([drill_hole.pixel_x, drill_hole.pixel_y])
            geo_coords.append([drill_hole.Drillhole_X, drill_hole.Drillhole_Y])
        all_geo_coords.append([drill_hole.Drillhole_X, drill_hole.Drillhole_Y])
    pixel_coords = calc_homography(geo_coords, pixel_coords, np.array(all_geo_coords))
    out = open(output_path, "w")
    holes = []
    for i, drill_hole in enumerate(pixel_coords):
        hole = {'x': drill_hole[0],'y':drill_hole[1], 'r':2, 'type':"circle"}
        holes.append(hole)
    out.write(json.dumps(holes))
    
def process_file(file_path: str) -> List[DrillHole]:
    drillholes = []
    try:
        with open(file_path, 'r') as file:
            header = file.readline()  # Skip the header line
            print(f"Header: {header.strip()}")  # Print the header for debugging
            for line_num, line in enumerate(file, start=2):  # Start from line 2 (skip the header)
                line = line.strip()  # Remove leading/trailing whitespaces or newlines
                if line:  # Ensure there's data in the line
                    print(f"Processing line {line_num}: {line}")  # Debug: print each line
                    drillhole = DrillHole.from_csv(line)
                    if drillhole:
                        drillholes.append(drillhole)
        print(f"Successfully processed {len(drillholes)} drillholes.")
    except Exception as e:
        print(f"Error processing the file: {e}")
    return drillholes