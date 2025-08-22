import streamlit as st
import requests
from PIL import Image, ImageDraw, ImageOps
import io
import base64

PIXEL_TO_MM = 0.1
API_KEY = st.secrets["ROBOFLOW_API_KEY"]
PROJECT_NAME = "-1121"
VERSION = "3"
ROBOFLOW_API_URL = f"https://outline.roboflow.com/{PROJECT_NAME}/{VERSION}?api_key={API_KEY}"

st.title("ひび割れ検出アプリ（セグメンテーション対応）")

st.markdown(
    """
    <style>
    body {
        background-color: #98FF98; /* Mint Green */
    }
    </style>
    """,
    unsafe_allow_html=True
)

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

            # マスク画像（base64形式）を取得
            mask_base64 = pred.get("mask")
            if mask_base64:
                mask_bytes = base64.b64decode(mask_base64)
                mask_image = Image.open(io.BytesIO(mask_bytes)).convert("L")

                # マスクを赤色に変換して重ねる
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
