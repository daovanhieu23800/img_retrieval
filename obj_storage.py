from minio import Minio
import os

# Initialize MinIO client
client = Minio(
    "127.0.0.1:9000",  # Example: "localhost:9000"
    access_key="minioaccesskey",
    secret_key="miniosecretkey",
    secure=False  # Set to True if using https
)
