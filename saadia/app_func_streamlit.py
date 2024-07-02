from app_func import VideoFrame, VideoFrameWithPredictions, MyModel, render_boxes_on_frame
import streamlit as st
import cv2
from PIL import Image
from game import Game, Player

#Application streamlit
def app():
    st.header("Let's play ShifuMi")
    st.subheader('Powered by YOLOv9')

    my_model = MyModel("../models/shifumi_trained_yolo9t.torchscript")

    # # Initialize players
    # player1 = Player("Joueur 1")
    # player2 = Player("Joueur 2")
    # game = Game(player1, player2)

    cap = cv2.VideoCapture(0)


    if not cap.isOpened():
        st.error("Erreur: Impossible d'ouvrir le flux vidéo")
    

    frame_id = 0

    stframe = st.empty()
    stop_button = st.button("Arrêter la webcam")


    while cap.isOpened():
        ret, frame = cap.read() #frame est une image du flux vidéo capturé 
        if not ret:
            break

        frame_id += 1
        frame_timestamp = cap.get(cv2.CAP_PROP_POS_MSEC)

            # cv2.imshow('Frame', frame)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

        # Create a VideoFrame
        video_frame = VideoFrame(frame, frame_id, frame_timestamp)

        # Run inference
        predictions = my_model.infer([video_frame])

        # Render boxes on the frame
        result_frame = render_boxes_on_frame(predictions[0])

        # Convert the result frame to an image format Streamlit can display
        result_frame_rgb = cv2.cvtColor(result_frame, cv2.COLOR_BGR2RGB)
        result_image = Image.fromarray(result_frame_rgb)

        # Display the resulting frame
        stframe.image(result_image, channels="RGB")

        if stop_button:
            break
    
        cap.release()

if __name__ == '__main__':
    app()


