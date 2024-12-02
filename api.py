from fastapi import FastAPI, File, UploadFile, Depends
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
from PIL import Image, ImageDraw, ImageFont
import io
from pydantic import BaseModel
from vector_database import VectorDatabase
from obj_storage import MinioDatabase
from utils import FeatureExtractor
import os
# Lifespan to manage resources

resources = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager to handle startup and shutdown.
    """
    # Initialize resources
    vector_database = VectorDatabase()
    img_feature_extractor = FeatureExtractor()
    minio_database = MinioDatabase()

    resources["vector_database"] = vector_database
    resources["img_feature_extractor"] = img_feature_extractor
    resources["minio_database"] = minio_database

    yield
    # Clean up the ML models and release the resources
    resources.clear()


# Create FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)


# Request model
class TextRequest(BaseModel):
    text: str


@app.get("/")
def read_root():
    return {"Hello": "Hieu"}


@app.post("/generate-image-from-text/")
async def generate_image_from_text(request: TextRequest):
    """
    Generate an image from a text input.
    """
    # Access resources if needed
    # img_feature_extractor = resources["img_feature_extractor"]

    text = request.text
    img = Image.new("RGB", (400, 200), color="white")
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    draw.text((20, 80), text, fill="black", font=font)

    # Save the image to bytes
    img_byte_array = io.BytesIO()
    img.save(img_byte_array, format="PNG")
    img_byte_array.seek(0)

    return StreamingResponse(img_byte_array, media_type="image/png")


# @app.post("/process-image/")
# async def process_image(file: UploadFile = File(...)):
#     """
#     Process an uploaded image and return multiple processed images.
#     """
#     # Access resources
#     vector_database = resources["vector_database"]
#     img_feature_extractor = resources["img_feature_extractor"]
#     minio_database = resources["minio_database"]

#     # Read the uploaded file
#     contents = await file.read()
#     img = Image.open(io.BytesIO(contents))

#     # Extract features and query vector database
#     features = img_feature_extractor(img)
#     # Replace with actual query logic
#     results = vector_database.query(features)

#     # Stream images one by one
#     async def image_generator():
#         for result in results:
#             # Assuming 'filepath' in result payload
#             file_path = result.payload.get("filepath")
#             bucket_name = "image"  # Replace with your bucket name

#             try:
#                 # Fetch the image from MinIO
#                 image_bytes = minio_database.read_image_from_minio(
#                     bucket_name, os.path.basename(file_path))

#                 # Convert bytes to proper format for streaming
#                 yield (
#                     b"--image_boundary\r\n"
#                     b"Content-Type: image/png\r\n"
#                     b"\r\n" + image_bytes.read() + b"\r\n"
#                 )
#             except Exception as e:
#                 print(f"Error fetching file from MinIO: {e}")

#     # Return a streaming response for multipart image content
#     return StreamingResponse(
#         image_generator(),
#         media_type="multipart/x-mixed-replace; boundary=image_boundary"
#     )

# @app.post("/process-image/")
# async def process_image(file: UploadFile = File(...)):
#     """
#     Process an uploaded image and return the processed image.
#     """
#     # Access resources
#     print(resources)
#     vector_database = resources["vector_database"]
#     img_feature_extractor = resources["img_feature_extractor"]
#     minio_database = resources["minio_database"]
#     # Read the uploaded file
#     contents = await file.read()
#     img = Image.open(io.BytesIO(contents))

#     # Example: Extract features and query vector database
#     features = img_feature_extractor(img)
#     results = vector_database.query(features)
#     print(results)
#     # Stream images one by one
#     async def image_generator():
#         for result in results:
#             # Assuming 'filepath' is in the payload
#             file_path = result.payload.get("filepath")
#             print(os.path.basename(file_path))
#             bucket_name = "image"  # Replace with your bucket name

#             try:
#                 # Fetch the image from MinIO
#                 image_bytes = minio_database.read_image_from_minio(
#                     bucket_name, os.path.basename(file_path))
#                 yield image_bytes.read()  # Stream image content
#             except Exception as e:
#                 print(f"Error fetching file from MinIO: {e}")

#     return StreamingResponse(image_generator(), media_type="image/png")
#     # # print(results)
    # return_images = []

    # # Process each result
    # for result in results:
    #     # Assuming 'filepath' is in the payload
    #     file_path = result.payload.get("filepath")
    #     print(os.path.basename(file_path))
    #     bucket_name = "image"  # Replace with your bucket name

    #     try:
    #         # Fetch the image from MinIO
    #         image_bytes = minio_database.read_image_from_minio(
    #             bucket_name, os.path.basename(file_path))
    #         image_stream = io.BytesIO(image_bytes.read())
    #         return_images.append(image_stream)
    #     except Exception as e:
    #         print(f"Error fetching file from MinIO: {e}")

    # return StreamingResponse(return_images, media_type="image/png")

    # return {"message": "No images retrieved from MinIO."}

@app.post("/process-image/")
async def process_image(file: UploadFile = File(...)):
    """
    Process an uploaded image, query results, and retrieve multiple images from MinIO.
    """
    # Access resources
    vector_database = resources["vector_database"]
    img_feature_extractor = resources["img_feature_extractor"]
    minio_database = resources["minio_database"]

    # Read the uploaded file
    contents = await file.read()
    img = Image.open(io.BytesIO(contents))

    # Extract features and query the vector database
    features = img_feature_extractor(img)
    results = vector_database.query(features)

    # Prepare a list of images
    image_streams = []
    for result in results:
        file_path = result.payload.get("filepath")
        bucket_name = "image"

        try:
            # Fetch image from MinIO
            image_bytes = minio_database.read_image_from_minio(
                bucket_name, os.path.basename(file_path))
            retrieved_img = Image.open(image_bytes)

            # Optional: Annotate the image
            draw = ImageDraw.Draw(retrieved_img)
            font = ImageFont.load_default()
            draw.text(
                (10, 10), f"Score: {result.score:.2f}", fill="blue", font=font)

            # Convert image to bytes and store in the list
            img_byte_array = io.BytesIO()
            retrieved_img.save(img_byte_array, format="PNG")
            img_byte_array.seek(0)
            image_streams.append(img_byte_array.getvalue())

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

    # Return images as JSON (Base64-encoded)
    return {"images": [image_stream.hex() for image_stream in image_streams]}
