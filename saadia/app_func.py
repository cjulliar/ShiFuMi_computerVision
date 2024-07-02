import streamlit as st
from typing import List
from ultralytics import YOLO
import numpy as np
import cv2
from PIL import Image

class VideoFrame:
    def __init__(self, image, frame_id, frame_timestamp):
        self.image = image
        self.frame_id = frame_id
        self.frame_timestamp = frame_timestamp

class VideoFrameWithPredictions:
    def __init__(self, video_frame: VideoFrame, predictions: dict = None):
        self.video_frame = video_frame
        self.predictions = predictions or {}

    @property
    def image(self):
        return self.video_frame.image

    @property
    def frame_id(self):
        return self.video_frame.frame_id

    @property
    def frame_timestamp(self):
        return self.video_frame.frame_timestamp

class MyModel:
    def __init__(self, weights_path: str):
        # Load the YOLO model
        self._model = YOLO(weights_path)
        print("Modèle chargé avec succès")

    def infer(self, video_frames: List[VideoFrame]) -> List[VideoFrameWithPredictions]:
        print('Video frames:', len(video_frames))
        
        # Convert the list of images to the format expected by YOLO
        images = [v.image for v in video_frames]

        # Convert images to numpy arrays
        images_np = [np.array(img) for img in images]

        # Make predictions
        results = self._model(images_np)

        # Create a list to store enriched VideoFrames
        enriched_video_frames = []

        # Update video frames with predictions
        for i, result in enumerate(results):
            boxes = result.boxes.xyxy.tolist() if result.boxes else []
            scores = result.boxes.conf.tolist() if result.boxes else []
            class_indices = result.boxes.cls.tolist() if result.boxes else []

            # Create a new VideoFrameWithPredictions
            enriched_frame = VideoFrameWithPredictions(
                video_frame=video_frames[i],
                predictions={
                    'boxes': boxes,
                    'scores': scores,
                    'class_indices': class_indices
                }
            )

            enriched_video_frames.append(enriched_frame)

        return enriched_video_frames

def render_boxes_on_frame(video_frame_with_predictions: VideoFrameWithPredictions) -> np.ndarray:
    # Convert the image to numpy array
    image = np.array(video_frame_with_predictions.image)
    predictions = video_frame_with_predictions.predictions

    # Define class names and colors
    class_map = {
        0: ("Feuille", (0, 255, 0)),  # Green
        1: ("Pierre", (255, 0, 0)),  # Blue
        2: ("Ciseaux", (0, 0, 255))   # Red
    }

    if predictions:
        boxes = predictions['boxes']
        scores = predictions['scores']
        class_indices = predictions['class_indices']

        for box, score, class_idx in zip(boxes, scores, class_indices):
            if score < 0.5:
                continue
            x1, y1, x2, y2 = map(int, box)
            label, color = class_map.get(class_idx, ("unknown", (255, 255, 255)))  # Default to white

            # Draw the rectangle around the detected object
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)

            # Put the label
            label_text = f'{label}, {score:.2f}'
            cv2.putText(image, label_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    return image

