import cv2
import numpy as np

def stabilize_video(input_path, output_path):
    video = cv2.VideoCapture(input_path)
    n_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = video.get(cv2.CAP_PROP_FPS)

    # Define the output video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Read the first frame
    ret, prev_frame = video.read()
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    transforms = []

    for _ in range(n_frames - 1):
        ret, curr_frame = video.read()
        if not ret:
            break
        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)

        # Calculate optical flow
        flow = cv2.calcOpticalFlowFarneback(prev_gray, curr_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        dx = -flow[..., 0].mean()  # Translation in x
        dy = -flow[..., 1].mean()  # Translation in y
        transforms.append((dx, dy))
        prev_gray = curr_gray

    # Apply cumulative transformations
    cumulative_dx, cumulative_dy = 0, 0
    video.set(cv2.CAP_PROP_POS_FRAMES, 0)
    for i, (dx, dy) in enumerate(transforms):
        cumulative_dx += dx
        cumulative_dy += dy
        ret, frame = video.read()
        if not ret:
            break

        # Apply translation
        M = np.float32([[1, 0, cumulative_dx], [0, 1, cumulative_dy]])
        stabilized_frame = cv2.warpAffine(frame, M, (width, height))

        cv2.imshow("stabilize_cv", stabilized_frame)
        cv2.waitKey(1)

        out.write(stabilized_frame)

    video.release()
    out.release()

if __name__ == "__main__":
    path = "./temp/ROI_video.mp4"
    output = "./temp/stabilize.mp4"
    stabilize_video(path, output)