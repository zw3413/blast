
import asyncio
import os, sys
sys.path.append(os.path.join(os.getcwd(),"src"))
from lib.ByteTrack.yolox.tracker.byte_tracker import BYTETracker
from func.utils import add_suffix_to_filename
from func.methods import *
from func.operations import *
from func.video import Video
from func.PanZoomWindow import PanZoomWindow
import numpy as np
import cv2
from PIL import Image


if __name__ == "__main__":
    path = "./temp/test_20250114_340_102/340_102_clip_StabVid.mp4"
    output = "./temp/test_20250114_340_102/340_102_clip_StabVid_Slungshot.mp4"

    asyncio.run(slungshot_execute(path, output,'OpticalFlow', 'StrongSORT', WS_Enable= False))