import cv2
import numpy as np


def analyze_flyrock_size(video_path):
    """
    Tool to analyze potential flyrock sizes in video frames

    Parameters:
    video_path (str): Path to the video file
    """
    # Open the video
    cap = cv2.VideoCapture(video_path)

    screen_res = 1920, 1080

    # Variables for mouse callback
    drawing = False
    ix, iy = -1, -1

    def draw_rectangle(event, x, y, flags, param):
        nonlocal ix, iy, drawing, img

        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            ix, iy = x, y

        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing:
                img_copy = img.copy()
                cv2.rectangle(img_copy, (ix, iy), (x, y), (0, 255, 0), 2)
                cv2.imshow("Frame", img_copy)

        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            width = abs(x - ix)
            height = abs(y - iy)
            area = width * height
            print(f"Selected area dimensions:")
            print(f"Width: {width} pixels")
            print(f"Height: {height} pixels")
            print(f"Area: {area} square pixels")

            # Draw final rectangle
            cv2.rectangle(img, (ix, iy), (x, y), (0, 255, 0), 2)
            cv2.imshow("Frame", img)

    cv2.namedWindow("Frame")
    cv2.setMouseCallback("Frame", draw_rectangle)

    frame_count = 0

    while True:
        ret, img = cap.read()
        if not ret:
            break

        frame_count += 1

        # Only process every 30th frame (1 second intervals)
        if frame_count % 30 != 0:
            continue

        center_x, center_y = img.shape[1] // 2, img.shape[0] // 2
        half_screen_width, half_screen_height = screen_res[0] // 2, screen_res[1] // 2
        center_area = img[
            center_y - half_screen_height : center_y + half_screen_height,
            center_x - half_screen_width : center_x + half_screen_width,
        ]
        # img = center_area

        cv2.imshow("Frame", img)

        key = cv2.waitKey(0)  # Wait indefinitely for a key press
        if key == ord("q"):  # Press 'q' to quit
            break
        elif key == ord("n"):  # Press 'n' for next frame
            continue

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    path = "./temp/328_109_clipped.mp4"
    analyze_flyrock_size(path)
