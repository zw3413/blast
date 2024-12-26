import cv2
import numpy as np


def denseOpticalFlow(input_path, output_path):
    cap = cv2.VideoCapture(input_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    _, frameFirst = cap.read()
    imgPrev = cv2.cvtColor(frameFirst, cv2.COLOR_BGR2GRAY)
    imgHSV = np.zeros_like(frameFirst)
    imgHSV[:, :, 1] = 255

    while True:
        ret, frameCur = cap.read()
        if not ret:
            break
        imgCur = cv2.cvtColor(frameCur, cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(
            prev=imgPrev,
            next=imgCur,
            flow=None,
            pyr_scale=0.5,
            levels=3,
            winsize=15,
            iterations=3,
            poly_n=5,
            poly_sigma=0.12,
            flags=cv2.OPTFLOW_FARNEBACK_GAUSSIAN,
        )
        mag, ang = cv2.cartToPolar(flow[:, :, 0], flow[:, :, 1])
        # OpenCV H is [0,180] so divid by 2
        imgHSV[:, :, 0] = ang * 180 / np.pi / 2
        imgHSV[:, :, 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
        img_BGR = cv2.cvtColor(imgHSV, cv2.COLOR_HSV2BGR)
        cv2.imshow("Frame", img_BGR)
        cv2.waitKey(5)
        imgPrev = imgCur
        out.write(img_BGR)

    cap.release()
    out.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    path = "./data/kayake.mp4"
    output = "./data/optical_flow.mp4"
    denseOpticalFlow(path, output)
