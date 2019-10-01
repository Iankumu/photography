from PIL import Image
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances
img = Image.open('img/box.png')
img1 = Image.open('img/home.jpg')

img_array = np.array(img)
img_array1 = np.array(img1)
print(img_array.shape)
print(img_array1.shape)


