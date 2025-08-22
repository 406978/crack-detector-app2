
import streamlit as st
import requests
from PIL import Image
import io

# Secrets から API キーを取得
API_KEY = st.secrets["ROBOFLOW_API_KEY"]

# Roboflow 推論 API の正しい URL を構築
# プロジェクト名とバージョンは Roboflow の Deploy タブから確認
PROJECT_NAME = "-1121"  # 例: あなたのプロジェクト名
VERSION = "3"  # 例: モデルのバージョン番号
ROBOFLOW_API_URL = f"https://detect.roboflow.com/{PROJECT_NAME}/{VERSION}?api_key={API_KEY}"

st.title("ひび割れ検出アプリ")

uploaded_file = st.file_uploader("画像をアップロードしてください", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="アップロード画像", use_column_width=True)

    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    buffered.seek(0)

    response = requests.post(
        ROBOFLOW_API_URL,
        files={"file": buffered.getvalue()}
    )

    if response.status_code == 200:
        predictions = response.json().get("predictions", [])
        st.write("検出結果：")
        for pred in predictions:
            width = pred.get("width")
            x = pred.get("x")
            y = pred.get("y")
            st.write(f"位置: ({x}, {y})、幅: {width}px")
    else:
        st.error("Roboflow APIの呼び出しに失敗しました。")
        st.text(f"ステータスコード: {response.status_code}")
        st.text(response.text)
