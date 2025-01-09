import cv2
import numpy as np
import sys, os
sys.path.append(os.path.join(os.getcwd(),"src"))
from func.video import Video

async def roi_video(input_path, output_path, bbox= None):
    video = Video(input_path)
    # Initialize object tracker, stabilizer, and video reader
    param_handler = cv2.TrackerCSRT_Params()
    setattr(param_handler, "psr_threshold", 0.025)
    setattr(param_handler, "template_size", 500)
    setattr(param_handler, "use_hog", True)
    setattr(param_handler, "use_color_names", True)
    setattr(param_handler, "use_rgb", True)
    setattr(param_handler, "use_gray", False)
    setattr(param_handler, "use_channel_weights", True)
    setattr(param_handler, "use_segmentation", True)
    object_tracker = cv2.TrackerCSRT_create(param_handler)

    # Initialize bounding box for drawing rectangle around tracked object
    object_bounding_box = None
    roi_h = 0
    roi_w = 0
    out = None
    try:
        while video.is_cap_opended():
            ret, frame = await video.read()
            if not ret:
                break
            if frame is None:
                break
            out_frame = None
            
            # Select ROI for tracking and begin object tracking
            if object_bounding_box is None and bbox is None:
                object_bounding_box = cv2.selectROI(
                    "Select ROI", frame, fromCenter=False, showCrosshair=True
                )
                object_bounding_box = clip_bounding_box( tuple( np.array(bbox) + np.array((-20, -20, 40, 40)) ), video.width, video.height)
                
                object_tracker.init(frame, object_bounding_box)
                cv2.destroyAllWindows()
            elif object_bounding_box is None and bbox is not None:
                #object_bounding_box = clip_bounding_box( tuple( np.array(bbox) + np.array((-20, -20, 40, 40)) ), video.width, video.height)
                object_bounding_box = bbox
                object_tracker.init(frame, object_bounding_box)
            else:
                # Draw rectangle around tracked object if tracking has started
                success, object_bounding_box = object_tracker.update(frame)

                if success:
                    (x, y, w, h) = [int(v) for v in object_bounding_box]
                    if out is None:
                        roi_h = h
                        roi_w = w
                        out = cv2.VideoWriter(output_path, video.fourcc, video.fps, (roi_w, roi_h))
                    x = int(((w) / 2 + x) - roi_w / 2)
                    y = int(((h) / 2 + y) - roi_h / 2)
                    #cv2.rectangle(frame, (x, y), (x + roi_w, y + roi_h), (0, 255, 0), 2)
                    out_frame = frame[y : y + roi_h, x : x + roi_w].copy()

            if out_frame is not None:
                out_frame = crop_frame_with_buffer(frame, object_bounding_box, -20)
                video.visualization = out_frame
                # cv2.imshow("ROI", out_frame)
                # key = cv2.waitKey(1)
                # if key == 27:
                #     break
                if out is not None:
                    out.write(out_frame)
            else:
                if out is not None:
                    break
                else:
                    print("ROI: lost frame may occured.")
    except Exception as e:
        print("ROI crop error:")
        print(e)
    if out is not None:
        out.release()
    cv2.destroyAllWindows()
    
def crop_frame_with_buffer(frame, bounding_box, buffer_size):
    """Crops a frame around a bounding box with a specified buffer.
    Args:
        frame: The input frame (NumPy array).
        bounding_box: A list or tuple representing the bounding box [x, y, w, h].
        buffer_size: The buffer size to add around the bounding box (integer).
    Returns:
        The cropped frame (NumPy array), or None if the cropping is invalid.
    """
    x, y, w, h = bounding_box
    # Calculate buffered coordinates
    x1 = x - buffer_size
    y1 = y - buffer_size
    x2 = x + w + buffer_size
    y2 = y + h + buffer_size
    # Clip coordinates to frame boundaries
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(frame.shape[1], x2)  # frame.shape[1] is width
    y2 = min(frame.shape[0], y2)  # frame.shape[0] is height
    # Check for invalid cropping (e.g., negative width or height)
    if x1 >= x2 or y1 >= y2:
        print("Error: Invalid cropping region.")
        return None

    # Crop the frame
    cropped_frame = frame[y1:y2, x1:x2]
    return cropped_frame

def clip_bounding_box(bounding_box, frame_width, frame_height):
    """Clips a bounding box to the frame dimensions.
    Args:
        bounding_box: A list or tuple representing the bounding box [x, y, w, h].
        frame_width: Width of the frame.
        frame_height: Height of the frame.
    Returns:
        A clipped bounding box [x, y, w, h].
    """
    x, y, w, h = bounding_box
    # Clip x and y to be within the frame
    x = max(0, x)
    y = max(0, y)
    # Clip width and height so that the bounding box stays within the frame
    w = min(frame_width - x, w)
    h = min(frame_height - y, h)
    return [x, y, w, h]