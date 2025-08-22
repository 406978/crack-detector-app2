
import streamlit as st
import requests
from PIL import Image, ImageDraw
import io

# スケール係数（例: 1px = 0.1mm）
PIXEL_TO_MM = 0.1

# Secrets から API キーを取得
API_KEY = st.secrets["ROBOFLOW_API_KEY"]

# Roboflow 推論 API の URL（YOLOv8sモデル）
PROJECT_NAME = "-1121"
VERSION = "3"
ROBOFLOW_API_URL = f"https://detect.roboflow.com/{PROJECT_NAME}/{VERSION}?api_key={API_KEY}"

st.title("ひび割れ検出アプリ（YOLOv8sモデル対応）")

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

        draw = ImageDraw.Draw(image)
        st.write("検出されたひび割れ領域：")
        for pred in predictions:
            width = pred.get("width")
            height = pred.get("height")
            x = pred.get("x")
            y = pred.get("y")
            class_name = pred.get("class", "crack")

            # バウンディングボックスの座標を計算
            left = x - width / 2
            top = y - height / 2
            right = x + width / 2
            bottom = y + height / 2

            # バウンディングボックスを描画
            draw.rectangle([left, top, right, bottom], outline="red", width=2)
            draw.text((left, top - 10), f"{class_name}", fill="red")

            # 幅をmmに変換
            width_mm = width * PIXEL_TO_MM
            st.write(f"位置: ({x:.1f}, {y:.1f})、幅: {width:.1f}px（約 {width_mm:.1f}mm）、高さ: {height:.1f}px")

        st.image(image, caption="検出結果（バウンディングボックス）", use_container_width=True)
    else:
        st.error("Roboflow APIの呼び出しに失敗しました。")
        st.text(f"ステータスコード: {response.status_code}")
        st.text(response.text)
