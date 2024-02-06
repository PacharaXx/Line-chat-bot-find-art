import json
from sentence_transformers import SentenceTransformer, util
from PIL import Image
import glob

class ImageSearcher:
    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name)
        self.encoded_images = None
        self.image_names = None

    def set_image_names(self, image_names):
        self.image_names = image_names

    def load_images(self):
        if self.image_names is None:
            raise ValueError("Image names not set. Use set_image_names method.")
        encoded_images = self.model.encode([Image.open(filepath) for filepath in self.image_names],
                                           batch_size=128, convert_to_tensor=True, show_progress_bar=True)
        self.encoded_images = encoded_images

    def find_most_similar_images(self, target_image, top_k=3):
        if self.encoded_images is None:
            raise ValueError("Images not loaded. Use load_images method.")
        
        encoded_target_image = self.model.encode(target_image, convert_to_tensor=True)

        # Find similar images to the target image
        similar_images = util.semantic_search(encoded_target_image, self.encoded_images, top_k=top_k)

        # Return the most similar image paths and scores
        most_similar_image_paths = [self.image_names[int(image['corpus_id'])] for image in similar_images[0]]
        scores = [image['score'] for image in similar_images[0]]

        return most_similar_image_paths, scores

    def run_test(self, target_image_path):
        target_image = Image.open(target_image_path)
        most_similar_image_paths, scores = self.find_most_similar_images(target_image)
        
        response = [{"most_similar_image_path": image_path, "score": score} for image_path, score in zip(most_similar_image_paths, scores)]
        json_response = json.dumps(response)
        return json_response

if __name__ == '__main__':
    # Create an ImageSearcher object and load the model
    image_searcher = ImageSearcher('clip-ViT-B-32')

    # Load the image names (JPEG and JPG)
    image_names = list(glob.glob('./imgsearch/*.jpg') + glob.glob('./imgsearch/*.jpeg'))
    image_searcher.set_image_names(image_names)

    # Load the encoded images
    image_searcher.load_images()

    # Test the API with a sample target image
    target_image_path = './serverPROJECT/target/target.jpg'
    response = image_searcher.run_test(target_image_path)
    print(response)
