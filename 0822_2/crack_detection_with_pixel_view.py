
import streamlit as st
from PIL import Image, ImageDraw, ImageOps
import requests
import io
import base64
import numpy as np

from streamlit_drawable_canvas import st_canvas

PIXEL_TO_MM = 0.1
API_KEY = st.secrets["ROBOFLOW_API_KEY"]
PROJECT_NAME = "-1121"
VERSION = "3"
ROBOFLOW_API_URL = f"https://outline.roboflow.com/{PROJECT_NAME}/{VERSION}?api_key={API_KEY}"

st.title("ひび割れ検出アプリ（セグメンテーション対応）")

confidence_threshold = st.slider(
    "信頼度の閾値を選択してください（低いほど多く検出されます）",
    min_value=0.0,
    max_value=1.0,
    value=0.2,
    step=0.01
)

uploaded_file = st.file_uploader("画像をアップロードしてください", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="アップロード画像", use_container_width=True)

    # Roboflow API 呼び出し
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    buffered.seek(0)

    response = requests.post(
        ROBOFLOW_API_URL,
        files={"file": buffered.getvalue()}
    )

    if response.status_code == 200:
        result = response.json()
        predictions = result.get("predictions", [])

        filtered_predictions = [
            pred for pred in predictions
            if pred.get("confidence", 0) >= confidence_threshold
        ]

        st.write(f"検出されたひび割れ領域（信頼度 ≥ {confidence_threshold:.2f}）:")

        overlay = image.copy()

        for pred in filtered_predictions:
            class_name = pred.get("class", "crack")
            confidence = pred.get("confidence", 0)
            mask_base64 = pred.get("mask")
            if mask_base64:
                mask_bytes = base64.b64decode(mask_base64)
                mask_image = Image.open(io.BytesIO(mask_bytes)).convert("L")
                red_mask = ImageOps.colorize(mask_image, black="black", white="red")
                overlay.paste(red_mask, (0, 0), mask_image)
            st.write(f"検出: {class_name}（信頼度: {confidence:.2f}）")

        st.image(overlay, caption="検出結果（ひび割れ領域マスク）", use_container_width=True)

        if not filtered_predictions:
            st.warning("指定された信頼度以上のひび割れは検出されませんでした。")
    else:
        st.error("Roboflow APIの呼び出しに失敗しました。")
        st.text(f"ステータスコード: {response.status_code}")
        st.text(response.text)

    # ピクセル値表示機能
    st.subheader("クリック位置のピクセルRGB値を表示")
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=1,
        background_image=image,
        update_streamlit=True,
        height=image.height,
        width=image.width,
        drawing_mode="point",
        point_display_radius=1,
        key="canvas"
    )

    pixels = np.array(image)
    if canvas_result.json_data is not None:
        for obj in canvas_result.json_data.get("objects", []):
            x = int(obj.get("left", 0))
            y = int(obj.get("top", 0))
            if 0 <= y < image.height and 0 <= x < image.width:
                rgb = pixels[y, x]
                st.write(f"クリック位置: ({x}, {y}) のRGB値: {rgb}")
