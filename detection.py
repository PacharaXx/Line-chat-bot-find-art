import cv2
import numpy as np
from PIL import Image
import time

class ImageProcessor:
    def __init__(self):
        self.img = None

    def set_img(self, img):
        starttime = time.time()
        self.img = np.array(img)
        endtime = time.time()
        print(f"Time taken to SET_IMG: {endtime - starttime:.2f} seconds")

    def preprocess_and_crop_image(self):
        starttime = time.time()
        # Convert the input image to grayscale
        grayscale_img = cv2.cvtColor(self.img, cv2.COLOR_RGB2GRAY)
        endtime = time.time()
        print(f"Time taken to CONVERT_TO_GRAYSCALE: {endtime - starttime:.2f} seconds")

        # Reduce noise in the image
        starttime = time.time()
        blur = cv2.GaussianBlur(grayscale_img, (5, 5), 200)
        endtime = time.time()
        print(f"Time taken to REMOVE_NOISE: {endtime - starttime:.2f} seconds")

        # Detect edges in the image using Canny edge detection
        starttime = time.time()
        edges = cv2.Canny(blur, 100, 100)
        endtime = time.time()
        print(f"Time taken to CANNY_EDGE_DETECTION: {endtime - starttime:.2f} seconds")

        # Find contours in the image
        starttime = time.time()
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        endtime = time.time()
        print(f"Time taken to FIND_CONTOURS: {endtime - starttime:.2f} seconds")

        # Initialize variables to store minimum and maximum coordinates
        starttime = time.time()
        min_x, min_y = float('inf'), float('inf')
        max_x = max_y = -float('inf')

        # Find the bounding box of all contours
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w < 100 and h < 100:
                continue
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x + w)
            max_y = max(max_y, y + h)
        endtime = time.time()
        print(f"Time taken to FIND_BOUNDING_BOX: {endtime - starttime:.2f} seconds")

        # Crop the image based on the bounding box
        starttime = time.time()
        cropped_img = self.img[min_y:max_y, min_x:max_x]
        endtime = time.time()
        print(f"Time taken to CROP_IMAGE: {endtime - starttime:.2f} seconds")

        # Convert the processed image to a PIL Image
        starttime = time.time()
        result_image = Image.fromarray(cropped_img)
        endtime = time.time()
        print(f"Time taken to CONVERT_TO_PIL_IMAGE: {endtime - starttime:.2f} seconds")

        # Convert the image to RGB format
        starttime = time.time()
        result_image = result_image.convert('RGB')
        endtime = time.time()
        print(f"Time taken to CONVERT_TO_RGB: {endtime - starttime:.2f} seconds")
        return result_image


# # Load the image
# # img = cv2.imread('237050.jpg')
# img = cv2.imread('imgsearch/237047.jpg')

# # Convert input image to grayscale
# grayscale_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# # remove noise
# blur = cv2.GaussianBlur(grayscale_img, (5, 5), 200)

# # resize 
# cv2.namedWindow('blur', cv2.WINDOW_NORMAL)
# # show blur image
# cv2.imshow('blur', blur)

# # Define thresholds
# threshold1 = 100
# threshold2 = 100

# # Perform Canny edge detection
# edges = cv2.Canny(blur, threshold1, threshold2)

# # RESIZE WINDOW
# cv2.namedWindow('Canny Edge Detection', cv2.WINDOW_NORMAL)
# # show canny edge detection
# cv2.imshow('Canny Edge Detection', edges)


# # Find contours in the image as groups
# contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# # Initialize variables to store minimum and maximum coordinates
# min_x, min_y = float('inf'), float('inf')
# max_x = max_y = -float('inf')

# # Find the bounding box of all contours
# for contour in contours:
#     x, y, w, h = cv2.boundingRect(contour)
#     if w < 100 and h < 100:
#         continue
#     min_x = min(min_x, x)
#     min_y = min(min_y, y)
#     max_x = max(max_x, x + w)
#     max_y = max(max_y, y + h)

# # combine all contours into the big one
# big_contour = np.concatenate(contours)

# # crop the image
# img2 = img[min_y:max_y, min_x:max_x]

# # find edges in the cropped image
# grayscale_img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
# blur2 = cv2.GaussianBlur(grayscale_img2, (5, 5), 100)
# edges2 = cv2.Canny(blur2, 10, 40)

# # Find contours draw square and draw contours
# contours2, _ = cv2.findContours(edges2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# # make it to one contour and draw only outline
# big_contour2 = np.concatenate(contours2)

# # Initialize variables to store minimum and maximum coordinates
# min_x2, min_y2 = float('inf'), float('inf')
# max_x2 = max_y2 = -float('inf')

# # Find the bounding box of all contours
# for contour in contours2:
#     x, y, w, h = cv2.boundingRect(contour)
#     min_x2 = min(min_x2, x)
#     min_y2 = min(min_y2, y)
#     max_x2 = max(max_x2, x + w)
#     max_y2 = max(max_y2, y + h)

# # Draw the bounding box on the artwork image
# cv2.rectangle(img2, (min_x2, min_y2), (max_x2, max_y2), (0, 255, 0), 3)  # Green color


# # RESIZE WINDOW
# cv2.namedWindow('Result', cv2.WINDOW_NORMAL)
# cv2.namedWindow('Original', cv2.WINDOW_NORMAL)
# # cv2.namedWindow('Canny Edge Detection2', cv2.WINDOW_NORMAL)


# #show original image
# cv2.imshow('Original', img)

# #Show the image that was cropped
# cv2.imshow('Result', img2)
# # save the image that was cropped
# cv2.imwrite('result.jpg', img2)

# #show canny edge detection
# # cv2.imshow('Canny Edge Detection2', edges2)
# cv2.waitKey(0)




