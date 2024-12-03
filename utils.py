import torch
from transformers import ViTFeatureExtractor, ViTModel
from PIL import Image
from sklearn.preprocessing import normalize


class FeatureExtractor:
    def __init__(self, model_name="google/vit-base-patch16-224", device="cpu"):
        """
        Initialize the ViT feature extractor.
        :param model_name: Pre-trained ViT model name from Hugging Face.
        """
        # Load the feature extractor and model
        self.device = device
        self.feature_extractor = ViTFeatureExtractor.from_pretrained(
            'google/vit-base-patch16-224-in21k')
        self.model = ViTModel.from_pretrained(
            'google/vit-base-patch16-224-in21k').to(self.device)
        self.model.eval()  # Set the model to evaluation mode

    # def __call__(self, image_path):

    def __call__(self, image):
        """
        Extract feature vector from an image using ViT.
        :param image_path: Path to the input image.
        :return: Normalized feature vector as a 1D numpy array.
        """
        # Load the image and preprocess it
        # image = Image.open(image_path).convert(
        #     "RGB")  # Ensure the image is in RGB
        inputs = self.feature_extractor(images=image, return_tensors="pt").to(self.device)

        # Perform inference
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Extract the feature vector from the last hidden state
        feature_vector = outputs.last_hidden_state.mean(
            dim=1).squeeze().cpu().numpy()

        # Normalize the feature vector
        return normalize(feature_vector.reshape(1, -1), norm="l2").flatten()
