import cv2
import numpy as np
import math
from datetime import datetime

import os, sys
sys.path.append( os.path.join(os.getcwd(), 'src'))
from func.methods import *

class BlastEventDetector:
    def __init__(
        self,
        smoke_threshold=25,
        flyrock_threshold=40,
        min_smoke_area=1000,
        expansion_rate_threshold=0.3,
    ):
        """
        Initialize blast event detector with configurable parameters.

        Args:
            smoke_threshold (int): Threshold for smoke detection (0-255)
            flyrock_threshold (int): Threshold for flyrock detection (0-255)
            min_smoke_area (int): Minimum area to consider as smoke cloud
            expansion_rate_threshold (float): Minimum rate of change for smoke expansion
        """
        self.smoke_threshold = smoke_threshold
        self.flyrock_threshold = flyrock_threshold
        self.min_smoke_area = min_smoke_area
        self.expansion_rate_threshold = expansion_rate_threshold
        self.event_log = []

    def detect_blast_events(self, input_path, output_path, roi=None):
        try:
            cap = cv2.VideoCapture(input_path)
            if not cap.isOpened():
                raise ValueError(f"Error: Could not open video file {input_path}")

            # Video properties
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*"avc1")
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

            # Initialize background subtractor
            backSub = cv2.cuda.createBackgroundSubtractorMOG2(
                history=100, varThreshold=10, detectShadows=False
            )

            # Initialize motion history
            mhi = np.zeros((height, width), dtype=np.float32)
            cumulative = np.zeros((height, width), dtype = np.uint8)
            # Previous frame for optical flow
            ret, prev_frame = cap.read()
            if not ret:
                raise ValueError("Error: Could not read first frame")

            prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Convert to grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # 1. Detect Smoke
                gpu_frame = cv2.cuda_GpuMat()
                gpu_frame.upload(frame)
                fgMask_gpu = backSub.apply(gpu_frame, learningRate=-1, stream=None)
                fgMask = fgMask_gpu.download() 
                # Apply morphological operations to reduce noise
                kernel = np.ones((8, 8), np.uint8)
                fgMask = cv2.morphologyEx(fgMask, cv2.MORPH_OPEN, kernel) #open
                fgMask = cv2.morphologyEx(fgMask, cv2.MORPH_CLOSE, kernel) #close

                # 2. Detect Flyrock using optical flow
                # flow = calc_optical_flow(prev_gray, gray, poly_n=5, poly_sigma=0.8) 
                # magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])

                # # Convert angle to degrees (optional, but makes it easier to understand)
                # angle_degrees = angle * 180 / math.pi
                # downward_threshold_min = 90 - 45 # 45 degree tolerance
                # downward_threshold_max = 90 + 45 # 45 degree tolerance

                # Detect high-velocity objects (potential flyrock) AND downward motion
                # flyrock_mask = (magnitude > self.flyrock_threshold) #& (angle_degrees >= downward_threshold_min) & (angle_degrees <= downward_threshold_max)
                # flyrock_mask_gray = flyrock_mask.astype(np.uint8) * 255
                # overlay = cv2.cvtColor(flyrock_mask_gray, cv2.COLOR_BAYER_BG2BGR)
                # visualization = frame.copy()
                # visualization = cv2.addWeighted(visualization,1,overlay,0.5,0)
                # cv2.imshow("temp", visualization)

                # Update motion history
                # mhi = np.maximum(0, mhi-1)  # Decay factor
                # mhi = np.maximum(mhi, magnitude)

                # Visualization
                visualization = frame.copy()

                # Draw smoke detection
                #cumulative = np.maximum(0, cumulative-1)  # Decay factor
                if is_valid_fgmask(fgMask, 0.2):
                    cumulative = np.maximum(cumulative, fgMask)
                #cumulative = cumulative + fgMask
                smoke_overlay = cv2.cvtColor(cumulative, cv2.COLOR_GRAY2BGR)
                visualization = cv2.addWeighted(visualization, 1, smoke_overlay, 0.8, 0)
                
                #flyrock_overlay = cv2.cvtColor(flyrock_mask_gray, cv2.COLOR_BAYER_BG2BGR)
                
                #visualization = cv2.addWeighted(visualization, 1, flyrock_overlay, 0.3, 0 )
                # Draw flyrock detection
                flyrock_points = np.where(mhi > self.flyrock_threshold)
                for y, x in zip(flyrock_points[0], flyrock_points[1]):
                    cv2.circle(visualization, (x, y), 3, (0, 0, 255), 2)

                # Save and display
                out.write(visualization)
                cv2.imshow("Blast Detection", visualization)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            return True

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return False

        finally:
            if "cap" in locals():
                cap.release()
            if "out" in locals():
                out.release()
            cv2.destroyAllWindows()

    def _save_event_log(self, filename):
        """Save detected events to CSV file"""
        import csv

        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=["time", "frame", "smoke_area", "max_velocity"]
            )
            writer.writeheader()
            writer.writerows(self.event_log)
def is_valid_fgmask(fgMask, threshold=0.7):
    """
    Check if more than `threshold` percentage of pixels in the mask are 255.
    
    Parameters:
    - fgMask: numpy array, the foreground mask.
    - threshold: float, the percentage threshold (0.7 means 70%).
    
    Returns:
    - bool: True if the percentage of 255 pixels > threshold, otherwise False.
    """
    # Count the number of pixels with value 255
    total_pixels = fgMask.size  # Total number of pixels in the mask
    white_pixels = np.sum(fgMask > 200)  # Count pixels with value 255
    
    # Calculate the percentage of white pixels
    white_pixel_ratio = white_pixels / total_pixels
    
    # Check if the ratio exceeds the threshold
    return white_pixel_ratio < threshold
    
# Example usage
if __name__ == "__main__":
    detector = BlastEventDetector(
        smoke_threshold=10, #25
        flyrock_threshold=2,#40
        min_smoke_area=1000,
        expansion_rate_threshold=0.3,
    )

    detector.detect_blast_events(
        "./temp/test_20250114_340_102/340_102_clip_StabVid.mp4",
        "./temp/test_20250114_340_102/340_102_clip_StabVid_smoke_backgroundsubtract.mp4"
    )
