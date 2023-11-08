import json
from sentence_transformers import SentenceTransformer, util
from PIL import Image
from colorclassification import ColorQuantizer
import sqlite3
import requests
import time
from io import BytesIO

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
        try:
            quantizer = ColorQuantizer(self.target)
            quantizer.load_image()
            result = quantizer.quantize(5)
            self.list_color_target = [color['ColorName'] for color in json.loads(result)]
            print('List color target:',self.list_color_target)
        except Exception as e:
            print(e)
            return e

    def load_model(self):
        self.model = SentenceTransformer(self.model)

    def load_images(self):
        startLoadImage = time.time()
        encoded_images = []
        for filepath in self.image_names:
            if filepath.startswith('http'):
                image = Image.open('./imgsearch/'+filepath.split('/')[-1])
            else:
                image = Image.open(filepath)
            encoded_images.append(image)
        try:
            print('len of encoded_images:',len(encoded_images))
            self.encoded_images = self.model.encode(encoded_images,batch_size=128, convert_to_tensor=True, show_progress_bar=True)
            endLoadImage = time.time()
            print('Time load images:',endLoadImage-startLoadImage)
        except Exception as e:
            print(e)
            return e

    def load_images_from_db(self, color):
        startLoadDB = time.time()

        try:
            # Load image names from the database based on the specified color
            conn = sqlite3.connect('test1.db')
            cursor = conn.cursor()

            # Create the SQL query to fetch image URLs by color
            sql = "SELECT image_url FROM Artworks WHERE artwork_id IN (SELECT artwork_id FROM ArtworkColors WHERE color_name = ?)"
            cursor.execute(sql, (color,))
            result = cursor.fetchall()

            if not result:
                print('No images found for the specified color')
                return

            # Extract image URLs from the result set
            image_names = [row[0] for row in result]

            # Set image_names attribute in your class
            self.set_image_names(image_names)

            print('Loaded image URLs from the database successfully')
        except sqlite3.Error as e:
            print("Error fetching image URLs from the database:", str(e))
        finally:
            # Close the cursor and the database connection
            cursor.close()
            conn.close()

        endLoadDB = time.time()
        print('Time load image_names from db:', endLoadDB - startLoadDB)

    def find_most_similar_images(self, target_image):
        try:
            encoded_target_image = self.model.encode(target_image, convert_to_tensor=True)

            # Find similar images to the target image
            NUM_SIMILAR_IMAGES = 3
            similar_images = util.semantic_search(encoded_target_image, self.encoded_images, top_k=NUM_SIMILAR_IMAGES)

            # Sort the similar images by score and return only top three scores
            similar_images = sorted(similar_images[0], key=lambda x: x['score'], reverse=True)[:3]

            # Return the most similar image
            most_similar_image_paths = [self.image_names[int(image['corpus_id'])] for image in similar_images]
            scores = [image['score'] for image in similar_images]

            # get data from db by use image_names 
            # fetch image names from db to list by color
            conn = sqlite3.connect('test1.db')
            cursor = conn.cursor()
            artworks = []
            for image_path in most_similar_image_paths:
                sql = f"SELECT * FROM Artworks WHERE image_url = ?"
                cursor.execute(sql, (image_path,))
                row = cursor.fetchone()
                artworks.append({'artwork_id':row[0],'artwork_name':row[1],'artist_name':row[2],'artwork_type':row[3],'artwork_size':row[4],'artwork_technique':row[5],'exhibition_name':row[6],'award_name':row[7],'license':row[8],'concept':row[9],'detail':row[10],'image_url':row[11],'url':row[12],'score':scores[most_similar_image_paths.index(image_path)]})
            return artworks

        except Exception as e:
            print(e)
            return e


    # def api_endpoint(self, request):
    #     target_image = Image.open(request.files['target'])
    #     most_similar_image = self.find_most_similar_image(target_image)

    #     # Return the top three similar images path and their scores

    def run_test(self):
        try:
            print('target :',self.target)
            self.set_list_color_target()
            colors = self.list_color_target
            for color in colors:
                self.load_images_from_db(color)
                self.load_images()
                artworks = self.find_most_similar_images(self.target)
                if artworks is not None:
                    return artworks
                else:
                    return 'No images found'
        except Exception as e:
            # Handle exceptions and return an error message
            error_message = {'error': str(e)}
            json_error = json.dumps(error_message)
            print('Error:', json_error)
            return json_error



# just for run test
# if __name__ == '__main__':
#     # Create an ImageSearcher object
#     image_searcher = ImageSearcher()
#     image_searcher.set_model('clip-ViT-B-32')
#     image_searcher.load_model()
#     print('create image_searcher success')

    # image_searcher.load_images_from_db('Red')

    # # Load the image names jpg and jpeg
    # image_names = list(glob.glob('./imgsearch/*.jpg') + glob.glob('./imgsearch/*.jpeg'))
    # image_searcher.set_image_names(image_names)  # No need to assign this to a variable
    # print('load image_names success')

    # Load the encoded images
    # image_searcher.load_images()
    # print('load encoded_images success')

    # Test the API with a sample image file
    # image_searcher.set_target(Image.open('./target/target.jpg'))
    # print('set target success')
    # image_searcher.set_list_color_target()
    # response = image_searcher.run_test()
    # print(response)
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
    
