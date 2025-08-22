import streamlit as st
import requests
from PIL import Image
import io

API_KEY = st.secrets["ROBOFLOW_API_KEY"]

ROBOFLOW_API_URL = "https://detect.roboflow.com/-1121/3?api_key=thLVPRMwb08fXYlWxBB9"


st.title("ひび割れ検出アプリ")

uploaded_file = st.file_uploader("画像をアップロードしてください", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="アップロード画像", use_column_width=True)

    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    response = requests.post(
        f"{ROBOFLOW_API_URL}?api_key={API_KEY}",
        files={"file": buffered.getvalue()}
    )

    if response.status_code == 200:
        predictions = response.json()["predictions"]
        st.write("検出結果：")
        for pred in predictions:
            width = pred["width"]
            x = pred["x"]
            y = pred["y"]
            st.write(f"位置: ({x}, {y})、幅: {width}px")
    else:
        st.error("Roboflow APIの呼び出しに失敗しました。")
