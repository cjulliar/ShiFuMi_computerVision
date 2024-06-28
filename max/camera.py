# Import the InferencePipeline object
from functools import partial
import json
import os
from typing import Any, List
from inference import InferencePipeline

# Import the built in render_boxes sink for visualizing results
from inference.core.interfaces.stream.sinks import render_boxes
from inference.core.interfaces.camera.entities import VideoFrame
from inference.core.interfaces.stream.sinks import UDPSink

from ultralytics import YOLO

TARGET_DIR = "./my_predictions"


class MyModel:
    def __init__(self, weights_path: str):
        self._model = YOLO(weights_path, task="detect")

    def infer(self, video_frames: List[VideoFrame]) -> List[Any]:
        return self._model([v.image for v in video_frames])

    def on_prediction(predictions, video_frame) -> None:
        with open(os.path.join(TARGET_DIR, f"{video_frame.frame_id}.json")) as f:
            json.dump(predictions, f)


my_model = MyModel(
    "/Users/maximekuil/Documents/Simplon/ShiFuMi_computerVision/models/shifumi_trained_yolo9t.torchscript"
)


def on_prediction(predictions, video_frame):
    render_boxes(
        predictions=predictions,
        video_frame=video_frame,
        display_statistics=True,  # Enable displaying statistics
    )


udp_sink = UDPSink.init(ip_address="127.0.0.1", port=9090)

pipeline = InferencePipeline.init_with_custom_logic(
    on_video_frame=my_model.infer,
    video_reference=1,
    # on_prediction=my_model.on_prediction,
    # on_prediction=on_prediction,  # Function to run after each prediction
)

pipeline.start()
pipeline.join()
