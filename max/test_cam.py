from ultralytics import YOLO

model = YOLO("../models/shifumi_trained_yolo9t.torchscript")
results = model.predict(source="0", show=True, stream=True)

for r in results:
    boxes = r.boxes  # Boxes object for bbox outputs
    masks = r.masks  # Masks object for segment masks outputs
    probs = r.probs  # Class probabilities for classification outputs

    print("***", boxes)

# print(results)
