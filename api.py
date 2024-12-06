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
from prometheus_fastapi_instrumentator import Instrumentator
import time
# Lifespan to manage resources

resources = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager to handle startup and shutdown.
    """
    # Initialize resources
    vector_database = VectorDatabase()
    img_feature_extractor = FeatureExtractor(device="cuda:0")
    # img_feature_extractor = FeatureExtractor()

    minio_database = MinioDatabase()

    resources["vector_database"] = vector_database
    resources["img_feature_extractor"] = img_feature_extractor
    resources["minio_database"] = minio_database
    instrumentator.expose(app)
    yield
    # Clean up the ML models and release the resources
    resources.clear()


# Create FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)
instrumentator = Instrumentator().instrument(app)

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
    start_time = time.time()
    results = vector_database.query(features, brute_force=False)
    print(start_time-time.time())
    # Prepare a list of images
    image_streams = []
    for result in results.points:
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


@ app.post("/get-image-feature/")
async def process_image(file: UploadFile = File(...)):
    """
    Process an uploaded image, query results, and retrieve multiple images from MinIO.
    """
    # Access resources
    img_feature_extractor = resources["img_feature_extractor"]

    # Read the uploaded file
    contents = await file.read()
    # print(contents, file)
    img = Image.open(io.BytesIO(contents))
    # print(img)
    # Extract features and query the vector database
    features = img_feature_extractor(img)
    # print(features)
    # Prepare a list of imag

    # Return images as JSON (Base64-encoded)
    return {"features": str(features)}


@ app.post("/get-image-test/")
async def process_image(file: UploadFile = File(...)):
    """
    Process an uploaded image, query results, and retrieve multiple images from MinIO.
    """
    # Access resources
    vector_database = resources["vector_database"]
    img_feature_extractor = resources["img_feature_extractor"]
    minio_database = resources["minio_database"]

    # Read the uploaded file
    # contents = await file.read()
    # img = Image.open(io.BytesIO(contents))
    contents = await file.read()

    img = Image.open(io.BytesIO(contents))
    # Extract features and query the vector database
    features = img_feature_extractor(img)
    # start_time = time.time()
    results = vector_database.query(features, brute_force=False)
    # print(time.time()-start_time)
    # Prepare a list of images
    image_streams = []
    for result in results.points:
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
    return
