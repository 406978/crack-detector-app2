import streamlit as st
import requests
from PIL import Image, ImageDraw
import io
import base64

# Secrets から API キーを取得
API_KEY = st.secrets["ROBOFLOW_API_KEY"]

# Roboflow 推論 API の URL（セグメンテーションモデル）
PROJECT_NAME = "-1121"
VERSION = "3"
ROBOFLOW_API_URL = f"https://detect.roboflow.com/{PROJECT_NAME}/{VERSION}?api_key={API_KEY}"

st.title("ひび割れ検出アプリ（セグメンテーション対応）")

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
        mask_data = result.get("mask", "")

        if mask_data:
            # Base64マスク画像をデコード
            mask_base64 = mask_data.split(",")[1]
            mask_bytes = base64.b64decode(mask_base64)
            mask_image = Image.open(io.BytesIO(mask_bytes)).convert("RGBA")

            # マスクの透明度を調整
            mask_image.putalpha(128)

            # 元画像とマスクを合成
            overlay = Image.alpha_composite(image.convert("RGBA"), mask_image)
            st.image(overlay, caption="検出結果（セグメンテーションマスク）", use_container_width=True)
        else:
            st.warning("セグメンテーションマスクが含まれていません。モデルがセグメンテーションに対応しているか確認してください。")

        # 測定結果の表示
        st.write("検出されたひび割れ領域：")
        for pred in predictions:
            width = pred.get("width")
            height = pred.get("height")
            x = pred.get("x")
            y = pred.get("y")
            class_name = pred.get("class", "crack")
            st.write(f"位置: ({x:.1f}, {y:.1f})、幅: {width:.1f}px、高さ: {height:.1f}px、クラス: {class_name}")
    else:
        st.error("Roboflow APIの呼び出しに失敗しました。")
        st.text(f"ステータスコード: {response.status_code}")
        st.text(response.text)
        st.text(f"マスクデータの先頭: {mask_data[:100]}")

