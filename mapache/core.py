# mapache, @cesans 2016 (c)

from skimage import io, transform
from sklearn.cluster import KMeans
from sklearn.utils import shuffle

import matplotlib.pylab as plt
import numpy as np

from io import BytesIO
from IPython.core.display import display, HTML

from scipy.misc import imsave
import base64

import re


class Party:
    """ A political party.

    """

    def __init__(self, name, picture_url, short_name=None, full_name=None,
                 extra_names=None, small_logo=None):
        """ A political party.

        :param name: Preferred name of the party to be used
        :param picture_url: url to the party logo, the color for the party will
                be generated from the image
        :param short_name: Name of the party displayed when there is no space
                or the preferred name is
        :param full_name: Oficial name of the party
        :param extra_names: Extra names (to help the algorithms to find the
                party in polls
        """
        self.name = name
        self._img = _get_image(picture_url)
        if not small_logo:
            small_logo = picture_url # TODO refactor picture_url
        self._small_logo = _get_image(small_logo)
            # TODO reshape in a better way
        self._small_logo =  transform.resize(self._small_logo, (40, 40))

        self.color = _get_color(self._img)

        if not short_name:
                    #If the name is not short enough an abbreviation is created:
            abbreviation = name
            if len(abbreviation) > 5:
                new_ab = ''.join([x[0] for x in abbreviation.split(" ")])
                if len(new_ab) < 2:
                    new_ab = abbreviation[:3]
                abbreviation = new_ab
            short_name = abbreviation.upper()
        if not full_name:
            full_name = name
        if not extra_names:
            extra_names = []

        self.full_name = full_name
        self.short_name = short_name[:6]
        self.extra_names = extra_names
        self.coalition = None

    def get_coalition(self):
        return self.coalition

    def add_to_coalition(self, party):
        if not self.coalition:
            self.coalition = [party]
        else:
            self.coalition.append(party)

    def show(self):
        """  Displays the information of the political party.
        """

        print('Name: {0}'.format(self.name))
        print('Full name: {0}'.format(self.full_name))
        print('Short name: {0}'.format(self.short_name))
        if self.coalition:
            print('In this coalition: ', [p.name for p in self.coalition])

        fig = plt.imshow(self._img, interpolation='none')

        plt.axis('off')
        fig.axes.get_xaxis().set_visible(False)
        fig.axes.get_yaxis().set_visible(False)


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
        del self.parties[key.upper()]

    def __setitem__(self, key, value):
        self.parties[key] = value

    def __next__(self):
        if self.__current == len(self.parties)-1:
            raise StopIteration
        else:
            self.__current += 1
            return self.parties[self.__current]

    def keys(self):
        return self.parties.keys()

    def add(self, party):
        """ TODO

        :param party:
        :return:
        """
        self.parties[party.short_name.upper()] = party

    def __get_html_img(self, img, height=80):
        buf = BytesIO()
        imsave(buf, img, format='png')
        buf.seek(0)
        img_64 = base64.b64encode(buf.read())
        return '''<img style="height:''' + str(height) + '''px   ;display: block;margin: 0 auto;"
                  src="data:image/png;base64,{0}\">
                  '''.format(img_64.decode("utf8"))

    def show_parties(self, small=False):
        html = "<div>"

        for party in self.parties.keys():
            if not small:
                html += '''<div style="margin:10px;border:1px solid gray;
                           padding: 40x; width: 400px">'''''
                html += self.__get_html_img(self.parties[party]._img)
                html += self.__get_html_img(self.parties[party]._small_logo, 20)
                html += ("<h3 style=\"text-align:center\">" +
                         self.parties[party].short_name + " - " +
                         self.parties[party].full_name + "</h3>")
                html += "</div>"

                # TODO Show logos for coalitions
            else:
                html += '''<div style="margin:3px;border:1px solid gray;
                           padding: 1px; width: 100px; display:inline-block">'''
                html += self.__get_html_img(self.parties[party]._small_logo, 40)
                html += ("<p style=\"text-align:center\">" +
                         self.parties[party].short_name + "</p>")
                html += "</div>"
        html += "</div>"
        display(HTML(html))



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
