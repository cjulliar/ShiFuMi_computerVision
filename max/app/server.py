from typing import List
from fastapi import FastAPI, Request
import cv2
from fastapi.responses import JSONResponse
import numpy as np
import base64
import json
from fastapi.middleware.cors import CORSMiddleware
from ultralytics.engine.results import Results

from ultralytics import YOLO

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = YOLO("../../models/shifumi_trained_yolo9t.torchscript")


@app.post("/send-frame")
async def receive_frame(request: Request):
    # Récupérer l'image JPEG envoyée par le client
    data = await request.body()
    data = data.replace(b"data:image/jpeg;base64,", b"")
    im_bytes = base64.b64decode(data, validate=True)
    im_arr = np.frombuffer(im_bytes, dtype=np.uint8)
    img = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)
    # print(img)

    # https://docs.ultralytics.com/reference/engine/results/#ultralytics.engine.results.Results
    results: List[Results] = model.predict(source=img, conf=0.7, stream=True)

    for r in results:
        return JSONResponse(r.tojson())
