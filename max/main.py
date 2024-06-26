from roboflow import Roboflow
from ultralytics import YOLO

rf = Roboflow(api_key="bwfkMjv05uCsaZFMHdGM")
project = rf.workspace("roboflow-58fyf").project("rock-paper-scissors-sxsw")
version = project.version(14)
dataset = version.download("yolov9")


# Load a pretrained YOLO model (recommended for training)
model = YOLO("yolov9c.pt")

# Train the model using the 'coco8.yaml' dataset for 3 epochs
results = model.train(data=dataset.location + "/data.yaml", epochs=3)

# Evaluate the model's performance on the validation set
results = model.val()
