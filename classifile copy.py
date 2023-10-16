import cv2
import numpy as np


def get_color_name(color):
    """Maps an RGB color to a basic color name."""
    # Define color ranges for basic colors.
    color_ranges = {
        'red': ((0, 0, 128), (0, 0, 255)),
        'orange': ((0, 128, 128), (0, 165, 255)),
        'yellow': ((0, 128, 0), (255, 255, 0)),
        'green': ((0, 128, 0), (0, 255, 0)),
        'cyan': ((128, 128, 0), (255, 255, 0)),
        'blue': ((128, 0, 0), (255, 0, 0)),
        'purple': ((128, 0, 128), (255, 0, 255)),
        'pink': ((128, 0, 128), (255, 0, 255)),
        'black': ((0, 0, 0), (0, 0, 0)),
        'white': ((255, 255, 255), (255, 255, 255)),
        'gray': ((128, 128, 128), (128, 128, 128))
    }
    
    # Check which color range the input color falls into.
    for name, (lower, upper) in color_ranges.items():
        lower = np.array(lower, dtype=np.uint8)
        upper = np.array(upper, dtype=np.uint8)
        if np.all(np.greater_equal(color, lower)) and np.all(np.less_equal(color, upper)):
            return name
    
    return 'other'

def get_main_color(image_path):
    """Gets the main color in an image using Python.

    Args:
        image_path: The path to the image file.

    Returns:
        The main color in the image, as a tuple of (R, G, B) values.
    """

    # Load the image.
    img = cv2.imread(image_path)

    if img is None:
        raise ValueError("Failed to load the image.")

    # Preprocess the image.
    img = cv2.resize(img, (256, 256))

    # Reshape the image.
    img = img.reshape((-1, 3))  # Reshape to a 2D array with 3 channels

    # Convert the data type to float32 for K-means clustering.
    img = np.float32(img)

    # Apply K-means clustering.
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    K = 1  # Number of clusters
    attempts = 10
    _, labels, centers = cv2.kmeans(img, K, None, criteria, attempts, cv2.KMEANS_RANDOM_CENTERS)

    # Get the dominant color.
    dominant_color = centers[0]

    # Convert the dominant color to RGB.
    dominant_color = np.uint8(dominant_color)

    return tuple(dominant_color)

# Get the main color in the image.
dominant_color = get_main_color("./imgsearch/i - 1150.jpeg")

# Create a blank image filled with the dominant color.
color_image = np.zeros((100, 100, 3), dtype=np.uint8)
color_image[:] = dominant_color

# Display the dominant color image.
cv2.imshow("Dominant Color", color_image)

# Get the color name.
color_name = get_color_name(dominant_color)

# Display the color name.
print(color_name)


# Wait for a key press and close the OpenCV window.
cv2.waitKey(0)
cv2.destroyAllWindows()
