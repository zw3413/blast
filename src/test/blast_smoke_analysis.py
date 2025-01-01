import cv2
import numpy as np
from scipy.spatial.distance import euclidean

def analyze_blast_smoke(video_path, ground_level=None):
    """
    Analyze blast smoke characteristics including height, area, and color analysis
    
    Parameters:
    video_path (str): Path to the video file
    ground_level (int): Y-coordinate of ground level (if None, will use bottom of frame)
    """
    cap = cv2.VideoCapture(video_path)
    
    # Get video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    if ground_level is None:
        ground_level = frame_height - 50  # Default to near bottom of frame

    def detect_smoke(frame):
        # Convert to HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Define range for smoke detection (greyish to orange)
        # Adjusted to include orange tones
        lower_bound = np.array([0, 20, 20])
        upper_bound = np.array([30, 255, 255])
        
        # Create mask for smoke
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        
        # Apply morphological operations to reduce noise
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        return mask

    def analyze_color(frame, mask):
        # Convert to HSV for better color analysis
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Get pixels where smoke is detected
        smoke_pixels = hsv[mask > 0]
        
        if len(smoke_pixels) == 0:
            return 0, 0  # No smoke detected
        
        # Calculate average hue and saturation
        avg_hue = np.mean(smoke_pixels[:, 0])
        avg_saturation = np.mean(smoke_pixels[:, 1])
        
        # Calculate orange intensity (closer to orange hue = more toxic)
        orange_hue = 15  # Orange hue value in HSV
        toxicity = (1 - abs(avg_hue - orange_hue) / 180) * 100  # Normalize to percentage
        
        # Saturation indicates concentration
        concentration = (avg_saturation / 255) * 100  # Normalize to percentage
        
        return toxicity, concentration

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Detect smoke
        smoke_mask = detect_smoke(frame)
        
        # Find contours of smoke
        contours, _ = cv2.findContours(smoke_mask, cv2.RETR_EXTERNAL, 
                                     cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Find the largest contour (main smoke plume)
            main_contour = max(contours, key=cv2.contourArea)
            
            # Calculate area
            area_pixels = cv2.contourArea(main_contour)
            
            # Find highest point of smoke
            top_point = tuple(main_contour[main_contour[:, :, 1].argmin()][0])
            height_pixels = ground_level - top_point[1]
            
            # Analyze color characteristics
            toxicity, concentration = analyze_color(frame, smoke_mask)
            
            # Draw measurements on frame
            cv2.drawContours(frame, [main_contour], -1, (0, 255, 0), 2)
            cv2.line(frame, (top_point[0], ground_level), 
                    top_point, (255, 0, 0), 2)
            
            # Add text measurements
            cv2.putText(frame, f'Height: {height_pixels}px', (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame, f'Area: {int(area_pixels)}px^2', (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame, f'Toxicity: {toxicity:.1f}%', (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame, f'Concentration: {concentration:.1f}%', (10, 150), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # Draw ground level line
            cv2.line(frame, (0, ground_level), (frame_width, ground_level), 
                    (0, 0, 255), 2)
        
        # Display the frame
        cv2.imshow('Blast Smoke Analysis', frame)
        
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

# Example calibration values for real-world measurements
PIXELS_PER_METER = 50  # This needs to be calibrated for your specific setup

def convert_to_real_measurements(pixels, pixels_per_meter):
    """Convert pixel measurements to real-world units"""
    return pixels / pixels_per_meter

# Example usage
analyze_blast_smoke('./temp/340_102_clipped_StabilizeV_ROI_StablizeV.mp4', ground_level=800)