import asyncio
import cv2
import numpy as np
import os,sys
sys.path.append(os.path.join(os.getcwd(),"src"))
from func.methods import *
from func.utils import add_suffix_to_filename
from func.video import Video


async def slungshot_OpticalFlow(input_path, output_path=None):
    if output_path is None:
        output_path = add_suffix_to_filename(input_path, "SlungshotOpticalFlow")
    video = Video(input_path, output_path)
    imgHSV = np.zeros_like(video.frame)
    imgHSV[:, :, 1] = 255 #saturation
    while video.is_cap_opended():
        ret, frame = await video.read(enable_ws=False)
        if not ret:
            break
        flow = calc_optical_flow(video.prev_gray, video.gray)
        positive_y_flow = np.array(flow.copy())
        negative_y_flow = flow.copy()
        positive_y_flow[ positive_y_flow[:, :, 1] < 0 ]  = (0,0)
        negative_y_flow[negative_y_flow[:, :, 1] > 0] = (0,0)
        use_flow = flow
        mag, ang = cv2.cartToPolar(use_flow[:, :, 0], use_flow[:, :, 1])
        imgHSV = getHSVFromMagAng(mag, ang, threshold=2)
        img_BGR = cv2.cvtColor(imgHSV, cv2.COLOR_HSV2BGR)
        img_show = img_BGR + frame
        
        slungshot = detectSlungshotFromFlow(flow, min_speed=2)
        drawResultOnFrame(slungshot, img_show, "Speed")
        video.visualization = img_show
        video.write_frame = img_show
        cv2.imshow('slungshot_OpticalFlow', img_show)
        cv2.waitKey(1)
    video.release()
    cv2.destroyAllWindows()

async def testSlungshotOpticalFlow():
    path = "./temp/123/340_102_clipped_ROI_stabv.mp4"
    #path =  "./temp/340_102_clipped_StabilizeV_ROI_StablizeV.mp4"
    await slungshot_OpticalFlow(path)


if __name__ == "__main__":
    asyncio.run(testSlungshotOpticalFlow())
