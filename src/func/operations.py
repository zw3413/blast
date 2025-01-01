from .video import Video
from vidstab import VidStab
import cv2

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
        if stabilized_frame is not None and stabilized_frame.sum()>0:
            video.visualization = stabilized_frame
    video.release()
    cv2.destroyAllWindows()