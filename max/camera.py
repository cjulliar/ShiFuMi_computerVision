# Import the InferencePipeline object
from functools import partial
import json
import os
from typing import Any, List
import cv2
from inference import InferencePipeline
import numpy as np

# Import the built in render_boxes sink for visualizing results
from inference.core.interfaces.stream.sinks import render_boxes
from inference.core.interfaces.camera.entities import VideoFrame
from inference.core.interfaces.stream.sinks import UDPSink

from ultralytics import YOLO


# affichage classes + probas + box sur vidéo en live


class VideoFrameWithPredictions:
    def __init__(self, video_frame: VideoFrame, predictions: dict = None):
        self.video_frame = video_frame
        self.predictions = predictions or {}


class MyModel:
    def __init__(self, weights_path: str):
        # charge le modele et les poids
        self._model = YOLO(weights_path)
        print("Modèle chargé avec succès")

    def infer(self, video_frames: List[VideoFrame]) -> List[any]:
        # convertir liste d'images en objet reconnu par yolo
        images = [v.image for v in video_frames]
        # convertir les images en numpy array
        # images_np = [np.array(img) for img in images]

        # faire predictions
        results = self._model(images, imgsz="640", stream=True)

        for i, result in enumerate(results):
            boxes = result.boxes.xyxy.tolist() if result.boxes else []
            scores = result.boxes.conf.tolist() if result.boxes else []
            class_indices = result.boxes.cls.tolist() if result.boxes else []

            video_frame = video_frames[i]
            predictions = {
                "boxes": boxes,
                "scores": scores,
                "class_indices": class_indices,
            }

        return predictions, video_frame

    def infer2(self, video_frames: List[VideoFrame]) -> List[VideoFrameWithPredictions]:
        # print("Video frames:", len(video_frames))

        # convertir liste d'images en objet reconnu par yolo
        images = [v.image for v in video_frames]

        # convertir les images en numpy array
        # images_np = [np.array(img) for img in images]

        # faire predictions
        results = self._model(images)

        # liste pour stocker les images et les prédictions
        enriched_video_frames = []

        # màj des images avec les prédictions
        for i, result in enumerate(results):
            boxes = result.boxes.xyxy.tolist() if result.boxes else []
            scores = result.boxes.conf.tolist() if result.boxes else []
            class_indices = result.boxes.cls.tolist() if result.boxes else []

            # créer un nouvelle image enrichie avec les prédictions
            enriched_frame = VideoFrameWithPredictions(
                video_frame=video_frames[i],
                predictions={
                    "boxes": boxes,
                    "scores": scores,
                    "class_indices": class_indices,
                },
            )

            enriched_video_frames.append(enriched_frame)

        return [
            enriched_video_frames[0].predictions,
            enriched_video_frames[0].video_frame,
        ]


def render_boxes_on_frame(predictions, video_frame: VideoFrame) -> VideoFrame:
    print(predictions)
    # convertir l'image en numpy array
    image = video_frame.image

    if predictions:
        boxes = predictions["boxes"]
        scores = predictions["scores"]
        class_indices = predictions["class_indices"]

        for box, score, class_idx in zip(boxes, scores, class_indices):
            x1, y1, x2, y2 = map(int, box)
            label = f"Classe: {class_idx}, Probabilité: {score:.2f}"

            # dessine le boarding box
            cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), 2)

            # mettre le label
            cv2.putText(
                image,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (255, 0, 0),
                2,
            )

    video_frame.image = image
    return video_frame


my_model = MyModel("../models/shifumi_trained_yolo9t.torchscript")
pipeline = InferencePipeline.init_with_custom_logic(
    on_video_frame=my_model.infer,
    video_reference=0,  # Ensure this is the correct device ID for your webcam
    on_prediction=render_boxes_on_frame,
)


pipeline.start()
pipeline.join()
