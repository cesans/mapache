from skimage import io, transform
from sklearn.cluster import KMeans
from sklearn.utils import shuffle

import matplotlib.pylab as plt
import numpy as np

class Party:
    def __init__(self, name, pictureURL, short_name=None, full_name=None):
        self.name = name
        self.img = self._get_image(pictureURL)
        self.color = self._get_color(self.img)
        if not short_name:
            short_name = name
        if not full_name:
            full_name = name
        self.full_name = full_name
        self.short_name = short_name[:4]


    def _get_image(self, url):
        img = io.imread(url)
        w, h, d = tuple(img.shape)
        img = transform.resize(img, (240, int(h/w * 240)))
        return img

    def _get_color(self, img):
        w, h, d = tuple(img.shape)
        image_array = np.reshape(img, (w * h, d))
        image_array_sample = shuffle(image_array, random_state=0)[:1000]
        kmeans = KMeans(n_clusters=5, random_state=0).fit(image_array_sample)
        colors = kmeans.cluster_centers_[:,:3]
        unique, counts = np.unique(kmeans.predict(image_array), return_counts=True)
        for idx in np.argsort(counts)[::-1]:
            if not (colors[unique[idx]] > 0.9).all():
                color = colors[unique[idx]]
                return color


    def show(self):
        print('Name: {0}'.format(self.name))
        print('Full name: {0}'.format(self.full_name))
        print('Short name: {0}'.format(self.short_name))
        plt.imshow(self.img, interpolation='nearest')
        plt.axis('off')
