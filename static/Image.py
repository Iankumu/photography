from PIL import Image
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances
img = Image.open('img/box.png')
img1 = Image.open('img/home.jpg')

img_array = np.array(img)
#img_array.reshape(100000,2)
img_array1 = np.array(img1)
print(img_array.shape)
print(img_array1.shape)

#print(euclidean_distances(img_array,img_array1))

