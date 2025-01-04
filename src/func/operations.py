from .video import Video
from vidstab import VidStab
from .utils import add_suffix_to_filename
import cv2
import sys, os
sys.path.append(os.path.join(os.getcwd(),"src"))
from app import schemas
from .methods import *

async def slungshot(input_path, output_path = None,method = 'optical_flow'):
    if method == 'optical_flow':
        if output_path is None:
            output_path = add_suffix_to_filename(input_path, "SlungshotOpticalFlow")
        await slungshot_OpticalFlow(input_path,output_path)


async def slungshot_OpticalFlow(input_path, output_path):
    video = Video(input_path, output_path)
    imgHSV = np.zeros_like(video.frame)
    imgHSV[:, :, 1] = 255
    while video.is_cap_opended():
        ret, frame = await video.read()
        if not ret:
            break
        flow = calc_optical_flow(video.prev_gray, video.gray)
        mag, ang = cv2.cartToPolar(flow[:, :, 0], flow[:, :, 1])
        # OpenCV H is [0,180] so divid by 2
        imgHSV[:, :, 0] = ang * 180 / np.pi / 2
        normalizedMag = normalize_magnitude_with_threshold(mag, 2)
        imgHSV[:, :, 2] = normalizedMag
        img_BGR = cv2.cvtColor(imgHSV, cv2.COLOR_HSV2BGR)
        img_show = img_BGR + frame
        video.visualization = img_show
    video.release()
    
async def stabilize_vidstab(input_path, output_path):
    video = Video(input_path, output_path)
    stabilizer = VidStab()
    while video.is_cap_opended():
        ret, frame = await video.read()
        if not ret:
            break
        stabilized_frame = stabilizer.stabilize_frame(
            input_frame=frame, smoothing_window=30
        )
        if stabilized_frame is None:
            break
        if stabilized_frame is not None and stabilized_frame.sum() > 0:
            video.visualization = stabilized_frame
    video.release()
    cv2.destroyAllWindows()


async def crop_roi(input_path, output_path, shape):
    video = Video(input_path)
    print(shape)
    x = shape[0]["x"]
    y = shape[0]["y"]
    w = shape[0]["w"]
    h = shape[0]["h"]
    fps = video.fps
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"avc1"), fps, (w, h))
    while video.is_cap_opended():
        ret, frame = await video.read()
        if not ret:
            break
        cropped_frame = frame[y : y + h, x : x + w]
        out.visualization = cropped_frame
        out.write(cropped_frame)
    video.release()
    out.release()
    cv2.destroyAllWindows()


async def set_pixel(input_path, output_path):
    csvContent = open(input_path, "r").read()
    geo_coords = []
    pixel_coords = []
    all_geo_coords = []
    drill_holes = []
    line_index = 0
    for line in csvContent.split("\n"):
        if line and line_index > 0:
            line_index += 1
            drill_hole = schemas.DrillHole(line) 
            print(drill_hole)
            print(1)
            print(drill_hole.Pattern_Name)
            print(2)
            if(drill_hole.pixel_x is not None and drill_hole.pixel_x >0 and drill_hole.pixel_y is not None and drill_hole.pixel_y >0):
                pixel_coords.append([drill_hole.pixel_x, drill_hole.pixel_y])
                geo_coords.append([drill_hole.Drillhole_X, drill_hole.Drillhole_Y])
            all_geo_coords.append([drill_hole.Drillhole_X, drill_hole.Drillhole_Y])
            drill_holes.append(drill_hole)
    pixel_coords = calc_homography(geo_coords, pixel_coords, all_geo_coords)
    out = open(output_path, "w")
    for i, drill_hole in enumerate(drill_holes):
        drill_hole.pixel_x = pixel_coords[i][0]
        drill_hole.pixel_y = pixel_coords[i][1]
        out.write(
            f"{drill_hole.Pattern_Name},{drill_hole.Hole_id},{drill_hole.Drillhole_X},{drill_hole.Drillhole_Y},{drill_hole.Drillhole_Z},{drill_hole.Drillhole_ToeX},{drill_hole.Drillhole_ToeY},{drill_hole.Drillhole_ToeZ},{drill_hole.Drillhole_Length},{drill_hole.Drillhole_Dip},{drill_hole.Drillhole_Azimuth},{drill_hole.pixel_x},{drill_hole.pixel_y},{drill_hole.pixel_r}\n"
        )
    
