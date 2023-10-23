from math import sqrt
import random
import matplotlib.pyplot as plt
try:
    from PIL import Image
except ImportError:
    import Image

class Point:
    def __init__(self, coords, n, ct):
        self.coords = coords
        self.n = n
        self.ct = ct

class ColorQuantizer:
    def __init__(self, filename, thumbnail_size=(200, 200), min_diff=1):
        self.filename = filename
        self.thumbnail_size = thumbnail_size
        self.min_diff = min_diff
        self.img = self.load_image()

    def load_image(self):
        try:
            img = Image.open(self.filename)
            img.thumbnail(self.thumbnail_size)
            return img
        except (IOError, Image.DecompressionBombError):
            raise ValueError("Error loading image")
    
    def get_points(self):
        points = []
        w, h = self.img.size
        for count, color in self.img.getcolors(w * h):
            points.append(Point(color, 3, count))
        return points

    def rtoh(self, rgb):
        return '#%s' % ''.join(('%02x' % p for p in rgb))

    def euclidean(self, p1, p2):
        return sqrt(sum([(p1.coords[i] - p2.coords[i]) ** 2 for i in range(p1.n)]))

    def calculate_center(self, points, n):
        vals = [0.0 for i in range(n)]
        plen = 0
        for p in points:
            plen += p.ct
            for i in range(n):
                vals[i] += (p.coords[i] * p.ct)
        return Point([(v / plen) for v in vals], n, 1)

    def kmeans(self, points, k, min_diff):
        random.seed(0)
        clusters = [random.choice(points) for _ in range(k)]

        while 1:
            plists = [[] for _ in range(k)]

            for p in points:
                smallest_distance = float('Inf')
                for i, cluster in enumerate(clusters):
                    distance = self.euclidean(p, cluster)
                    if distance < smallest_distance:
                        smallest_distance = distance
                        idx = i
                plists[idx].append(p)

            diff = 0
            for i in range(k):
                old_center = clusters[i]
                new_center = self.calculate_center(plists[i], old_center.n)
                clusters[i] = new_center
                diff = max(diff, self.euclidean(old_center, new_center))

            if diff < min_diff:
                break

        return clusters

    def get_color_name(self, rgb):
        # A predefined dictionary that maps common RGB values to color names
        color_names = {
            (255, 0, 0): "Red",
            (0, 255, 0): "Green",
            (0, 0, 255): "Blue",
            (255, 255, 0): "Yellow",
            (0, 255, 255): "Cyan",
            (255, 0, 255): "Magenta",
            (0, 0, 0): "Black",
        }
        
        # Find the closest match for the given RGB color in the dictionary
        closest_match = min(color_names.keys(), key=lambda x: sum(
            (a - b) ** 2 for a, b in zip(x, rgb)))

        # Return the color name corresponding to the closest match
        return color_names.get(closest_match, "Unknown")

    def quantize(self, n):
        points = self.get_points()
        clusters = self.kmeans(points, n, self.min_diff)
        rgbs = [list(map(int, c.coords)) for c in clusters]

        color_descriptions = []
        for rgb in rgbs:
            hex_color = self.rtoh(rgb)
            color_name = self.get_color_name(rgb)
            color_description = f"{color_name} ({hex_color})"
            color_descriptions.append(color_description)

        return color_descriptions
    
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

# Example usage:
if __name__ == "__main__":
    filename = "imgsearch/target.jpg"  # Provide the path to your image file
    quantizer = ColorQuantizer(filename)
    result = quantizer.quantize(5)
    quantizer.visualize_palette()
    print(result)
