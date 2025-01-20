import cv2
import numpy as np
import json,csv
import multiprocessing
import os, sys
sys.path.append(os.path.join(os.getcwd(),"src"))
from lib.ByteTrack.yolox.tracker.byte_tracker import STrack

def calc_optical_flow(prev_gray, gray, poly_n=5, poly_sigma=0.8):
    if cv2.cuda.getCudaEnabledDeviceCount() > 0 :      
        #print("calc_optical_flow Using GPU")  
        flow = cv2.calcOpticalFlowFarneback(
            prev_gray,
            gray,
            None,
            pyr_scale=0.5,
            levels=3,
            winsize=15,
            iterations=3,
            poly_n=poly_n,
            poly_sigma=poly_sigma,
            flags=0,
        )
        return flow
    else:
        #print("calc_optical_flow Using CPU")
        gpu_previous = cv2.cuda_GpuMat()
        gpu_previous.upload(prev_gray)
        gpu_current= cv2.cuda_GpuMat()
        gpu_current.upload(gray)
        gpu_flow = cv2.cuda.FarnebackOpticalFlow.create(3, 0.5, False, 15, 3, poly_n, poly_sigma, 0 )
        aflow = cv2.cuda.GpuMat()
        aflow = gpu_flow.calc( gpu_previous, gpu_current, aflow, None )
        flow = aflow.download()
        return flow

def calc_frame_diff(prev_gray, gray):
        diff = cv2.absdiff(prev_gray, gray)
        _, thresh = cv2.threshold(diff, 15, 255, cv2.THRESH_BINARY)
        #thresh = cv2.adaptiveThreshold(diff, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))  # Elliptical kernel of size 5x5
        cleaned_mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
        final_mask = cv2.morphologyEx(cleaned_mask, cv2.MORPH_CLOSE, kernel, iterations=1)

        return final_mask

def detect_by_frame_diff(prev_gray, curr_gray):
    results = calc_frame_diff(prev_gray, curr_gray)
    min_speed =2 # pixel diff between frames
    mask = results > min_speed
    detections = getDetectionsFromMask(mask)
    return np.array(detections)

def detect_by_optical_flow(prev_gray, curr_gray):
    flow = calc_optical_flow(prev_gray, curr_gray)
    # positive_y_flow = np.array(flow.copy())
    # negative_y_flow = flow.copy()
    # positive_y_flow[ positive_y_flow[:, :, 1] < 0 ]  = (0,0)
    # negative_y_flow[negative_y_flow[:, :, 1] > 0] = (0,0)
    use_flow = flow
    mag, ang = cv2.cartToPolar(use_flow[:, :, 0], use_flow[:, :, 1])
    imgHSV = getHSVFromMagAng(mag, ang, threshold=2)
    return detectSlungshotFromFlow(flow, min_speed=2)

