from math import sqrt
import random
import matplotlib.pyplot as plt
import numpy as np
import sqlite3
import json
import time
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
from PIL import ImageFile
import requests
from sklearn.cluster import KMeans
class Point:
    def __init__(self, coords, n, ct):
        self.coords = coords
        self.n = n
        self.ct = ct

class ColorQuantizer:
    def __init__(self, filename, thumbnail_size=(128, 128), min_diff=1):
        self.start_time = time.time()
        self.filename = filename
        self.thumbnail_size = thumbnail_size
        self.min_diff = min_diff
        self.img = None
        self.color_names = {
            (0, 0, 255): ("Blue", 1),
            (255, 0, 0): ("Red", 2),
            (255, 255, 0): ("Yellow", 3),
            (128, 0, 128): ("Violet", 4),
            (255, 165, 0): ("Orange", 5),
            (0, 128, 0): ("Green", 6),
            (138, 43, 226): ("Blue-Violet", 7),
            (255, 69, 0): ("Red-Orange", 8),
            (255, 215, 0): ("Yellow-Orange", 9),
            (0, 128, 128): ("Blue-Green", 10),
            (128, 0, 0): ("Red-Violet", 11),
            (173, 255, 47): ("Yellow-Green", 12),
            (0, 0, 0): ("Black", 13),
            (255, 255, 255): ("White", 14),
        }
        self.end_time = time.time()
        

    def load_image(self):
        self.start_time = time.time()
        try:
            self.img = self.filename
            self.img.thumbnail(self.thumbnail_size)
            self.end_time = time.time()
            print(f"Time taken to LOAD_IMAGE: {self.end_time - self.start_time:.2f} seconds")
            return self.img
        except (IOError, Image.DecompressionBombError):
            raise ValueError("Error loading image")

    
    def get_points(self):
        # start_time = time.time()
        points = []
        w, h = self.img.size
        for count, color in self.img.getcolors(w * h):
            points.append(Point(color, 3, count))
        # end_time = time.time()
        # print(f"Time taken to GET_POINTS: {end_time - start_time:.2f} seconds")
        return points

    def rtoh(self, rgb):
        return '#%s' % ''.join(('%02x' % p for p in rgb))

    def calculate_center(self, points, n):
        # start_time = time.time()
        vals = [0.0 for i in range(n)]
        plen = 0
        for p in points:
            plen += p.ct
            for i in range(n):
                vals[i] += (p.coords[i] * p.ct)
        # end_time = time.time()
        # print(f"Time taken to CALCENTER: {end_time - start_time:.2f} seconds")
        return Point([(v / plen) for v in vals], n, 1)

    def kmeans(self, points, k, min_diff=0):
        self.start_time = time.time()

        # Extract RGB values from points
        data = np.array([p.coords for p in points])
        # Fix Expected 2D array, got 1D array instead
        if data.ndim == 1:
            data = data.reshape(-1, 1)

        print('Length of data: ',len(data))

        # Use scikit-learn's KMeans
        kmeans = KMeans(n_clusters=k, random_state=0)
        labels = kmeans.fit_predict(data)
        centroids = kmeans.cluster_centers_
        
        # Initialize centroids, the first 'k' elements in 'points' will be our initial centroids
        clusters = [Point(centroid, len(centroid), 1) for centroid in centroids]

        self.end_time = time.time()
        print(f"Time taken to KMEANS: {self.end_time - self.start_time:.2f} seconds")
        return clusters
    
    def closest(self, colors, color):
        # Convert to numpy arrays
        colors = np.array(colors)
        color = np.array(color)

        # Ensure that color has the same number of dimensions as colors
        if color.ndim == 1:
            color = color[:3]  # Take only the first three elements if there are more

        # Ensure that color has the correct shape
        if color.shape != (1, 3):
            color = color.reshape(1, -1)

        # Calculate Euclidean distances
        distances = np.sqrt(np.sum((colors - color) ** 2, axis=1))

        # Find the index of the smallest distance
        index_of_smallest = np.argmin(distances)

        # Get the closest color
        smallest_distance = colors[index_of_smallest]

        return smallest_distance, index_of_smallest




    def get_color_name(self, rgb):
        # start_time = time.time()
        closest_rgb, index = self.closest(list(self.color_names.keys()), rgb)
        color_name, color_id = self.color_names[tuple(closest_rgb)]
        # end_time = time.time()
        # print(f"Time taken to GET_COLOR_NAME: {end_time - start_time:.2f} seconds")
        return color_id, color_name


    def quantize(self, n):
        self.start_time = time.time()
        points = self.get_points()
        clusters = self.kmeans(points, n, self.min_diff)
        rgbs = [list(map(int, c.coords)) for c in clusters]

        color_descriptions = []
        for rgb in rgbs:
            hex_color = self.rtoh(rgb)
            color_id, color_name = self.get_color_name(rgb)
            color_description = {
                "ColorID": color_id,
                "ColorName": color_name,
                "HexColor": hex_color,
            }
            color_descriptions.append(color_description)

        # Convert color_descriptions list to a JSON string
        json_result = json.dumps(color_descriptions, indent=4)
        self.end_time = time.time()
        print(f"Time taken to QUANTIZE: {self.end_time - self.start_time:.2f} seconds")
        return json_result
    
    def visualize_palette(self):
        points = self.get_points()
        clusters = self.kmeans(points, 5, self.min_diff)  # You can specify the number of colors to display
        
        palette = [list(map(int, c.coords)) for c in clusters]
        hex_colors = [self.rtoh(rgb) for rgb in palette]

        fig, ax = plt.subplots(1, 1, figsize=(6, 2))  # Adjust the figure size as needed

        for i, color in enumerate(hex_colors):
            rect = plt.Rectangle((i, 0), 1, 1, facecolor=color)
            ax.add_patch(rect)

        ax.set_xlim(0, len(palette))
        ax.set_ylim(0, 1)
        ax.axis("off")  # Turn off axes

        plt.show()

    def send_All_to_DB(self):
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        self.start_time = time.time()
        i = 1
        db = sqlite3.connect('test1.db')
        cursor = db.cursor()
        # # Add artwork_id to ArtworkColors with NULL color_id and color_name if it doesn't exist
        # cursor.execute("""
        #     INSERT INTO ArtworkColors (artwork_color_id, artwork_id, color_id, color_name)
        #     SELECT (SELECT MAX(artwork_color_id) + 1 FROM ArtworkColors), artwork_id, NULL, NULL FROM Artworks
        #     WHERE artwork_id NOT IN (SELECT artwork_id FROM ArtworkColors)
        # """)
        # db.commit()  # Commit the insert statement

        # Now fetch image URLs for further processing
        cursor.execute("SELECT image_url FROM Artworks")
        image_urls = cursor.fetchall()
        
        if len(image_urls) == 0:
            print('All images have been processed')
            return
        else:
            print('ImageUrl: ',len(image_urls))
        
        for img_url in image_urls:
            if img_url[0].startswith('http'):
                self.img = Image.open(requests.get(img_url[0], stream=True).raw)
            else:
                self.img = Image.open('./imgsearch/' + img_url[0])
            self.img.thumbnail(self.thumbnail_size)
            response = self.quantize(5)

            # Parse the JSON response
            colors = json.loads(response)

            # Get the artwork_id for the current image_url
            cursor.execute("SELECT artwork_id FROM Artworks WHERE image_url = ?", (img_url[0],))
            artwork_id = cursor.fetchone()

            if artwork_id:
                artwork_id = artwork_id[0]

                # Delete existing color data for the artwork_id
                cursor.execute("DELETE FROM ArtworkColors WHERE artwork_id = ?", (artwork_id,))

                # Loop through the colors and update the ArtworkColors table
                for color in colors:
                    color_name = color['ColorName']
                    color_id = color['ColorID']

                    # Update the ArtworkColors table with the color data
                    cursor.execute(
                        "INSERT INTO ArtworkColors (artwork_color_id, artwork_id, color_name, color_id) VALUES (?, ?, ?, ?)",
                        (i,artwork_id, color_name, color_id)
                    )
                    i += 1
            # ------- for debug -------
            print(response)
            # self.visualize_palette()
            # -------------------------
            db.commit()
        cursor.close()
        db.close()
        self.end_time = time.time()
        print(f"Time taken to SEND TO DB: {self.end_time - self.start_time:.2f} seconds")



# Example usage:
if __name__ == "__main__":
    st_time = time.time()
    # filename = "imgsearch/target.jpg"  # Provide the path to your image file
    # quantizer = ColorQuantizer(filename)
    # result = quantizer.quantize(5)
    # print(result)
    # quantizer.visualize_palette()
    quantizer = ColorQuantizer('')
    quantizer.send_All_to_DB()
    ed_time = time.time()
    print(f"Time taken to ALLPROCESS: {ed_time - st_time:.2f} seconds")

