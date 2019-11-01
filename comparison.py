import glob
import numpy as np
from PIL import Image
from sklearn.metrics.pairwise import euclidean_distances

images = glob.glob('C:/Users/User/Documents/Strathmore/ICS/Academic Work/Year 2/Semester 2/IS Project/photography/static**/*jpg', recursive=True)


def image_comparison(img):
    # test image
    resized_image = Image.open(img).resize((400, 400))
    size1 = resized_image.size
    img3 = np.shape(resized_image)
    img4 = np.array(resized_image)
    img6 = img4.flatten()
    all_images = []
    new_list = []
    for image in images:
        with open(image, 'rb') as file:
            img = Image.open(file)
            new = img.resize((400, 400))
            size = new.size
            np.shape(new)
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
    return sort
