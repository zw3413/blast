import cv2
import numpy as np
from deep_sort.deep_sort import DeepSort

# Initialize DeepSORT
deepsort = DeepSort(
    model_path='ckpt.t7',  # Path to pretrained DeepSORT model
    max_dist=0.2,
    min_confidence=0.3,
    nms_max_overlap=1.0,
    max_iou_distance=0.7,
    max_age=30,
    n_init=3,
    nn_budget=100
)

# Function to detect flyrocks (replace with your detection logic)
def detect_flyrocks(frame):
    # Example detection (random positions for demonstration)
    detections = [
        [100, 150, 200, 250, 0.9],  # [x1, y1, x2, y2, confidence]
        [300, 350, 400, 450, 0.8]
    ]
    return detections

# Load video
video_path = "flyrock_video.mp4"  # Replace with your video
cap = cv2.VideoCapture(video_path)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Detect flyrocks
    detections = detect_flyrocks(frame)

    # Prepare detections for DeepSORT
    bbox_xywh = []
    confidences = []
    for det in detections:
        x1, y1, x2, y2, conf = det
        bbox_xywh.append([(x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y2 - y1])  # Convert to [cx, cy, w, h]
        confidences.append(conf)

    bbox_xywh = np.array(bbox_xywh)
    confidences = np.array(confidences)

    # Update tracker
    outputs = deepsort.update(bbox_xywh, confidences, frame)

    # Draw tracked objects
    for output in outputs:
        x1, y1, x2, y2, track_id = output
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        cv2.putText(frame, f"ID: {track_id}", (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # Display frame
    cv2.imshow("Flyrock Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
