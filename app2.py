import streamlit as st
from typing import List
from ultralytics import YOLO
import numpy as np
import cv2
from PIL import Image
import time

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
            x1, y1, x2, y2 = map(int, box)
            label, color = class_map.get(class_idx, ("unknown", (255, 255, 255)))  # Default to white

            # Draw the rectangle around the detected object
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)

            # Put the label
            label_text = f'{label}, Probabilité: {score:.2f}'
            cv2.putText(image, label_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    return image

def determine_winner(class_idx1, class_idx2):
    if class_idx1 == class_idx2:
        return "draw"
    elif (class_idx1 == 0 and class_idx2 == 1) or (class_idx1 == 1 and class_idx2 == 2) or (class_idx1 == 2 and class_idx2 == 0):
        return "player1"
    else:
        return "player2"

# Streamlit app

st.title("Détection de Formes de Main (Pierre, Feuille, Ciseaux) avec YOLO")

# Initialize the model
my_model = MyModel("models/shifumi_trained_yolo9t.torchscript")

# Open the webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    st.error("Erreur: Impossible d'ouvrir le flux vidéo")
else:
    frame_id = 0
    stframe = st.empty()

    player1_score = 0
    player2_score = 0

    # Streamlit elements for displaying scores
    score_placeholder = st.empty()
    countdown_placeholder = st.empty()

    start_game = st.button('Start')

    if start_game:
        while cap.isOpened():
            # Display video stream
            ret, frame = cap.read()
            if not ret:
                break

            frame_id += 1
            frame_timestamp = cap.get(cv2.CAP_PROP_POS_MSEC)

            # Create a VideoFrame
            video_frame = VideoFrame(frame, frame_id, frame_timestamp)

            # Run inference
            predictions = my_model.infer([video_frame])

            # Render boxes on the frame
            result_frame = render_boxes_on_frame(predictions[0])

            if player1_score == 3:
                st.write("Partie terminée, le Joueur 1 a gagné !")
                break
            if player2_score == 3:
                st.write("Partie terminée, le Joueur 2 a gagné !")
                break

            # Countdown overlay
            for i, word in enumerate(["Shi", "Fu", "Mi"], 1):
                countdown_frame = result_frame.copy()
                cv2.putText(countdown_frame, word, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3, cv2.LINE_AA)
                result_frame_rgb = cv2.cvtColor(countdown_frame, cv2.COLOR_BGR2RGB)
                result_image = Image.fromarray(result_frame_rgb)
                stframe.image(result_image, channels="RGB")
                time.sleep(3)

            # Convert the result frame to an image format Streamlit can display
            result_frame_rgb = cv2.cvtColor(result_frame, cv2.COLOR_BGR2RGB)
            result_image = Image.fromarray(result_frame_rgb)

            # Display the resulting frame
            stframe.image(result_image, channels="RGB")

            # Check predictions and determine winner
            if predictions[0].predictions:
                class_indices = predictions[0].predictions['class_indices']
                if len(class_indices) == 2:  # Assuming two hands are detected
                    player1_class = class_indices[0]
                    player2_class = class_indices[1]
                    winner = determine_winner(player1_class, player2_class)

                    if winner == "player1":
                        player1_score += 1
                    elif winner == "player2":
                        player2_score += 1

                    # Update scores
                    score_placeholder.text(f"Score: Joueur 1 - {player1_score} | Joueur 2 - {player2_score}")

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # When everything done, release the capture
        cap.release()
