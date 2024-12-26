
import cv2

def enhance_contrast_linear(frame, alpha =2.2 , beta = -100 ):
    return cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)

#Contrast Limited Adaptive Histogram Equalization
def enhance_constrast_clahe(frame):
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    enhanced_lab = cv2.merge((cl,a,b))
    return cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
#Histogram Equalization:
def enhance_contrast_hsv(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hsv[:, :, 2] = cv2.equalizeHist(hsv[:, :, 2])  # Equalize the value channel
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

def enhance_video(input_path, output_path, alpha=1.3, beta=5):
    """
    Enhance video contrast and brightness
    alpha: Contrast control (1.0-3.0)
    beta: Brightness control (0-100)
    """
    cap = cv2.VideoCapture(input_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Method 1: Simple linear contrast adjustment
        #enhanced1 = enhance_contrast_linear(frame, alpha, beta)
        
        # Method 2: Adaptive histogram equalization
        #enhanced2 = enhance_constrast_clahe(frame)

        # Method 3:
        enhanced3 = enhance_contrast_hsv(frame)

        # Denoise the image
        #denoised_frame = cv2.fastNlMeansDenoisingColored(frame, None, 10, 10, 7, 21)


        # cv2.imshow('enhanced1',enhanced1)
        # cv2.imshow('enhanced2', enhanced2)
        cv2.imshow('enhanced3', enhanced3)
        #cv2.imshow('denoised_frame', denoised_frame)
        cv2.waitKey(1)
        
        # Choose which enhancement to use
        final = enhanced3  # or enhanced2
        
        out.write(final)
    
    cap.release()
    out.release()

if __name__ == "__main__":
    path = "./data/352_108.MP4"
    output = "./data/contrasted_video.mp4"
    alpha = 2.2   #Contrast control (1.0-3.0)
    beta = -100      #Brightness control (0-100)
    enhance_video(path, output, alpha, beta)