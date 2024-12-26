from functionality import enhance_video, roi_video, stabilize_video, movediff_video



if __name__ == "__main__":
    path = "./data/352_108.MP4"
    
    output1 = "./data/contrasted_video.mp4"
    enhance_video(path, output1)

    output2 = "./data/stabilize1.mp4"
    stabilize_video(output1, output2)

    output3 = "./data/roi.mp4"
    roi_video(output2, output3)

    output4 = "./data/stabilize2.mp4"
    stabilize_video(output3, output4)

    output5 = "./data/movediff.mp4"
    movediff_video(output4, output5)
