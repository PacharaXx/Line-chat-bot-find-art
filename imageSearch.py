import json
from sentence_transformers import SentenceTransformer, util
from PIL import Image
from colorclassification import ColorQuantizer
import sqlite3

class ImageSearcher:
    def __init__(self):
        self.model = None
        self.encoded_images = None
        self.image_names = None
        self.target = None
        self.list_color_target = []

    def set_image_names(self, image_names):
        self.image_names = image_names

    def set_model(self, model):
        self.model = model

    def set_target(self, target):
        self.target = target

    def set_list_color_target(self):
        quantizer = ColorQuantizer(self.target)
        result = quantizer.quantize(5)
        print(result)
        self.list_color_target = result

    def load_model(self):
        self.model = SentenceTransformer(self.model)

    def load_images(self):
        try:
            encoded_images =    self.model.encode([Image.open(filepath) for filepath in self.image_names],
                                            batch_size=250, convert_to_tensor=True, show_progress_bar=True)
            print('len encoded_images',len(encoded_images))
            self.encoded_images = encoded_images
        except Exception as e:
            print(e)
            return e

    def load_images_from_db(self,color):
        # Load the image names jpg and jpeg in db
        # fetch image names from db to list by color
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()
        try:
            # Fetch image URLs based on the specified color
            cursor.execute("SELECT image_url FROM Artworks WHERE artwork_id IN (SELECT artwork_id FROM ArtworkColors WHERE color_name = ?)", (color,))
            
            # Fetch the results as a list of image URLs
            image_urls = [f'./imgsearch/{row[0]}' for row in cursor.fetchall()]
            print(image_urls)
            self.image_names = image_urls
        except sqlite3.Error as e:
            print("Error fetching image URLs from the database:", str(e))
        finally:
            # Close the cursor and the database connection
            cursor.close()
            conn.close()
        pass

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
        response = []
        colors = self.list_color_target
        for color in colors:
            self.load_images_from_db(color)
            self.load_images()
            most_similar_image_path, score = self.find_most_similar_images(self.target)
            if score[0] >= 0.9:
                break
        if (len(most_similar_image_path) <= 2):
            for i in range(len(most_similar_image_path)):
                response.append({'most_similar_image_path': most_similar_image_path[i], 'score': score[i]})
        json_response = json.dumps(response)
        return json_response


# just for run test
if __name__ == '__main__':
    # Create an ImageSearcher object
    image_searcher = ImageSearcher()
    image_searcher.set_model('clip-ViT-B-32')
    image_searcher.load_model()
    print('create image_searcher success')

    # image_searcher.load_images_from_db('Red')

    # # Load the image names jpg and jpeg
    # image_names = list(glob.glob('./imgsearch/*.jpg') + glob.glob('./imgsearch/*.jpeg'))
    # image_searcher.set_image_names(image_names)  # No need to assign this to a variable
    # print('load image_names success')

    # Load the encoded images
    # image_searcher.load_images()
    # print('load encoded_images success')

    # Test the API with a sample image file
    image_searcher.set_target(Image.open('./target/target.jpg'))
    print('set target success')
    image_searcher.set_list_color_target()
    response = image_searcher.run_test()
    print(response)
    # print("Most similar image path:", response['most_similar_image_path'])
    # print("Score:", response['score'])

    # # Test the API with a sample image file
    # target_image2 = Image.open('./237047.jpg')  # Load your target image
    # most_similar_image_path2 = image_searcher.find_most_similar_image(target_image2)
    # print("Most similar image path:", most_similar_image_path2)
    # print("Score:", util.pytorch_cos_sim(image_searcher.encoded_images, image_searcher.model.encode(target_image2, convert_to_tensor=True)))
    # # show the most similar image
    # most_similar_image2 = Image.open(most_similar_image_path2)
    # most_similar_image2.show()
    
