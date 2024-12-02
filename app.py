import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# Backend API base URL
API_URL = "http://172.16.87.75:8000"

st.title("Streamlit with FastAPI")

# Choose between text or image input
option = st.selectbox("Choose input type:", ["Text", "Image"])

if option == "Text":
    text_input = st.text_input("Enter your text here:")
    if st.button("Generate Image"):
        if text_input:
            response = requests.post(f"{API_URL}/generate-image-from-text/", json={"text": text_input})
            if response.status_code == 200:
                img_data = BytesIO(response.content)
                img = Image.open(img_data)
                st.image(img, caption="Generated Image", use_column_width=True)
            else:
                st.error("Failed to generate image.")
        else:
            st.error("Please enter text to generate an image.")

elif option == "Image":
    uploaded_image = st.file_uploader("Upload an image:", type=["jpg", "png", "jpeg"])
    if uploaded_image:
        if st.button("Process Image"):
            files = {"file": uploaded_image.getvalue()}
            response = requests.post(f"{API_URL}/process-image/", files=files)
            if response.status_code == 200:
                img_data = BytesIO(response.content)
                img = Image.open(img_data)
                st.image(img, caption="Processed Image", use_column_width=True)
            else:
                st.error("Failed to process image.")
