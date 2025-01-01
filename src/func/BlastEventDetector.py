import cv2
import numpy as np
import math
from datetime import datetime

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
        self.previous_smoke_area = 0
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
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

            # Initialize background subtractor
            backSub = cv2.createBackgroundSubtractorMOG2(
                history=100, varThreshold=50, detectShadows=False
            )

            # Initialize motion history
            mhi = np.zeros((height, width), dtype=np.float32)

            # Previous frame for optical flow
            ret, prev_frame = cap.read()
            if not ret:
                raise ValueError("Error: Could not read first frame")

            prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

            frame_count = 0
            blast_detected = False

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                frame_count += 1
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Apply ROI if specified
                if roi:
                    x, y, w, h = roi
                    analysis_frame = frame[y : y + h, x : x + w]
                else:
                    analysis_frame = frame

                # Convert to grayscale
                gray = cv2.cvtColor(analysis_frame, cv2.COLOR_BGR2GRAY)

                # 1. Detect Smoke
                fgMask = backSub.apply(analysis_frame)

                # Apply morphological operations to reduce noise
                kernel = np.ones((5, 5), np.uint8)
                fgMask = cv2.morphologyEx(fgMask, cv2.MORPH_OPEN, kernel) #open
                fgMask = cv2.morphologyEx(fgMask, cv2.MORPH_CLOSE, kernel) #close

                # Calculate smoke area
                smoke_area = np.sum(fgMask > 0)

                # Calculate expansion rate
                if self.previous_smoke_area > 0:
                    expansion_rate = (
                        smoke_area - self.previous_smoke_area
                    ) / self.previous_smoke_area
                else:
                    expansion_rate = 0

                # 2. Detect Flyrock using optical flow
                flow = self.calcOpticalFlow(prev_gray, gray, poly_n=5, poly_sigma=0.8) 
                magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])

                # Convert angle to degrees (optional, but makes it easier to understand)
                angle_degrees = angle * 180 / math.pi
                downward_threshold_min = 90 - 45 # 45 degree tolerance
                downward_threshold_max = 90 + 45 # 45 degree tolerance

                # Detect high-velocity objects (potential flyrock) AND downward motion
                flyrock_mask = (magnitude > self.flyrock_threshold) & (angle_degrees >= downward_threshold_min) & (angle_degrees <= downward_threshold_max)
                flyrock_mask_gray = flyrock_mask.astype(np.uint8) * 255
                overlay = cv2.cvtColor(flyrock_mask_gray, cv2.COLOR_BAYER_BG2BGR)
                visualization = frame.copy()
                visualization = cv2.addWeighted(visualization,1,overlay,0.5,0)
                cv2.imshow("temp", visualization)

                # Update motion history
                mhi = np.maximum(0, mhi-1)  # Decay factor
                mhi = np.maximum(mhi, magnitude)

                # Detect blast event
                blast_conditions = [
                    smoke_area > self.min_smoke_area,
                    expansion_rate > self.expansion_rate_threshold,
                    np.any(magnitude > self.flyrock_threshold),
                ]

                current_blast_detected = all(blast_conditions)

                if current_blast_detected and not blast_detected:
                    blast_detected = True
                    self.event_log.append(
                        {
                            "time": current_time,
                            "frame": frame_count,
                            "smoke_area": smoke_area,
                            "max_velocity": np.max(magnitude),
                        }
                    )

                # Visualization
                visualization = frame.copy()

                # Draw smoke detection
                smoke_overlay = cv2.cvtColor(fgMask, cv2.COLOR_GRAY2BGR)
                visualization = cv2.addWeighted(visualization, 1, smoke_overlay, 0.3, 0)
                
                flyrock_overlay = cv2.cvtColor(flyrock_mask_gray, cv2.COLOR_BAYER_BG2BGR)
                
                visualization = cv2.addWeighted(visualization, 1, flyrock_overlay, 0.3, 0 )
                # Draw flyrock detection
                flyrock_points = np.where(magnitude > self.flyrock_threshold)
                for y, x in zip(flyrock_points[0], flyrock_points[1]):
                    cv2.circle(visualization, (x, y), 3, (0, 0, 255), -1)

                # Add information overlay
                info_text = [
                    f"Time: {current_time}",
                    f"Smoke Area: {smoke_area:.0f}",
                    f"Expansion Rate: {expansion_rate:.2f}",
                    f"Max Velocity: {np.max(magnitude):.1f}",
                ]

                if current_blast_detected:
                    info_text.append("BLAST EVENT DETECTED!")
                    cv2.putText(
                        visualization,
                        "BLAST EVENT DETECTED!",
                        (10, height - 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 255),
                        2,
                    )

                for i, text in enumerate(info_text):
                    cv2.putText(
                        visualization,
                        text,
                        (10, 30 + i * 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (255, 255, 255),
                        2,
                    )

                # Save and display
                out.write(visualization)
                #cv2.imshow("Blast Detection", visualization)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

                # Update previous frame data
                prev_gray = gray
                self.previous_smoke_area = smoke_area

            # Generate event report
            self._save_event_log(
                f"blast_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )

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

    def calcOpticalFlow(self, prev_gray, gray, pyr_scale = 0.5, levels=3,winsize =15, iterations=3, poly_n =5, poly_sigma=1.2, flags=0):
        if cv2.cuda.getCudaEnabledDeviceCount() > 0 :        
            gpu_previous = cv2.cuda_GpuMat()
            gpu_previous.upload(prev_gray)
            gpu_current= cv2.cuda_GpuMat()
            gpu_current.upload(gray)
            gpu_flow = cv2.cuda.FarnebackOpticalFlow.create(levels, pyr_scale, False, winsize, iterations, poly_n, poly_sigma, flags )
            aflow = cv2.cuda.GpuMat()
            aflow = gpu_flow.calc( gpu_previous, gpu_current, aflow, None )
            flow = aflow.download()
            return flow
        else:
            flow = cv2.calcOpticalFlowFarneback(
                prev_gray,
                gray,
                None,
                pyr_scale=pyr_scale,
                levels=levels,
                winsize=winsize,
                iterations=iterations,
                poly_n=poly_n,
                poly_sigma=poly_sigma,
                flags=flags,
            )
            return flow     
# Example usage
if __name__ == "__main__":
    detector = BlastEventDetector(
        smoke_threshold=10, #25
        flyrock_threshold=5,#40
        min_smoke_area=1000,
        expansion_rate_threshold=0.3,
    )

    detector.detect_blast_events(
        "./temp/340_102_clipped_StabilizeV_ROI_StablizeV.mp4",
        "./temp/blast_detection_output.mp4"
    )
