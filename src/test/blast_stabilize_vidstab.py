import sys, os
sys.path.append(os.path.join(os.getcwd(),"src"))
from src.func.operations import stabilize_vidstab

if __name__ == "__main__":
    path = "./temp/123/340_102_clipped_StabilizeV_ROI.mp4"
    output = "./temp/123/340_102_clipped_StabilizeV_ROI_StablizeV.mp4"
    stabilize_vidstab(path, output)
