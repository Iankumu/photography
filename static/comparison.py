import glob
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances

from app import *

# def comparison(img):
images = glob.glob('/root/PycharmProjects/photography/static/**/*jpg', recursive=True)
# test image

new_image = Image.open('/root/PycharmProjects/photography/static/im.jpg')
new_image1 = new_image.resize((400, 400))
size1 = new_image1.size
img3 = np.shape(new_image1)
img4 = np.array(new_image1)
img6 = img4.flatten()
difference = []
all_images = []
new_list = []
joined = []
full_list = []
photoid = []
for image in images:
    with open(image, 'rb') as file:
        img = Image.open(file)

        new = img.resize((400, 400))
        size = new.size
        img0 = np.shape(new)
        img1 = np.array(new)
        img7 = img1.flatten()
        difference = euclidean_distances([img6], [img7])

        for i in difference:
            new_difference = (i[0])
            new_list.append(new_difference)

all_images.append(images)
var = all_images[0]
joined = dict(zip(var, new_list))
sort = sorted(joined.items(), key=lambda x: x[1])
# print(sort)
if sort:
    for i in sort:
        full_list = i
        filename = os.path.basename(full_list[0])
        print(filename)

    ''' cur = app.app_context(mysql.connect.cursor())
        result = cur.execute('SELECT photographerid FROM photos WHERE photo = %s', filename)
        app.app_context(mysql.connect.commit())
        cur.close()
        print(result)'''

# comparison()
