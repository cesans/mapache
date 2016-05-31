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


class Party:
    """ A political party.

    """

    def __init__(self, name, picture_url, short_name=None, full_name=None,
                 extra_names=None):
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
        self.color = _get_color(self._img)
        self.coalition = None
    
        if not short_name:
            short_name = name
        if not full_name:
            full_name = name
        if not extra_names:
            extra_names = []

        self.full_name = full_name
        self.short_name = short_name[:4]
        self.extra_names = extra_names

    def get_coalition(self):
        return self.coalition
    
    def add_coalition_party(self, party):
    
        if not self.coalition:
            self.coalition = []
        
        self.coalition.append(party)
    
    def add_coalition_parties(self, parties):
        if not self.coalition:
            self.coalition = parties
        else:
            self.coalition += parties

    def show(self):
        """Display the information of the political party."""        
        print('Name: {0}'.format(self.name))
        print('Full name: {0}'.format(self.full_name))
        print('Short name: {0}'.format(self.short_name))

        fig = plt.imshow(self._img, interpolation='nearest')

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
        del self.parties[key]

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
        #check if exists
        self.parties[party.name.upper()] = party
    
    def remove(self, party):
        del self.parties[party.upper()]
        
    def __get_html_img(self, img):
        buf = BytesIO()
        imsave(buf, img, format='png')
        buf.seek(0)
        img_64 = base64.b64encode(buf.read())
        return '''<img style="height:80px;display: block;margin: 0 auto;"
                  src="data:image/png;base64,{0}\">
                  '''.format(img_64.decode("utf8"))

    def show_parties(self):
        html = ""
        for party in self.parties.keys():
            html += '''<div style="margin:10px;border:1px solid gray;
                       padding: 20px">'''
            html += self.__get_html_img(self.parties[party]._img)
            html += ("<h3 style=\"text-align:center\">" + party + " - " +
                     self.parties[party].full_name + "</h3>")
            coalition = self.parties[party].get_coalition()
            if coalition:
                html += '<p style=\"text-align:center\"> *Including: '
                for c in coalition:
                    html += c.name + ', '
                html = html[:-2]
                html += '</p>'
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
