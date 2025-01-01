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
        # flow = cv2.calcOpticalFlowFarneback(
        #     prev=imgPrev,
        #     next=imgCur,
        #     flow=None,
        #     pyr_scale=0.5,
        #     levels=3,
        #     winsize=15,
        #     iterations=3,
        #     poly_n=5,
        #     poly_sigma=1.1,
        #     flags=cv2.OPTFLOW_FARNEBACK_GAUSSIAN,
        # )

        gpu_previous = cv2.cuda_GpuMat()
        gpu_previous.upload(imgPrev)
        gpu_current= cv2.cuda_GpuMat()
        gpu_current.upload(imgCur)
        gpu_flow = cv2.cuda_FarnebackOpticalFlow.create(
            3,  #numLevels
            0.5 ,  #pyrScale
            False, #fastPyramids
            15,  #winSize
            3,   #numItems
            5,   #polyN
            1.1, #polySigma 
            0    #flags
            )
        aflow = cv2.cuda.GpuMat()
        aflow = gpu_flow.calc( gpu_previous, gpu_current, aflow, None )
        flow = aflow.download()

        mag, ang = cv2.cartToPolar(flow[:, :, 0], flow[:, :, 1])
        
        # OpenCV H is [0,180] so divid by 2
        imgHSV[:, :, 0] = ang * 180 / np.pi / 2
        normalizedMag = normalize_magnitude_with_threshold(mag, 2)
        imgHSV[:, :, 2] = normalizedMag

        img_BGR = cv2.cvtColor(imgHSV, cv2.COLOR_HSV2BGR)

        img_show = img_BGR + frameCur
        cv2.imshow("Frame", img_show)
        cv2.waitKey(5)
        imgPrev = imgCur
        out.write(img_show)

    cap.release()
    out.release()
    cv2.destroyAllWindows()

def normalize_magnitude_with_threshold(mag, threshold, min_output = 0, max_output = 255):
    mag[mag<threshold] = 0 
    min_mag = np.min(mag)
    max_mag = np.max(mag)
    normalized_mag = (mag-min_mag) * (max_output - min_output) / (max_mag - min_mag) + min_output
    return normalized_mag.astype(np.uint8)

if __name__ == "__main__":
    path = "./temp/340_102_clipped_StabilizeV_ROI_StablizeV.mp4"
    output = "./temp/optical_flow.mp4"
    denseOpticalFlow(path, output)
