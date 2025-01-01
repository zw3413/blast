import cv2
import numpy as np

def calc_optical_flow(prev_gray, gray):
    if cv2.cuda.getCudaEnabledDeviceCount() > 0 :        
        flow = cv2.calcOpticalFlowFarneback(
            prev_gray,
            gray,
            None,
            pyr_scale=0.5,
            levels=3,
            winsize=15,
            iterations=3,
            poly_n=5,
            poly_sigma=1.2,
            flags=0,
        )
        return flow
    else:
        gpu_previous = cv2.cuda_GpuMat()
        gpu_previous.upload(prev_gray)
        gpu_current= cv2.cuda_GpuMat()
        gpu_current.upload(gray)
        gpu_flow = cv2.cuda.FarnebackOpticalFlow.create(3, 0.5, False, 15, 3, 5, 1.1, 0 )
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

def extract_object(mask, min_size=0, max_size=np.inf):
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    objects = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if  min_size <= area <= max_size * max_size:
            x, y, w, h = cv2.boundingRect(contour)
            obj = [x,y,x+w,y+h,0.99]
            objects.append(obj)
    return np.array(objects)

def draw_tracks(frame, tracks):
    # Draw tracked objects on the frame
    for track in tracks:
        x1, y1, x2, y2, track_id = track
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f"ID: {int(track_id)}", (x1, y1 - 10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        
