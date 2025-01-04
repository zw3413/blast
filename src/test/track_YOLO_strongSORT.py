import torch
import numpy as np
import cv2
import os
from time import perf_counter
from ultralytics import YOLO
from pathlib import Path

import supervision as sv
from strongsort.strong_sort import StrongSORT

from src.func.utils import YamlParser


SAVE_VIDEO =True
TRACKER = "strongsort"

class ObjectDetection:

    def __init__(self, capture_index):
        self.capture_index = capture_index
        self.device ='cuda' if torch.cuda.is_available() else 'gpu'
        print("Using Device: ", self.device)

        self.model = self.load_model()

        self.CLASS_NAMES_DICT = self.model.model.names

        self.box_annotator = sv.BoxAnnotator(sv.ColorPalette.DEFAULT, thickness=3)

        reid_weights = Path("weights/osnet_x0_25_msmt17.pt") 
        current_directory = os.getcwd()
        print(f"Current working directory: {current_directory}")
        
        tracker_config = "config/strongsort.yaml"
        cfg = YamlParser()
        cfg.merge_from_file(tracker_config)

        self.tracker = StrongSORT(
            reid_weights,
            torch.device(self.device),
            False,
            max_dist = cfg.strongsort.max_dist,
            max_iou_distance = cfg.strongsort.max_iou_dist,
            max_age = cfg.strongsort.max_age,
            #max_unmatched_preds = cfg.strongsort.max_unmatched_preds,
            n_init = cfg.strongsort.n_init,
            nn_budget = cfg.strongsort.nn_budget,
            mc_lambda = cfg.strongsort.mc_lambda,
            ema_alpha=cfg.strongsort.ema_alpha,
        )

    def load_model(self):
        model = YOLO("yolov8s-seg.pt")
        model.fuse()
        return model
    
    def predict(self, frame):
        results = self.model(frame)
        return results
    
    def draw_results(self, frame, results):
        xyxys = []
        confidences = []
        class_ids = []
        detections = []
        boxes = []
        for result in results:
            class_id = result.boxes.cls.cpu().numpy().astype(int)
            if len(class_id) == 0:
                continue
            if len(class_id)>1:
                class_id=class_id[0]
            if class_id == 0:
                xyxys.append(result.boxes.xyxy.cpu().numpy())
                confidences.append(result.boxes.conf.cpu().numpy())
                class_ids.append(result.boxes.cls.cpu().numpy().astype(int))
                boxes.append(result.boxes)
                detections = sv.Detections(
                    xyxy=result.boxes.xyxy.cpu().numpy(),
                    confidence = result.boxes.conf.cpu().numpy(),
                    class_id = result.boxes.cls.cpu().numpy().astype()
                )

            self.labels = [f"{self.CLASS_NAMES_DICT[class_id]} {confidence:0.2f}"
                           for _, confidence, class_id, tracker_id in detections
                           ]
            frame = self.box_annotator.annotate(scene= frame, detections=detections, labels= self.labels)
        
        def __call__(self):
            cap = cv2.VideoCapture(self.capture_index)
            assert cap.isOpened()
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

            if SAVE_VIDEO:
                outputvid = cv2.VideoWriter('./temp/result_tracking.avi', cv2.VideoWriter_fourcc('M','J','P','G'), 8 ,(1280,720))
            
            tracker = self.tracker
            tracker.model.warmup()

            outputs = [None]
            curr_frames, prev_frames = None, None

            while True:
                start_time = perf_counter()
                ret, frame = cap.read()
                assert ret
                results = self.predict(frame)
                frame, _= self.draw_results(frame, results)
                
                if prev_frames is not None and curr_frames is not None:
                    tracker.tracker.camera_update(prev_frames, curr_frames)

                for result in results:
                    outputs[0] = tracker.update(result,frame)
                    for i, (output) in enumerate(outputs[0]):
                        bbox = output[0:4]
                        tracked_id = output[4]
                        #cls = output[5]
                        #conf = output[6]
                        top_left = (int(bbox[-2]-100), int(bbox[1]))
                        cv2.putText(frame, f"ID : {tracked_id}", top_left, cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0),3 )
                    
                    end_time = perf_counter()
                    fps = 1/np.round(end_time - start_time, 2)

                    cv2.putText(frame, f'FPS:{int(fps)}', (20,70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 2)
                    cv2.imshow('YOLOv8 Detection', frame)
                    
                    if SAVE_VIDEO:
                        outputvid.write(frame)
                    if cv2.waitKey(5) & 0xFF ==27:
                        break
                if SAVE_VIDEO:
                    outputvid.release()
                cap.release()
                cv2.destroyAllWindows()


detector = ObjectDetection(capture_index=0)
detector()
