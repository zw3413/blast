import cv2
import numpy as np


def detect_tiny_flyrock(video_path, output_path, min_size=2, max_size=5, min_speed=5):
    """
    Detect very small, fast-moving objects (flyrock) in video

    Parameters:
    video_path (str): Path to the video file
    min_size (int): Minimum object size in pixels
    max_size (int): Maximum object size in pixels
    min_speed (int): Minimum pixel movement between frames to be considered
    """
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    # Read first frame
    ret, prev_frame = cap.read()
    if not ret:
        return

    # Convert to grayscale
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert current frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Calculate magnitude and angle of flow vectors
        magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])

        # Threshold for fast-moving objects
        motion_mask = magnitude > min_speed

        # Find contours of moving objects
        contours, _ = cv2.findContours(
            motion_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # Filter contours by size
        for contour in contours:
            area = cv2.contourArea(contour)
            if min_size <= area <= max_size * max_size:
                x, y, w, h = cv2.boundingRect(contour)

                # Calculate average magnitude in the region
                roi_magnitude = magnitude[y : y + h, x : x + w]
                avg_magnitude = np.mean(roi_magnitude)

                # If movement is significant, mark as potential flyrock
                if avg_magnitude > min_speed:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
                    cv2.putText(
                        frame,
                        f"Speed: {avg_magnitude:.1f}",
                        (x, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.3,
                        (0, 255, 0),
                        1,
                    )

        # Display the frame
        cv2.imshow("Flyrock Detection", frame)
        out.write(frame)
        # Update previous frame
        prev_gray = gray.copy()

        if cv2.waitKey(5) & 0xFF == ord("q"):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()


# Parameters can be adjusted based on your specific case
path = "./temp/340_102_clipped_StabilizeV_ROI_StablizeV.mp4"
output = "./temp/motion_detect.mp4"
detect_tiny_flyrock(path, output, min_size=1, max_size=20, min_speed=2)
