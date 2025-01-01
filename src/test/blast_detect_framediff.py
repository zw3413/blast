import cv2
import numpy as np
import os,sys
sys.path.append(os.path.join(os.getcwd(),"src"))
from func.methods import calc_frame_diff

def movediff_video(input_path, output_path):
    cap = cv2.VideoCapture(input_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    ret, prev_frame = cap.read()
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    first_gray = prev_gray.copy()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        results = calc_frame_diff(prev_gray, gray)
        overlay = cv2.cvtColor(results, cv2.COLOR_BAYER_BG2BGR)
        overlay[results>0] = [0,255,255]
        visualization = frame.copy()
        visualization = cv2.addWeighted(visualization,1,overlay,0.5,0)
        cv2.imshow("Frame Diff", visualization)
        prev_gray = gray
        if cv2.waitKey(30) & 0xFF == 27:
            break
        out.write(frame)

    cap.release()
    out.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    path = "./temp/340_102_clipped_StabilizeV_ROI_StablizeV.mp4"
    output = "./temp/340_102_clipped_StabilizeV_ROI_StablizeV_movediff.mp4"
    movediff_video(path, output)
