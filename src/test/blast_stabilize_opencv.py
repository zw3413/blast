import cv2
import numpy as np

# Create a VideoCapture object to read the input video
input_video_path = "input_video.mp4"
output_video_path = "stabilized_video.mp4"
cap = cv2.VideoCapture(input_video_path)

# Check if the video opened successfully
if not cap.isOpened():
    print("Error: Cannot open video file.")
    exit()

# Get video properties
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Define the codec and create a VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

# Initialize transformation matrices
prev_gray = None
transform_accumulated = np.zeros((2, 3), np.float32)
stabilized_frames = []

# Stabilization loop
for i in range(frame_count):
    ret, frame = cap.read()
    if not ret:
        break

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if prev_gray is not None:
        # Calculate optical flow (dense flow)
        prev_pts = cv2.goodFeaturesToTrack(prev_gray, maxCorners=200, qualityLevel=0.01, minDistance=30)
        next_pts, status, _ = cv2.calcOpticalFlowPyrLK(prev_gray, gray, prev_pts, None)

        # Keep only good points
        good_prev_pts = prev_pts[status == 1]
        good_next_pts = next_pts[status == 1]

        # Estimate rigid transform
        transform_matrix, _ = cv2.estimateAffinePartial2D(good_prev_pts, good_next_pts)

        if transform_matrix is not None:
            # Accumulate the transformation
            transform_accumulated += transform_matrix

            # Apply the transformation to stabilize the frame
            stabilized_frame = cv2.warpAffine(frame, transform_accumulated, (frame_width, frame_height),
                                              flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
            stabilized_frames.append(stabilized_frame)
        else:
            stabilized_frames.append(frame)
    else:
        stabilized_frames.append(frame)

    prev_gray = gray

# Write stabilized frames to output video
for frame in stabilized_frames:
    out.write(frame)

# Release resources
cap.release()
out.release()
print(f"Stabilized video saved to {output_video_path}")
