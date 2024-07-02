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

def render_boxes_on_frame(video_frame_with_predictions: VideoFrameWithPredictions, player1_score, player2_score) -> np.ndarray:
    # Convert the image to numpy array
    image = np.array(video_frame_with_predictions.image)
    predictions = video_frame_with_predictions.predictions

    # Define class names and colors
    class_map = {
        0: ("feuille", (0, 255, 0)),  # Green
        1: ("caillou", (255, 0, 0)),  # Blue
        2: ("ciseaux", (0, 0, 255))   # Red
    }

    if predictions:
        boxes = predictions['boxes']
        scores = predictions['scores']
        class_indices = predictions['class_indices']

        for box, score, class_idx in zip(boxes, scores, class_indices):
            if score >= 0.6:  # Only draw the box if the score is greater than or equal to 0.6
                x1, y1, x2, y2 = map(int, box)
                label, color = class_map.get(class_idx, ("unknown", (255, 255, 255)))  # Default to white

                # Draw the rectangle around the detected object
                cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)

                # Put the label
                print_score = score * 100
                label_text = f'{label}, {print_score:.2f}%'
                cv2.putText(image, label_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    # Display scores at the bottom center of the screen
    score_text = f"{player1_score} {player2_score}"
    h, w, _ = image.shape
    cv2.putText(image, score_text, (w // 2 - 100, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 5)

    return image

def determine_winner(classes):
    if len(classes) != 2:
        return "Erreur: deux joueurs requis", -1, -1
    
    player1, player2 = classes

    if player1 == player2:
        return "Egalite!", -1, -1
    elif (player1 == 0 and player2 == 1) or (player1 == 1 and player2 == 2) or (player1 == 2 and player2 == 0):
        return "Le joueur 1 gagne!", 0, 1
    else:
        return "Le joueur 2 gagne!", 1, 0

def assign_players_to_boxes(boxes, width):
    left_boxes = []
    right_boxes = []
    for box in boxes:
        x1, y1, x2, y2 = map(int, box)
        center_x = (x1 + x2) / 2
        if center_x < width / 2:
            left_boxes.append(box)
        else:
            right_boxes.append(box)
    
    if len(left_boxes) == 1 and len(right_boxes) == 1:
        return left_boxes[0], right_boxes[0]
    else:
        return None, None

# Streamlit app
st.title("Jeu Pierre, Feuille, Ciseaux avec YOLO")

# Initialize the model
my_model = MyModel("models/shifumi_trained_yolo9t.torchscript")

# Scores
if 'player1_score' not in st.session_state:
    st.session_state['player1_score'] = 0
if 'player2_score' not in st.session_state:
    st.session_state['player2_score'] = 0

# Open the webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    st.error("Erreur: Impossible d'ouvrir le flux vidéo")
else:
    frame_id = 0

    stframe = st.empty()
    game_state = "idle"
    countdown = 10  # Double the countdown duration
    start_time = None
    result_image = None
    game_result = ""
    winning_boxes = []
    display_result_start_time = None
    winner = None

    if st.button("Démarrer", key="start_button"):
        game_state = "countdown"
        start_time = time.time()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_id += 1
        frame_timestamp = cap.get(cv2.CAP_PROP_POS_MSEC)

        # Create a VideoFrame
        video_frame = VideoFrame(frame, frame_id, frame_timestamp)

        # Run inference
        predictions = my_model.infer([video_frame])

        # Add player labels and divider
        h, w, _ = frame.shape
        cv2.putText(frame, "Joueur 1", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 4)
        cv2.putText(frame, "Joueur 2", (w - 290, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 4)
        cv2.line(frame, (w // 2, 0), (w // 2, h), (255, 255, 255), 2)

        if game_state == "countdown":
            elapsed_time = time.time() - start_time
            frame = render_boxes_on_frame(predictions[0], st.session_state['player1_score'], st.session_state['player2_score'])
            cv2.putText(frame, f"{countdown - int(elapsed_time)}", (w // 2 - 50, h // 2), cv2.FONT_HERSHEY_SIMPLEX, 6, (255, 255, 255), 10)

            if elapsed_time >= countdown:
                game_state = "result"
                result_image = np.copy(video_frame.image)  # Save the raw frame without boxes
                left_box, right_box = assign_players_to_boxes(predictions[0].predictions['boxes'], w)
                if left_box is not None and right_box is not None:
                    player1_class = predictions[0].predictions['class_indices'][predictions[0].predictions['boxes'].index(left_box)]
                    player2_class = predictions[0].predictions['class_indices'][predictions[0].predictions['boxes'].index(right_box)]
                    game_result, winner, loser = determine_winner([player1_class, player2_class])
                    winning_boxes = [left_box, right_box]
                display_result_start_time = time.time()

            stframe.image(frame, channels="BGR")

        elif game_state == "result":
            if result_image is not None:
                cv2.putText(result_image, game_result, (w // 2 - 200, h // 2), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
                result_frame_rgb = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)
                result_image_pil = Image.fromarray(result_frame_rgb)
                stframe.image(result_image_pil, channels="RGB")

                if time.time() - display_result_start_time >= 5:
                    if winner is not None and winner != -1:
                        if winner == 0:
                            st.session_state['player1_score'] += 1
                        else:
                            st.session_state['player2_score'] += 1
                    game_state = "idle"
                    winner = None

        else:
            frame = render_boxes_on_frame(predictions[0], st.session_state['player1_score'], st.session_state['player2_score'])
            stframe.image(frame, channels="BGR")

    cap.release()

st.write("Appuyez sur 'q' pour quitter la capture vidéo.")
