import cv2


def roi_video(input_path, output_path):
    cap = cv2.VideoCapture(input_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
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

    out = None
    # Initialize bounding box for drawing rectangle around tracked object
    object_bounding_box = None
    roi_h = 0
    roi_w = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame is None:
            break
        out_frame = None
        # Select ROI for tracking and begin object tracking
        if object_bounding_box is None:
            object_bounding_box = cv2.selectROI(
                "Select ROI", frame, fromCenter=False, showCrosshair=True
            )
            object_tracker.init(frame, object_bounding_box)
        else:
            # Draw rectangle around tracked object if tracking has started
            success, object_bounding_box = object_tracker.update(frame)

            if success:
                (x, y, w, h) = [int(v) for v in object_bounding_box]
                if out is None:
                    roi_h = h
                    roi_w = w
                    out = cv2.VideoWriter(output_path, fourcc, fps, (roi_w, roi_h))
                x = int(((w) / 2 + x) - roi_w / 2)
                y = int(((h) / 2 + y) - roi_h / 2)
                cv2.rectangle(frame, (x, y), (x + roi_w, y + roi_h), (0, 255, 0), 2)
                out_frame = frame[y : y + roi_h, x : x + roi_w].copy()

        if out_frame is not None:
            cv2.imshow("ROI", out_frame)
            key = cv2.waitKey(1)
            if key == 27:
                break
            if out is not None:
                out.write(out_frame)
        else:
            if out is not None:
                break
            else:
                print("ROI: lost frame may occured.")

    cap.release()
    if out is not None:
        out.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    path = "./data/stabilize1.mp4"
    output = "./data/ROI_video.mp4"
    roi_video(path, output)