def draw_tracks_strongSORT(frame, tracks):
    # Draw tracked objects on the frame
    for track in tracks:
        l = len(track) 
        if l == 6:
            cls = track[5]
            track = track[:5]
        x1, y1, x2, y2, track_id = track
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        if l == 6:
            cv2.putText(frame, f"{cls}-ID: {int(track_id)}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)    
        else:
            cv2.putText(frame, f"ID: {int(track_id)}", (x1, y1 - 10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)    

def draw_tracks_ByteTrack(frame, tracks):
    # Draw tracked objects on the frame
    for track in tracks:
        track_id = track.track_id
        if track_id == 269:
            print(track)
            pass
        bbox = track.tlbr  # Top-left, bottom-right format
        x1, y1, x2, y2 = map(int, bbox)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(frame, f"ID: {track_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
def calc_homography(geo_coords, pixel_coords, all_geo_coords):
    # geo_coords = np.array([
    #     [429273.8, 5266303.1],
    #     [429301.28,5266318.62],
    #     [429237.18,5266366.5],
    #     [429264.41,5266382.41]
    # ])
    # pixel_coords = np.array([
    #     [938,931],
    #     [1370,1106],
    #     [1306,670],
    #     [1736,753]
    # ])
    H, _ = cv2.findHomography(np.array(geo_coords), np.array(pixel_coords), method=0)
    homogeneous_geo_coords = np.hstack([all_geo_coords, np.ones((all_geo_coords.shape[0], 1))])
    mapped_pixels_homogeneous = np.dot(H, homogeneous_geo_coords.T).T
    mapped_pixels = mapped_pixels_homogeneous[:, :2] / mapped_pixels_homogeneous[:, 2][:, np.newaxis]
    for geo, pixel in zip(all_geo_coords, mapped_pixels):
        print(f"Geographic coordinate {geo} maps to pixel coordinate {pixel}")
    return mapped_pixels

def normalize_magnitude(mag, min_output = 0, max_output = 255):
    min_mag = np.min(mag)
    max_mag = np.max(mag)
    normalized_mag = (mag-min_mag) * (max_output - min_output) / (max_mag - min_mag) + min_output
    return normalized_mag.astype(np.uint8)

def getHSVFromMagAng(mag, ang, threshold = 2):
    ang[mag <threshold ] = 0
    mag[mag < threshold] = 0
    imgHSV = np.zeros( mag.shape +(3,) )
    imgHSV[:, :, 1] = 255 #saturation
    # OpenCV H is [0,180] so divid by 2
    imgHSV[:, :, 0] = ang * 180 / np.pi / 2  #hue
    normalizedMag = normalize_magnitude(mag)
    imgHSV[:, :, 2] = normalizedMag #value
    return imgHSV.astype(np.uint8)
    
def detectSlungshotFromFlow(flow, min_speed = 5, min_size =1, max_size = 100):
    # Calculate magnitude and angle of flow vectors
    magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
    # Threshold for fast-moving objects
    motion_mask = magnitude > min_speed
    # Find contours of moving objects
    contours, _ = cv2.findContours(
        motion_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    results = []
    # Filter contours by size
    for contour in contours:
        area = cv2.contourArea(contour)
        if min_size <= area <= max_size * max_size:
            x, y, w, h = cv2.boundingRect(contour)
            # Calculate average magnitude in the region
            roi_magnitude = magnitude[y : y + h, x : x + w]
            avg_magnitude = np.mean(roi_magnitude)
            obj = [x , y,  x+w,  y+h ,  avg_magnitude]
            results.append(obj)
    return results

def getDetectionsFromMask(mask,min_size = 1, max_size = 100):
    contours, _ = cv2.findContours(
        mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    results = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if min_size <= area <= max_size * max_size:
            x, y, w, h = cv2.boundingRect(contour)
            roi_value = mask.astype(np.uint8)[y : y + h, x : x + w]
            avg_value = np.mean(roi_value)
            obj = [x , y, x+w, y+h, avg_value]
            results.append(obj)
    return results

def drawResultOnFrame(result, frame, label= None):
    for obj in result:
        x1, y1, x2, y2 , value= obj 
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)
        if label is not None and value is not None:
            cv2.putText(
                frame,
                f"{label}: {value:.1f}",
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.3,
                (0, 255, 0),
                1,
            )

def ecc_refine_bbox_multiprocessing(prev_gray, curr_gray, detections):
    threads = multiprocessing.cpu_count()
    with multiprocessing.Pool(processes=threads) as pool:
        args_list = [( prev_gray, curr_gray, detection) for detection in detections]
        pool.starmap(ecc_refine_bbox, args_list)

def ecc_refine_bytetrack_multiprocessing(prev_gray, curr_gray, bytetracks):
    threads = multiprocessing.cpu_count()
    remove_track_ids = []
    with multiprocessing.Pool(processes = threads) as pool:
        args_list = [(prev_gray, curr_gray, track) for track in bytetracks]
        remove_track_ids = pool.starmap(ecc_refine_bytetrack, args_list)
        remove_track_ids = np.array(remove_track_ids)
        return remove_track_ids[remove_track_ids != None]

def ecc_refine_bytetrack(prev_frame, curr_frame, track):
    x1,y1,w,h = track.tlwh
    x2 = x1+w
    y2 = y1+h
    bbox = [x1,y1,x2,y2]
    try:
        refined_bbox = ecc_refine_bbox(prev_frame, curr_frame, bbox)
    except Exception as e:
        print(e)
    
    if refined_bbox is None:
        return track.track_id
        pass
    else:
        #track.tlbr = np.array(refined_bbox)
        r_x1, r_y1, r_x2, r_y2 = refined_bbox
        r_w = r_x2 - r_x1
        r_h = r_y2 - r_y1
        refined_tlwh = [r_x1,r_y1, r_w, r_h]
        #track.tlwh = refined_tlwh
        try:
            refined_xyah = STrack.tlwh_to_xyah(np.array(refined_tlwh).astype(float))
            track.mean[:4] = refined_xyah
        except Exception as e:
            print(e)   
    # cx = refined_tlwh[0] + refined_tlwh[2] / 2
    # cy = refined_tlwh[1] + refined_tlwh[3] / 2
    # aspect_ratio = refined_tlwh[2] / refined_tlwh[3]
    # height = refined_tlwh[3]
    # track.mean[:4] = [cx, cy, aspect_ratio, height]

    # Optional: Adjust confidence score
    #track.score = min(track.score + 0.05, 1.0)
    
def ecc_refine_bbox(prev_frame, curr_frame, prev_bbox):
    # Extract ROI from the previous frame
    value = 0
    len_prev_bbox = len(prev_bbox)
    if len_prev_bbox == 5:
        value = prev_bbox[4]
        prev_bbox = prev_bbox[:4]
    if not hasattr(prev_bbox, 'astype'):
        prev_bbox = np.array(prev_bbox)
    x, y, w, h = prev_bbox.astype(int)
    prev_roi = prev_frame[y:y+h, x:x+w]
    curr_roi = curr_frame[y:y+h, x:x+w]

    # Define warp matrix (affine transformation)
    warp_matrix = np.eye(2, 3, dtype=np.float32)

    # Set ECC criteria
    # Criteria: Adjust the iteration count and epsilon for performance vs. accuracy trade-offs.
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 50, 1e-6)

    # Align current frame ROI to the previous frame ROI
    try:
        #Warp Type: Use cv2.MOTION_TRANSLATION, cv2.MOTION_AFFINE, or cv2.MOTION_HOMOGRAPHY depending on the motion complexity.
        score, warp_matrix = cv2.findTransformECC(
            prev_roi, curr_roi, warp_matrix, cv2.MOTION_TRANSLATION, criteria
        )
        # if(score < 0.9):
        #     return None
    except cv2.error as e:
        print(e)
        # Return the original bounding box if ECC fails
        return None

    # Update the bounding box based on the warp matrix
    dx, dy = warp_matrix[0, 2], warp_matrix[1, 2]
    new_bbox = [int(x + dx), int(y + dy), w, h]
    if len_prev_bbox ==5:
        new_bbox.append(value)
    return new_bbox

def ecc_validate_track(prev_frame, curr_frame, track_bbox):
    x, y, w, h = track_bbox
    prev_roi = prev_frame[y:y+h, x:x+w]
    curr_roi = curr_frame[y:y+h, x:x+w]

    # Compute ECC similarity
    warp_matrix = np.eye(2, 3, dtype=np.float32)
    try:
        score, _ = cv2.findTransformECC(prev_roi, curr_roi, warp_matrix, cv2.MOTION_TRANSLATION)
        return score > 0.9  # Threshold for valid track
    except cv2.error:
        return False

def ecc_smooth_trajectory(tracks, window_size=5):
    """
    Smooths the trajectory of tracked objects using a sliding window.

    Args:
        tracks (list): List of tracked objects with bounding boxes over frames.
        window_size (int): Number of frames to average for smoothing.

    Returns:
        list: Smoothed tracks.
    """
    smoothed_tracks = []
    for track_id in range(len(tracks)):
        trajectory = [t['bbox'] for t in tracks[track_id][-window_size:]]
        if len(trajectory) > 1:
            avg_x = int(sum(b[0] for b in trajectory) / len(trajectory))
            avg_y = int(sum(b[1] for b in trajectory) / len(trajectory))
            avg_w = int(sum(b[2] for b in trajectory) / len(trajectory))
            avg_h = int(sum(b[3] for b in trajectory) / len(trajectory))
            tracks[track_id][-1]['bbox'] = (avg_x, avg_y, avg_w, avg_h)
        smoothed_tracks.append(tracks[track_id])
    return smoothed_tracks

def ecc_filter_noisy_tracks(prev_frame, curr_frame, tracks, threshold=0.8):
    """
    Filters tracks that have low ECC similarity scores.

    Args:
        prev_frame (np.array): Previous frame (grayscale).
        curr_frame (np.array): Current frame (grayscale).
        tracks (list): List of tracked objects.
        threshold (float): Minimum ECC score for a valid track.

    Returns:
        list: Filtered tracks.
    """
    valid_tracks = []
    for track in tracks:
        score = ecc_validate_track(prev_frame, curr_frame, track['bbox'])
        if score >= threshold:
            valid_tracks.append(track)
    return valid_tracks

def append_track_result_ByteTrack(tracking_results, tracks, frame_id):
    for t in tracks:
        result = {
            'frame_id': frame_id,
            'track_id': t.track_id,
            'x1': t.tlwh[0],
            'y1': t.tlwh[1],
            'x2': t.tlwh[0] + t.tlwh[2],
            'y2': t.tlwh[1] + t.tlwh[3],
            'confidence': t.score,
            'class':   t.cls if hasattr(t,"cls") else ''
        }
        tracking_results.append(result)

def append_track_result_strongSORT(tracking_results, tracks, frame_id):
    for t in tracks:
        result = {
            'frame_id': frame_id,
            'track_id': t[4],
            'x1': t[0],
            'y1': t[1],
            'x2': t[2],
            'y2': t[3],
            'confidence': t[6],
            'class':   t[5]
        }
        tracking_results.append(result)

# Function to save tracking results to a CSV file
def save_to_csv(tracking_results, output_file):
    """
    Save tracking results to a CSV file.

    Parameters:
        tracking_results (list): List of dictionaries containing tracking data.
        output_file (str): Path to the CSV file.
    """
    with open(output_file, mode='w', newline='') as csvfile:
        fieldnames = ['frame_id', 'track_id', 'x1', 'y1', 'x2', 'y2', 'confidence', 'class']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for result in tracking_results:
            writer.writerow(result)

# Function to save tracking results to a JSON file
def save_to_json(tracking_results, output_file):
    """
    Save tracking results to a JSON file.

    Parameters:
        tracking_results (list): List of dictionaries containing tracking data.
        output_file (str): Path to the JSON file.
    """
    with open(output_file, mode='w') as jsonfile:
        json.dump(tracking_results, jsonfile, indent=4)

if __name__ == "__main__":
    mapped_pixels = calc_homography(None, None, None)
    json_output = []
    for pixel in mapped_pixels:
        point = {"x": pixel[0], "y": pixel[1], "type": "point"}
        json_output.append(point)
    output = open("json_output.json", "w")
    output.write(json.dumps(json_output))