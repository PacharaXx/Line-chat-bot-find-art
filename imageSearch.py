import json
from sentence_transformers import SentenceTransformer, util
from PIL import Image
from colorclassification import ColorQuantizer
import sqlite3
import time
import pickle
import numpy as np

class ImageSearcher:
    def __init__(self):
        self.model = None
        self.encoded_images = None
        self.image_names = None
        self.target = None
        self.list_color_target = []
        self.conn = None

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

    def get_artwork_data_from_db(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT artwork_id, image_url FROM Artworks")
        artwork_data = cursor.fetchall()
        cursor.close()
        return artwork_data

    def encode_and_insert_all_images(self):
        try:
            artwork_data = self.get_artwork_data_from_db()
            for artwork_id, image_path in artwork_data:
                if image_path.startswith('http'):
                    image_path = './imgsearch/'+image_path.split('/')[-1]
                else:
                    image_path = './imgsearch/'+image_path
                self.insert_encodeds_to_db(artwork_id, image_path)
                print('Saved embedding for', image_path)
            self.conn.close()
        except Exception as e:
            print(e)
            return e
        
    def insert_encodeds_to_db(self, artwork_id, image_path):
        try:
            image = Image.open(image_path)
            encoded_image = self.model.encode(image, batch_size=128, convert_to_tensor=True, show_progress_bar=True)
            serialized_encoded_image = pickle.dumps(encoded_image)
            cursor = self.conn.cursor()
        #     artwork_encoded_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        # artwork_id INT,
        # encoded BLOB,
        # FOREIGN KEY (artwork_id) REFERENCES Artworks(artwork_id)
            cursor.execute("INSERT OR REPLACE INTO ArtworkEncodeds (artwork_id, encoded) VALUES (?, ?)", (artwork_id, serialized_encoded_image))
            self.conn.commit()
            cursor.close()
        except Exception as e:
            # if not found insert new
            print(e)
            return e
        
    # def load_encodeds_from_db(self):
    #     cursor = self.conn.cursor()
    #     cursor.execute("SELECT artwork_id, encoded FROM ArtworkEncodeds")
    #     rows = cursor.fetchall()
    #     cursor.close()

    #     encodeds = []
    #     for row in rows:
    #         artwork_id, encoded_blob = row
    #         # Deserialize the encoded blob back into the original format (e.g., TensorFlow tensor)
    #         encoded = pickle.loads(encoded_blob)
    #         encodeds.append({'artwork_id': artwork_id, 'encoded': encoded})
    #     return encodeds

    def set_encoded_images(self, encoded_images=None):
        if encoded_images is None:
            self.encoded_images = []
        else:
            self.encoded_images = encoded_images

    def load_images_from_db(self, color):
        startLoadDB = time.time()
        try:
            # Load image names from the database based on the specified color
            self.conn = sqlite3.connect('test1.db')  # Establish connection
            cursor = self.conn.cursor()
            if isinstance(color, list):
                color = list(set(color))
                # Create the SQL query to fetch artwork_id by color
                sql = """
                    SELECT artwork_id FROM ArtworkColors
                    WHERE color_name IN ({})
                """.format(', '.join('?' for _ in color))

                # Execute the SQL query with flattened color list
                cursor.execute(sql, color)
            else:
                # Create the SQL query to fetch artwork_id by color
                sql = """
                    SELECT artwork_id FROM ArtworkColors
                    WHERE color_name = ?
                """
                # Execute the SQL query
                cursor.execute(sql, (color,))
            # # Create the SQL query to fetch artwork_id by color
            # sql = """
            #     SELECT artwork_id FROM ArtworkColors
            #     WHERE color_name = ?
            # """
            # print('color:',color)
            # # Execute the SQL query
            # cursor.execute(sql, (color,))   
            artwork_ids = cursor.fetchall()
            artwork_ids = [artwork_id[0] for artwork_id in artwork_ids]
            artwork_ids = list(set(artwork_ids))
            # print len of artwork_ids that have color target
            # uniqe_artwork_ids = set(artwork_ids)
            print('Len Of artwork_ids:',len(set(artwork_ids)))

            if artwork_ids:  # Check if artwork_ids is not empty
                # Create the SQL query to fetch artwork_encodeds by artwork_id
                sql = """
                    SELECT artwork_id, encoded FROM ArtworkEncodeds
                    WHERE artwork_id IN ({})
                """.format(', '.join('?' for _ in artwork_ids))

                # Execute the SQL query with flattened artwork_ids list
                cursor.execute(sql, artwork_ids)
                rows = cursor.fetchall()

                # Deserialize the encoded blob back into the original format
                encoded_images = []
                for row in rows:
                    artwork_id, encoded_blob = row
                    encoded = pickle.loads(encoded_blob)
                    encoded_images.append({'artwork_id': artwork_id, 'encoded': encoded})

                # Set the encoded images
                self.set_encoded_images(encoded_images)

                print('Loaded encoded images from the database successfully')
            else:
                print('No images found for the specified color')

            print('Loaded image URLs from the database successfully')
        except sqlite3.Error as e:
            print("Error fetching image URLs from the database:", str(e))
        finally:
            # Close the cursor and the database connection
            if cursor:
                cursor.close()
            if self.conn:
                self.conn.close()

        endLoadDB = time.time()
        print('Time load image_names from db:', endLoadDB - startLoadDB)

    # Function to calculate cosine similarity between two vectors
    def cosine_similarity(self,vector1, vector2):
        dot_product = np.dot(vector1, vector2)
        norm_vector1 = np.linalg.norm(vector1)
        norm_vector2 = np.linalg.norm(vector2)
        cosine_similarity = dot_product / (norm_vector1 * norm_vector2)
        return cosine_similarity

    def find_most_similar_images(self, target_image):
        try:
            # encoded_target_image = self.model.encode(target_image, batch_size=128, convert_to_tensor=True, show_progress_bar=True)
            # encoded_images = [entry['encoded'] for entry in self.encoded_images]

        #     # Calculate similarity with each encoded image
        #     similarities = []
        #     for encoded_image in encoded_images:
        #         similarity = self.cosine_similarity(encoded_target_image, encoded_image)
        #         similarities.append(similarity)

        #     # Find the indices of most similar images (top-k)
        #     NUM_SIMILAR_IMAGES = 3  # Example: Find top 2 similar images
        #     most_similar_indices = np.argsort(similarities)[::-1][:NUM_SIMILAR_IMAGES]

        #     # Get the most similar images based on indices
        #     most_similar_images = [encoded_images[i] for i in most_similar_indices]

        #     # Print the most similar images
        #     print("Most similar images:")
        #     for idx, image in enumerate(most_similar_images):
        #         print(f"Similarity {idx+1}: {similarities[most_similar_indices[idx]]} - Artwork ID: {self.encoded_images[most_similar_indices[idx]]['artwork_id']}")

        #     if most_similar_images:
        #         most_similar_image_paths = [self.encoded_images[i]['artwork_id'] for i in most_similar_indices]
        #         print('most_similar_image_paths:', most_similar_image_paths)

        #         conn = sqlite3.connect('test1.db')
        #         cursor = conn.cursor()
        #         artworks = []
        #         for image_path in most_similar_image_paths:
        #             sql = """SELECT artwork_id, artwork_name, artist_name, artwork_type, artwork_size,
        #                     artwork_technique, exhibition_name, award_name, license, concept, detail, image_url,
        #                     url FROM Artworks WHERE artwork_id = ?"""
        #             cursor.execute(sql, (image_path,))
        #             row = cursor.fetchone()
        #             artworks.append({'artwork_id':row[0],'artwork_name':row[1],'artist_name':row[2],
        #                             'artwork_type':row[3],'artwork_size':row[4],'artwork_technique':row[5],
        #                             'exhibition_name':row[6],'award_name':row[7],'license':row[8],'concept':row[9],
        #                             'detail':row[10],'image_url':row[11],'url':row[12],
        #                             'score':similarities[most_similar_image_paths.index(image_path)]})
        #         return artworks
        #     else:
        #         print("Invalid structure in similar_images or no results found.")
        # except Exception as e:
        #     print(e)
        #     return e

            encoded_target_image = self.model.encode(target_image,batch_size=128, convert_to_tensor=True, show_progress_bar=True)

            # Find similar images to the target image
            NUM_SIMILAR_IMAGES = 3
            similar_images = util.semantic_search(encoded_target_image, [entry['encoded'] for entry in self.encoded_images], top_k=NUM_SIMILAR_IMAGES)
            print('similar_images:',similar_images)
            # Check if similar_images is not empty and has the expected structure
            if similar_images and len(similar_images[0]) > 0 and 'corpus_id' in similar_images[0][0]:
                # Extract the similar image indices and scores
                similar_image_indices = [entry['corpus_id'] for entry in similar_images[0]]
                scores = [entry['score'] for entry in similar_images[0]]

                # Extract the filenames of the most similar images
                most_similar_image_paths = [self.encoded_images[i]['artwork_id'] for i in similar_image_indices]
                print('most_similar_image_paths:', most_similar_image_paths)
                
                conn = sqlite3.connect('test1.db')
                cursor = conn.cursor()
                artworks = []
                for image_path in most_similar_image_paths:
                    sql = """SELECT artwork_id, artwork_name, artist_name, artwork_type, artwork_size,
                            artwork_technique, exhibition_name, award_name, license, concept, detail, image_url,
                            url FROM Artworks WHERE artwork_id = ?"""
                    cursor.execute(sql, (image_path,))
                    row = cursor.fetchone()
                    artworks.append({'artwork_id':row[0],'artwork_name':row[1],'artist_name':row[2],
                                    'artwork_type':row[3],'artwork_size':row[4],'artwork_technique':row[5],
                                    'exhibition_name':row[6],'award_name':row[7],'license':row[8],'concept':row[9],
                                    'detail':row[10],'image_url':row[11],'url':row[12],
                                    'score':scores[most_similar_image_paths.index(image_path)]})
                return artworks
            else:
                print("Invalid structure in similar_images or no results found.")

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
            self.conn = sqlite3.connect('test1.db')
            # Load image names from the database based on the specified color 
            # and set the encoded images
            self.load_images_from_db(colors)
            # Find the most similar image
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
        
    def encoded_to_DB(self):
        try:
            self.conn = sqlite3.connect('test1.db')
            self.encode_and_insert_all_images()
        except Exception as e:
            print(e)
            return e
        
if __name__ == '__main__':
    # send encoded to db
    im = ImageSearcher()
    im.set_model('clip-ViT-B-32')
    im.load_model()
    im.encoded_to_DB()




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
    
