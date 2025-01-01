uvicorn src.app.main:app --reload
npm run dev


python inference_example.py --source_video_path C:\Developer\CoteGold\data\C1_328_109\328_109.MP4 --target_video_path tracking_result.mp4
python ultralytics_example.py --source_weights_path yolov8s.pt --source_video_path C:\Developer\CoteGold\data\C1_328_109\328_109.MP4 --target_video_path tracking_result.mp4


1. increase the contrast 
2. stabilize + ROI 
3. stabilize
4. frame diff
5. 


flyrock:
    - motion detection with optical flow algorithm
    - Object tracking

smoke:
    - motion detection with optical flow algorithm
    - color


 gpu_flow = cv2.cuda.FarnebackOpticalFlow.create(3, 0.5, False, 15, 3, 5, 1.1, 0 )

 gpu_flow = cv2.cuda.FarnebackOpticalFlow.create(pyr_scale, levels, winsize, iterations, poly_n, poly_sigma, flags)



