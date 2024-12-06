import time
from locust import HttpUser, task, between
import io
from PIL import Image


class FastAPI(HttpUser):
    wait_time = between(1, 15)
    host = "http://127.0.0.1:8000"
    # @task
    # def hello_world(self):
    #     self.client.get("/")

    @task
    def image_retrival(self):
        img = Image.new('RGB', (128, 128), color=(
            255, 0, 0))  # Create a red image
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        # Send the image as multipart/form-data
        files = {"file": img_byte_arr.getvalue()}
        with self.client.post("/get-image-test/", files=files, catch_response=True) as response:
            print(response.status_code)
            if response.status_code == 200:
                # Log success and validate response
                # print(response)
                response.success()
                # response_json = response.json()
                # if "features" in response_json and isinstance(response_json["features"], list):
                #     response.success()
                # else:
                #     response.failure("Response does not contain valid 'features'")
            else:
                response.failure(f"Failed with status {response.status_code}")
