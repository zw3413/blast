import cv2
from vidstab import VidStab


def stabilize_video(input_path, output_path):
    cap = cv2.VideoCapture(input_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    stabilizer = VidStab()
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        stabilized_frame = stabilizer.stabilize_frame(
            input_frame=frame, smoothing_window=30
        )

        if stabilized_frame is None:
            break

        if stabilized_frame is not None and stabilized_frame.sum()>0:
            cv2.imshow("Frame", stabilized_frame)
            key = cv2.waitKey(1)
            if key == 27:
                break
            if out is not None:
                out.write(stabilized_frame)

    cap.release()
    if out is not None:
        out.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    path = "./data/stabilize4.mp4"
    output = "./data/stabilize5.mp4"
    stabilize_video(path, output)
