import cv2


def movediff_video(input_path, output_path):
    cap = cv2.VideoCapture(input_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height), isColor=False)

    ret, prev_frame = cap.read()
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    first_gray = prev_gray.copy()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(prev_gray, gray)
        #diff = cv2.absdiff(first_gray, gray)
        _, thresh = cv2.threshold(diff, 20, 255, cv2.THRESH_BINARY)
        cv2.imshow("Motion Mask", thresh)
        prev_gray = gray
        if cv2.waitKey(30) & 0xFF == 27:
            break
        out.write(thresh)

    cap.release()
    out.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    path = "./data/stabilize5.mp4"
    output = "./data/diff_video2.mp4"
    movediff_video(path, output)
