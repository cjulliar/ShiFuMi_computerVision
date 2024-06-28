# Import the InferencePipeline object
from typing import Any, List
from inference import InferencePipeline

# Import the built in render_boxes sink for visualizing results
from inference.core.interfaces.stream.sinks import render_boxes
from inference.core.interfaces.camera.entities import VideoFrame
import torch
from ultralytics import YOLO


class MyModel:
    def __init__(self, weights_path: str):
        # self._model = torch.hub.load(
        #     "ultralytics/yolov9", "custom", path=weights_path, force_reload=True
        # )

        self._model = YOLO(
            "/Users/maximekuil/Documents/Simplon/ShiFuMi_computerVision/shifumi_trained.pt"
        )

        # with torch.inference_mode():
        self._model.predict(
            "/Users/maximekuil/Documents/Simplon/ShiFuMi_computerVision/Rock-Paper-Scissors-SXSW-14/test/images/20220216_221550_jpg.rf.02a071a383151953fcf8671fc7fca3af.jpg",
            classes=["Paper", "Rock", "Scissors"],
        )

    # after v0.9.18
    def infer(self, video_frames: List[VideoFrame]) -> List[Any]:
        # result must be returned as list of elements representing model prediction for single frame
        # with order unchanged.
        with torch.inference_mode():
            return self._model([v.image for v in video_frames])


my_model = MyModel(
    "/Users/maximekuil/Documents/Simplon/ShiFuMi_computerVision/shifumi_trained.pt"
)
# pipeline = InferencePipeline.init_with_custom_logic(
#     on_video_frame=my_model.infer,
#     video_reference=1,  # Path to video, device id (int, usually 0 for built in webcams), or RTSP stream url
#     on_prediction=render_boxes,  # Function to run after each prediction
# )
# pipeline.start()
# pipeline.join()
