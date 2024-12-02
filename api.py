from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image, ImageDraw, ImageFont
import io
from pydantic import BaseModel
app = FastAPI()


class TextRequest(BaseModel):
    text: str


@app.post("/generate-image-from-text/")
async def generate_image_from_text(request: TextRequest):
    """
    Generate an image from a text input.
    """
    text = request.text
    img = Image.new("RGB", (400, 200), color="white")
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    draw.text((20, 80), text, fill="black", font=font)
    
    # Save the image to bytes
    img_byte_array = io.BytesIO()
    img.save(img_byte_array, format="PNG")
    img_byte_array.seek(0)
    return {"message": "Image generated successfully"}
@app.post("/process-image/")
async def process_image(file: UploadFile = File(...)):
    """
    Process an uploaded image and return it.
    """
    image = Image.open(file.file)
    # Example: Convert to grayscale
    grayscale_image = image.convert("L")
    
    # Save the image to bytes
    img_byte_array = io.BytesIO()
    grayscale_image.save(img_byte_array, format="PNG")
    img_byte_array.seek(0)
    return JSONResponse(content={"message": "Image processed successfully"}, media_type="application/json")
