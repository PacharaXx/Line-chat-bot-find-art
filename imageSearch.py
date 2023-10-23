import json
from sentence_transformers import SentenceTransformer, util
from PIL import Image
import glob

class ImageSearcher:
    def __init__(self):
        self.model = None
        self.encoded_images = None
        self.image_names = None
        self.target = None

    def set_image_names(self, image_names):
        self.image_names = image_names

    def set_model(self, model):
        self.model = model

    def set_target(self, target):
        self.target = target

    def load_model(self):
        self.model = SentenceTransformer(self.model)

    def load_images(self):
        encoded_images =    self.model.encode([Image.open(filepath) for filepath in self.image_names],
                                           batch_size=128, convert_to_tensor=True, show_progress_bar=True)
        # print len of image
        print(len(encoded_images))
        self.encoded_images = encoded_images

    def find_most_similar_images(self, target_image):
        encoded_target_image = self.model.encode(target_image, convert_to_tensor=True)

        # Find similar images to the target image
        NUM_SIMILAR_IMAGES = 3
        similar_images = util.semantic_search(encoded_target_image, self.encoded_images, top_k=NUM_SIMILAR_IMAGES)

        # Sort the similar images by score and return only top three scores
        similar_images = sorted(similar_images[0], key=lambda x: x['score'], reverse=True)[:3]

        # Return the most similar image
        most_similar_image_paths = [self.image_names[int(image['corpus_id'])] for image in similar_images]
        scores = [image['score'] for image in similar_images]

        return most_similar_image_paths, scores


    # def api_endpoint(self, request):
    #     target_image = Image.open(request.files['target'])
    #     most_similar_image = self.find_most_similar_image(target_image)

    #     # Return the top three similar images path and their scores

    
    def run_test(self):
        most_similar_image_path, score = self.find_most_similar_images(self.target)
        # Return the top three similar images path and their scores
        response = [
            {'most_similar_image_path_1': most_similar_image_path[0],
            'score_1': score[0]},
            {'most_similar_image_path_2': most_similar_image_path[1],
            'score_2': score[1]},
            {'most_similar_image_path_3': most_similar_image_path[2],
            'score_3': score[2]}
        ]

        json_response = json.dumps(response)
        return json_response


# just for run test
if __name__ == '__main__':
    # Create an ImageSearcher object
    image_searcher = ImageSearcher()
    image_searcher.set_model('clip-ViT-B-32')
    image_searcher.load_model()
    print('create image_searcher success')

    # Load the image names jpg and jpeg
    image_names = list(glob.glob('./imgsearch/*.jpg') + glob.glob('./imgsearch/*.jpeg'))
    image_searcher.set_image_names(image_names)  # No need to assign this to a variable
    print('load image_names success')

    # Load the encoded images
    image_searcher.load_images()
    print('load encoded_images success')

    # Test the API with a sample image file
    image_searcher.set_target(Image.open('./serverPROJECT/target/target.jpg'))
    print('set target success')
    response = image_searcher.run_test()
    print(response)
    # print("Most similar image path:", response['most_similar_image_path'])
    # print("Score:", response['score'])

    # Test the API with a sample image file
    target_image2 = Image.open('./237047.jpg')  # Load your target image
    most_similar_image_path2 = image_searcher.find_most_similar_image(target_image2)
    print("Most similar image path:", most_similar_image_path2)
    print("Score:", util.pytorch_cos_sim(image_searcher.encoded_images, image_searcher.model.encode(target_image2, convert_to_tensor=True)))
    # show the most similar image
    most_similar_image2 = Image.open(most_similar_image_path2)
    most_similar_image2.show()
    
