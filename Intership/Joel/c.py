import cv2
import numpy as np
import streamlit as st

st.title("Vehicle Counting App")

# Constants
largura_min = st.slider("Minimum Width", 10, 200, 80)
altura_min = st.slider("Minimum Height", 10, 200, 80)
offset = st.slider("Error Offset", 1, 20, 6)
pos_linha = st.slider("Counting Line Position", 100, 800, 550)
delay = st.slider("FPS (Delay)", 1, 120, 60)

detec = []
carros = 0


def pega_centro(x, y, w, h):
    x1 = int(w / 2)
    y1 = int(h / 2)
    cx = x + x1
    cy = y + y1
    return cx, cy


uploaded_video = st.file_uploader("Upload a video file", type=["mp4"])

if uploaded_video:
    cap = cv2.VideoCapture(uploaded_video)
    subtracao = cv2.bgsegm.createBackgroundSubtractorMOG()

    while True:
        ret, frame1 = cap.read()
        if not ret:
            break
        tempo = float(1 / delay)
        sleep(tempo)
        grey = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(grey, (3, 3), 5)
        img_sub = subtracao.apply(blur)
        dilat = cv2.dilate(img_sub, np.ones((5, 5)))
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        dilatada = cv2.morphologyEx(dilat, cv2.MORPH_CLOSE, kernel)
        dilatada = cv2.morphologyEx(dilatada, cv2.MORPH_CLOSE, kernel)
        contorno, h = cv2.findContours(dilatada, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        cv2.line(frame1, (25, pos_linha), (1200, pos_linha), (255, 127, 0), 3)
        for i, c in enumerate(contorno):
            (x, y, w, h) = cv2.boundingRect(c)
            validar_contorno = (w >= largura_min) and (h >= altura_min)
            if not validar_contorno:
                continue

            cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)
            centro = pega_centro(x, y, w, h)
            detec.append(centro)
            cv2.circle(frame1, centro, 4, (0, 0, 255), -1)

            for x, y in detec:
                if y < (pos_linha + offset) and y > (pos_linha - offset):
                    carros += 1
                    cv2.line(frame1, (25, pos_linha), (1200, pos_linha), (0, 127, 255), 3)
                    detec.remove((x, y))

        cv2.putText(
            frame1,
            "VEHICLE COUNT : " + str(carros),
            (450, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            2,
            (0, 0, 255),
            5,
        )
        st.image(frame1, channels="BGR", use_column_width=True)

st.write("Finished processing video.")
