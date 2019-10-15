from PIL import Image
from sklearn.metrics import euclidean_distances

import glob

images = glob.glob('/root/PycharmProjects/photography/static/*jpg')

for image in images:
    for image in images:
        with open(image, 'rb') as file:
            img = Image.open(file)
            new = img.resize((500, 500))
            # size = width , height = img.size
            # print (img)
            print(new)
            # print (img.size[1])
