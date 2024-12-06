import streamlit as st
import requests
from PIL import Image
import io

# Backend API base URL
API_URL = "http://127.0.0.1:8000"

st.title("Streamlit with FastAPI")

# Choose between text or image input
option = st.selectbox("Choose input type:", ["Image"])

if option == "Text":
    text_input = st.text_input("Enter your text here:")
    if st.button("Generate Image"):
        if text_input.strip():
            # Send the text to the FastAPI endpoint
            response = requests.post(
                f"{API_URL}/generate-image-from-text/",
                json={"text": text_input}
            )
            if response.status_code == 200:
                # Load the image from the response
                img = Image.open(BytesIO(response.content))
                st.image(img, caption="Generated Image", use_column_width=True)
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
        else:
            st.warning("Please enter some text to generate an image.")
elif option == "Image":
    uploaded_image = st.file_uploader(
        "Upload an image:", type=["jpg", "png", "jpeg"]
    )
    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded Image",
                 use_column_width=True)
        if st.button("Process Image"):
            # Send the uploaded image to FastAPI
            files = {"file": uploaded_image.getvalue()}
            # print(files)
            response = requests.post(f"{API_URL}/process-image/", files=files)
            if response.status_code == 200:
                data = response.json()
                images = [Image.open(io.BytesIO(bytes.fromhex(image_hex)))
                          for image_hex in data["images"]]

                # Render images in rows and columns
                cols_per_row = 3  # Number of columns per row
                for i in range(0, len(images), cols_per_row):
                    cols = st.columns(cols_per_row)
                    for col, img in zip(cols, images[i:i+cols_per_row]):
                        with col:
                            st.image(img, use_column_width=True)
            else:
                st.error(
                    f"Failed to process the image: {response.status_code}")
