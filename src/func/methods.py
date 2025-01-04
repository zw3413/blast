import cv2
import numpy as np
import json

def calc_optical_flow(prev_gray, gray):
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
            poly_n=5,
            poly_sigma=1.2,
            flags=0,
        )
        return flow
    else:
        #print("calc_optical_flow Using CPU")
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

# def extract_object(mask, min_size=0, max_size=np.inf):
#     contours, _ = cv2.findContours(
#         mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
#     )
#     objects = []
#     for contour in contours:
#         area = cv2.contourArea(contour)
#         if  min_size <= area <= max_size * max_size:
#             x, y, w, h = cv2.boundingRect(contour)
#             obj = [x,y,x+w,y+h,0.99]
#             objects.append(obj)
#     return np.array(objects)

def draw_tracks(frame, tracks):
    # Draw tracked objects on the frame
    for track in tracks:
        x1, y1, x2, y2, track_id = track
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(frame, f"ID: {int(track_id)}", (x1, y1 - 10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)    
        
def calc_homography(geo_coords, pixel_coords, all_geo_coords):
    # Step 1: Input data
    # Geographic coordinates (latitude, longitude) for 4 known points
    geo_coords = np.array([
        [429273.8, 5266303.1],
        [429301.28,5266318.62],
        [429237.18,5266366.5],
        [429264.41,5266382.41]
    ])
    # Corresponding pixel coordinates on the drone footage
    pixel_coords = np.array([
        [938,931],
        [1370,1106],
        [1306,670],
        [1736,753]
    ])
    # All geographic coordinates that need to be mapped to pixels
    all_geo_coords = np.array([
        [429273.8,5266303.1],
        [429278.4,5266305.26],
        [429282.98,5266307.93],
        [429287.55,5266310.6],
        [429292.13,5266313.28],
        [429296.71,5266315.95],
        [429301.28,5266318.62],
        [429273.79,5266307.89],
        [429278.37,5266310.56],
        [429282.95,5266313.24],
        [429287.52,5266315.91],
        [429292.1,5266318.58],
        [429296.67,5266321.26],
        [429269.18,5266310.53],
        [429273.76,5266313.2],
        [429278.34,5266315.87],
        [429282.96,5266318.73],
        [429287.4,5266321.27],
        [429292.07,5266323.89],
        [429296.64,5266326.57],
        [429269.15,5266315.83],
        [429273.73,5266318.51],
        [429278.3,5266321.18],
        [429282.35,5266324.86],
        [429287.46,5266326.53],
        [429292.03,5266329.2],
        [429265.22,5266318.63],
        [429269.12,5266321.14],
        [429273.7,5266323.82],
        [429278.27,5266326.49],
        [429282.85,5266329.16],
        [429287.42,5266331.84],
        [429292,5266334.51],
        [429264.51,5266323.78],
        [429269.09,5266326.45],
        [429273.66,5266329.12],
        [429278.24,5266331.8],
        [429282.82,5266334.47],
        [429287.39,5266337.15],
        [429259.9,5266326.41],
        [429264.48,5266329.09],
        [429269.06,5266331.76],
        [429273.63,5266334.43],
        [429278.21,5266337.11],
        [429282.78,5266339.78],
        [429287.36,5266342.45],
        [429259.87,5266331.72],
        [429264.45,5266334.39],
        [429269.02,5266337.07],
        [429273.6,5266339.74],
        [429278.18,5266342.42],
        [429282.75,5266345.09],
        [429256.01,5266333.57],
        [429259.84,5266337.03],
        [429264.41,5266339.7],
        [429268.99,5266342.38],
        [429273.57,5266345.05],
        [429278.14,5266347.72],
        [429282.72,5266350.4],
        [429255.23,5266339.66],
        [429259.81,5266342.34],
        [429264.38,5266345.01],
        [429268.96,5266347.69],
        [429274.1,5266350.34],
        [429278.07,5266354.15],
        [429250.62,5266342.3],
        [429255.2,5266344.97],
        [429259.77,5266347.65],
        [429264.35,5266350.32],
        [429268.93,5266352.99],
        [429274.05,5266354.96],
        [429278.08,5266358.34],
        [429250.59,5266347.61],
        [429255.16,5266350.28],
        [429259.74,5266352.96],
        [429264.32,5266355.63],
        [429268.89,5266358.3],
        [429273.47,5266360.98],
        [429246.57,5266350.19],
        [429250.56,5266352.92],
        [429255.13,5266355.59],
        [429259.71,5266358.26],
        [429264.28,5266360.94],
        [429268.86,5266363.61],
        [429273.44,5266366.29],
        [429245.95,5266355.55],
        [429250.52,5266358.23],
        [429255.1,5266360.9],
        [429259.68,5266363.57],
        [429264.25,5266366.25],
        [429268.83,5266368.92],
        [429241.34,5266358.19],
        [429245.92,5266360.86],
        [429250.49,5266363.53],
        [429255.07,5266366.21],
        [429259.64,5266368.88],
        [429264.22,5266371.56],
        [429268.8,5266374.23],
        [429241.31,5266363.5],
        [429245.57,5266365.85],
        [429250.46,5266368.84],
        [429255.04,5266371.52],
        [429259.61,5266374.19],
        [429264.19,5266376.86],
        [429237.18,5266366.5],
        [429241.27,5266368.8],
        [429245.85,5266371.48],
        [429250.43,5266374.15],
        [429255,5266376.83],
        [429259.58,5266379.5],
        [429264.41,5266382.41]
        # Add more coordinates as needed
    ])
    # Step 2: Compute the homography matrix
    # Convert the coordinates to the appropriate shape
    H, _ = cv2.findHomography(geo_coords, pixel_coords, method=0)
    # Step 3: Map other geographic coordinates to pixel coordinates
    # Add a column of ones to make the coordinates homogeneous
    homogeneous_geo_coords = np.hstack([all_geo_coords, np.ones((all_geo_coords.shape[0], 1))])
    # Transform the geographic coordinates to pixel coordinates
    mapped_pixels_homogeneous = np.dot(H, homogeneous_geo_coords.T).T
    # Convert from homogeneous coordinates back to 2D
    mapped_pixels = mapped_pixels_homogeneous[:, :2] / mapped_pixels_homogeneous[:, 2][:, np.newaxis]
    # Step 4: Output the results
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
                obj = {"x1":x , "y1":y, "x2": x+w, "y2": y+h , "value": avg_magnitude}
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

if __name__ == "__main__":
    mapped_pixels = calc_homography(None, None, None)
    json_output = []
    for pixel in mapped_pixels:
        point = {"x": pixel[0], "y": pixel[1], "type": "point"}
        json_output.append(point)
    output = open("json_output.json", "w")
    output.write(json.dumps(json_output))