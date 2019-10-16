from PIL import Image
from sklearn.metrics.pairwise import euclidean_distances, cosine_similarity
import numpy as np
import matplotlib as plt
from math import sqrt

import glob

images = glob.glob('/root/PycharmProjects/photography/static/*jpg')

new_image = Image.open('/root/PycharmProjects/photography/static/im.jpg')
new_image1 = new_image.resize((400, 400))
size1 = new_image1.size
img3 = np.shape(new_image1)
img4 = np.array(new_image1)
# img5 = img4.reshape(1, 1)
# img6 = img5.flatten()
print(img4)
# print(img5)

for image in images:
    with open(image, 'rb') as file:
        img = Image.open(file)
        new = img.resize((400, 400))
        size = new.size
        img0 = np.shape(new)
        img1 = np.array(new)
        # img2 = img1.reshape(1, 1)
        img7 = img1.flatten()

        # print (img)
        # print(new)
        # print(size)
        # print(img4)
        # print(img1)
# print(euclidean_distances(img6, img7))
