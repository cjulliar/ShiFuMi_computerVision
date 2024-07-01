import cv2
import streamlit as st
import numpy as np
from ultralytics import YOLO
from camera import VideoFrame, MyModel, VideoFrameWithPredictions, render_boxes_on_frame
from game import Game, Player

def app():
    st.header("Let's play ShifuMi")
    st.subheader('Powered by YOLOv9')

    player1 = st.text_input("Nom du joueur 1")
    player2= st.text_input("Nom du joueur 2")
    game = Game(player1, player2)

    my_model = MyModel("../models/shifumi_trained_yolo9t.torchscript")
    if my_model:
        st.write("Modèle chargé!")


    #lancer la webcam
    cap = cv2.VideoCapture()

    stop_button = st.button("Arrêter la webcam")

    while cap.isOpened(): #boucle principale pour lire la vidéo
        ret, frame = cap.read() #ret et frame sont des paramètres de read, ret sert à vérifier si la lecture de la vidéo est possible et frame est l'image de la vidéo 
        if not ret:
            st.error('Impossible de lire la vidéo')
            break

        video_frame = VideoFrame(image=frame, frame_id=0, frame_timestamp=0)

        enriched_frames = my_model.infer([video_frame])

        enriched_frame = enriched_frames[0]

        image_with_boxes = np.array(enriched_frame.image)
        predictions = enriched_frame.predictions
        player1_hand = None
        player2_hand = None

        if predictions:
            boxes = predictions['boxes']
            scores = predictions['scores']
            class_indices = predictions['class_indices']

            for box, score, class_idx in zip(boxes, scores, class_indices):
                x1, y1, x2, y2 = map(int, box)
                label = f'Classe: {class_idx}, Probabilité: {score:.2f}'
                cv2.rectangle(image_with_boxes, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(image_with_boxes, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

                #identifier les mains des joueurs
                if x1 < frame.shape[1] // 2: #si x1 est inférieur à la moitié de la largeur de l'image
                    player1_hand = class_idx
                else:
                    player2_hand = class_idx

                # if class_idx == 0:
                #     player1_hand = "rock"
                # elif class_idx == 1:
                #     player1_hand = "paper"
                # elif class_idx == 2:
                #     player1_hand = "scissors"
                # else:
                #     player1_hand = "unknown"

            if player1_hand is not None and player2_hand is not None:
                result = game.play_round(player1_hand, player2_hand)
                st.write(result)
                st.write(game.get_score())

        st.image(image_with_boxes, channels="BGR")


        if stop_button:
            break

    cap.release() #permet de libérer la webcam



if __name__ == "__main__":
    app()