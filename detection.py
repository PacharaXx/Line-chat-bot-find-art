import cv2
import numpy as np

class ImgArgumentation:
    def __init__(self):
        self.img = None

    def set_img(self, img):
        self.img = img

    def blur(self):
        blur = cv2.GaussianBlur(self.img, (5, 5), 100)
        return blur
    
    def canny(self):
        edges = cv2.Canny(self.img, 10, 40)
        return edges
    
    def find_contours(self):
        contours, _ = cv2.findContours(self.img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return contours
    
    def find_biggest_contour(self):
        biggest_contour = max(self.find_contours(), key=cv2.contourArea)
        return biggest_contour
    
    def find_bounding_box(self):
        x, y, w, h = cv2.boundingRect(self.find_biggest_contour())
        return x, y, w, h
    
    def crop(self):
        x, y, w, h = self.find_bounding_box()
        crop_img = self.img[y:y+h, x:x+w]
        return crop_img
    
    def resize(self, width, height):
        resize_img = cv2.resize(self.img, (width, height))
        return resize_img
    
    def show(self, window_name):
        cv2.imshow(window_name, self.img)
        cv2.waitKey(0)
    
    # return the image that was cropped
    def get_result(self):
        return self.crop()
    
    def run(self):
        self.set_img(self.img)
        self.img = self.blur()
        self.img = self.canny()
        self.img = self.find_contours()
        self.img = self.find_biggest_contour()
        self.img = self.find_bounding_box()
        self.img = self.crop()
        self.img = self.resize(300, 300)
        self.show('Result')
        return self.get_result()


# # Load the image
# # img = cv2.imread('237050.jpg')
# img = cv2.imread('236915.jpg')

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




