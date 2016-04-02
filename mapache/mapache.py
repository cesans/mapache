# mapache, @cesans 2016 (c)

from skimage import io, transform
from sklearn.cluster import KMeans
from sklearn.utils import shuffle

import matplotlib.pylab as plt
import numpy as np


class Party:
    """ TODO

    """

    def __init__(self, name, picture_url, short_name=None, full_name=None):
        """ TODO

        :param name:
        :param picture_url:
        :param short_name:
        :param full_name:
        :return:
        """

        self.name = name
        self._img = _get_image(picture_url)
        self.color = _get_color(self._img)
        if not short_name:
            short_name = name
        if not full_name:
            full_name = name
        self.full_name = full_name
        self.short_name = short_name[:4]

    def show(self):
        """ TODO

        :return:
        """

        print('Name: {0}'.format(self.name))
        print('Full name: {0}'.format(self.full_name))
        print('Short name: {0}'.format(self.short_name))
        plt.imshow(self._img, interpolation='nearest')
        plt.axis('off')


class PartySet:
    """ TODO

    """
    def __init__(self, context_name=''):
        """ TODO

        :param context_name:
        :return:
        """

        self.context_name = context_name
        self.parties = {}

    def __iter__(self):
        self.__current = -1
        return self

    def __getitem__(self, key):
        return self.parties[key.upper()]

    def __delitem__(self, key):
        del self.parties[key]

    def __setitem__(self, key, value):
        self.parties[key] = value

    def __next__(self):
        if self.__current == len(self.parties)-1:
            raise StopIteration
        else:
            self.__current += 1
            return self.parties[self.__current]

    def add(self, party):
        """ TODO

        :param party:
        :return:
        """
        self.parties[party.name.upper()] = party


# =================
# Useful functions
# =================
def _get_color(img):
    """ TODO

    :param img:
    :return:
    """

    w, h, d = tuple(img.shape)
    image_array = np.reshape(img, (w * h, d))
    image_array_sample = shuffle(image_array, random_state=0)[:1000]
    kmeans = KMeans(n_clusters=5, random_state=0).fit(image_array_sample)
    colors = kmeans.cluster_centers_[:, :3]
    unique, counts = np.unique(kmeans.predict(image_array), return_counts=True)
    for idx in np.argsort(counts)[::-1]:
        if any(colors[unique[idx]] < 0.9):
            color = colors[unique[idx]]
            return color

    return None


def _get_image(url):
    """ TODO

    :param url:
    :return:
    """

    img = io.imread(url)
    w, h, d = tuple(img.shape)
    img = transform.resize(img, (240, int(h/w * 240)))
    return img
