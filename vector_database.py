from qdrant_client import models, QdrantClient
from qdrant_client.models import PointStruct

from utils import FeatureExtractor
import os
import uuid  # To generate unique IDs for each point
import time


class VectorDatabase():
    def __init__(self) -> None:
        self.feature_extractor = FeatureExtractor()
        self.qdrant_client = QdrantClient(url="http://localhost:6333")
        self.collection_name = "img_embed"
        # self.populate_data()

    def query(self, image_embedding, brute_force=False):
        # image_embedding = self.feature_extractor(filepath).tolist()
        start_time = time.time()

        search_result = self.qdrant_client.query_points(
            collection_name=self.collection_name,
            query=image_embedding,
            with_payload=True,
            limit=5,
            search_params=models.SearchParams(exact=brute_force)
        )
        end_time = time.time()

# Calculate elapsed time
        elapsed_time = end_time - start_time
        print(f"Search compl123ete1d in {elapsed_time:.4f} seconds.")
        # print(search_result)
        return search_result
    # def populate_data(self):
    #     # Check if collection exists, if not create it
    #     try:
    #         self.qdrant_client.get_collection(self.collection_name)
    #     except Exception:
    #         self.qdrant_client.create_collection(
    #             collection_name=self.collection_name,
    #             vectors_config=models.VectorParams(
    #                 size=768,  # Adjust size based on your vector dimension
    #                 distance=models.Distance.DOT,  # Dot product distance
    #             ),
    #         )
    #     # Root directory for images
    #     root = "./reverse_image_search/train/ambulance"

    #     insert = True
    #     if insert:
    #         # Walk through the directory and process each image
    #         for dirpath, foldername, filenames in os.walk(root):
    #             for filename in filenames:
    #                 if filename.endswith(".JPEG"):
    #                     filepath = os.path.join(dirpath, filename)

    #                     # Extract the image embedding
    #                     image_embedding = self.feature_extractor(filepath)

    #                     # Create a unique ID for each point
    #                     point_id = str(uuid.uuid4())

    #                     # Create the payload as a dictionary (you can add more metadata here)
    #                     payload = {"filepath": filepath}
    #                     # print(payload, image_embedding.shape)
    #                     # Upload the point to the Qdrant collection
    #                     self.qdrant_client.upload_points(
    #                         # Ensure this matches your collection name
    #                         collection_name=self.collection_name,
    #                         points=[models.PointStruct(
    #                             id=point_id,  # Unique ID
    #                             vector=image_embedding.tolist(),  # Ensure this is a list
    #                             payload=payload  # Payload should be a dictionary
    #                         )],
    #                     )
    #                     # print(response)
    #     return

    # if __name__ == "__main__":
    #     vector_database = VectorDatabase()
    #     vector_database.query(
    #         "./reverse_image_search/train/Afghan_hound/n02088094_1045.JPEG")
