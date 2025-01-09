import os, sys
sys.path.append(os.path.join(os.getcwd(),"src"))
from func.roi import roi_video
#from func.operations import crop_roi
import asyncio
import cv2

def crop_roi(input_path, output_path, shape, withROI=None):
    print(withROI)
    print(shape)
    
    if not withROI:
        cap = cv2.VideoCapture(input_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        #fourcc = cv2.VideoWriter_fourcc(*"avc1")
        visualization = None
       
        x = shape[0]["x"]
        y = shape[0]["y"]
        w = shape[0]["w"]
        h = shape[0]["h"]
        out = cv2.VideoWriter(output_path,fourcc,fps, (w,h))
        frame_count = 0
        try:
            while True:
                ret, frame =  cap.read()
                if not ret:
                    break
                frame_count += 1
                cropped_frame = frame[y : y + h, x : x + w].copy()
                out.write(cropped_frame)
                cv2.imshow("frame", cropped_frame)
                cv2.waitKey(1)
            out.release()
            cap.release()
            print(frame_count)
            cv2.destroyAllWindows()
        except Exception as e:
            print(e)
    else:
        roi_video(input_path, output_path, shape)
    print("crop finished")



if __name__ == "__main__":
    path = "./temp/test_20250106_1/340_102.MP4"
    output = "./temp/test_20250106_1/340_102_crop.MP4"
    crop_roi(path, output, [{"x":83,"y":296,"w":2699,"h":1689,"type":"rectangle"}] )
    
    #asyncio.run(roi_video(path, output))
