# mapache, @cesans 2016 (c)

from skimage import io, transform
from sklearn.cluster import KMeans
from sklearn.utils import shuffle

import matplotlib.pylab as plt
from matplotlib.patches import Rectangle
import numpy as np

from io import BytesIO
from IPython.core.display import display, HTML

from scipy.misc import imsave
import base64

import warnings


class Party:
    """ A political party.

    """

    def __init__(self, name, logo_url, short_name=None, full_name=None,
                 extra_names=None, small_logo_url=None):
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
        self.set_logo(logo_url)
        self.set_small_logo(small_logo_url)

        self.color = self._get_color(self._logo)

        if not short_name:
            # If the name is not short enough an abbreviation is created:
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
        self.short_name = short_name[:7]
        self.extra_names = extra_names
        self.coalition = None

    def set_logo(self, url):
        self._logo = self._get_image(url)

    def set_small_logo(self, url):
        if not url:
            self._small_logo = self._logo
        else:
            self._small_logo = self._get_image(url)
        
        # TODO reshape in a better way
        self._small_logo = transform.resize(self._small_logo, (40, 40))

        
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

        fig = plt.imshow(self._logo, interpolation='none')

        plt.axis('off')
        fig.axes.get_xaxis().set_visible(False)
        fig.axes.get_yaxis().set_visible(False)

    def _get_color(self, img):
        """ TODO

        :param img:
        :return:
        """

        w, h, d = tuple(img.shape)
        image_array = np.reshape(img, (w * h, d))
        if d==4:
            image_array = image_array[image_array[:,-1] == 1]
        image_array_sample = shuffle(image_array, random_state=0)[:1000]
        kmeans = KMeans(n_clusters=5, random_state=0).fit(image_array_sample)
        colors = kmeans.cluster_centers_[:, :3]
        unique, counts = np.unique(kmeans.predict(image_array),
                                   return_counts=True)
        for idx in np.argsort(counts)[::-1]:
            if any(colors[unique[idx]] < 0.9):
                color = colors[unique[idx]]
                return color

        return None

    def _get_image(self, url):
        """ TODO

        :param url:
        :return:
        """

        img = io.imread(url)
        w, h, d = tuple(img.shape)
        img = transform.resize(img, (240, int(h/w * 240)))
        return img

    def levenshtein_distance(self, str1, str2):
    
        if not (str1 and str2):
            return {'distance': 0, 'ratio': 0}
        str1, str2 = str1.upper(), str2.upper()
        m = len(str1)
        n = len(str2)
        lensum = float(m + n)
        d = []
        for i in range(m+1):
            d.append([i])
        del d[0][0]
        for j in range(n+1):
            d[0].append(j)
        for j in range(1, n+1):
            for i in range(1, m+1):
                if str1[i-1] == str2[j-1]:
                    d[i].insert(j, d[i-1][j-1])
                else:
                    minimum = min(d[i-1][j]+1, d[i][j-1]+1, d[i-1][j-1]+2)
                    d[i].insert(j, minimum)
        ldist = d[-1][-1]
        ratio = (lensum - ldist)/lensum
        return {'distance': ldist, 'ratio': ratio}

    def get_all_names(self):
        return (self.extra_names + [self.full_name] +
                [self.name] + [self.short_name])

    def match(self, party_name):
        max_ratio = 0
        for name in (self.extra_names + [self.full_name] +
                     [self.name] + [self.short_name]):
            max_ratio = max(max_ratio,
                            self.levenshtein_distance(name,
                                                      party_name)['ratio'])
        return(max_ratio)

    def show_color(self):
        plt.rcParams['figure.figsize'] = (3,3)

        fig, ax = plt.subplots()
        ax.set_aspect('equal', 'datalim')

        r = Rectangle((0,0),1,1, color=self.color)
        ax.add_patch(r)
        ax.text(0.5, 0.5, self.short_name, fontdict={'weight':'bold', 'color':'w', 'fontsize':'30', 'ha':'center', 'va':'center'})

        ax.axis('off')
        

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

    def extract(self, parties):         
        new_list = type(self)()
        new_list.__dict__.update(self.__dict__)
        
        new_list.parties = {}      
        for party in parties:
            p = self.match(party)
            if not p:
                raise Exception
                # TODO exception!
            new_list.add(p)
        return new_list
        
    def __getitem__(self, key):
        if key.upper() in self.parties:
            return self.parties[key.upper()]
        matched = self.match(key)
        if matched:
            warnings.warn('Party was not found, returning closest match')
            return matched
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
        

    def _get_html_img(self, img, height=80, inline=False):
        buf = BytesIO()
        imsave(buf, img, format='png')
        buf.seek(0)
        img_64 = base64.b64encode(buf.read())
        display = 'block'
        if inline:
            display = 'inline-block'
        return ('''<img style="height:''' + str(height) +
                '''px ;display: {0};margin: 0 auto;"
                    src="data:image/png;base64,{1}\">
                '''.format(display,img_64.decode("utf8")))
    def show_parties(self, small=False):
        html = "<div>"
        for party in self.parties.keys():
            if not small:
                html += '''<div style="margin:10px;border:1px solid #AAAAAA;
                            width: 400px; width: 50%; margin: 5px auto; 
                            display:inline-block;">'''
                html += '''<div style="display:inline-block; margin: 10px">'''
                html += self._get_html_img(self.parties[party]._small_logo, 20, inline=True)
                fname = self.parties[party].full_name
                if len(fname) > 45:
                    fname = fname[:41] + '...'
                html += ("<h3 style=\"display: inline-block; margin-top:5px\";>" +
                         self.parties[party].short_name + " - " +
                         fname + "</h3>")
                html += "</div>"                            
                html += '''<div style="margin: 10px auto">'''
                html += self._get_html_img(self.parties[party]._logo)
                html += "</div>"                            
                html += "</div>"

                # TODO Show logos for coalitions
            else:
                html += '''<div style="margin:3px;border:1px solid gray;
                           padding:1px; width:100px; display:inline-block">'''
                html += self._get_html_img(self.parties[party]._small_logo, 40)
                html += ("<p style=\"text-align:center\">" +
                         self.parties[party].short_name + "</p>")
                html += "</div>"
        html += "</div>"
        display(HTML(html))

    def match(self, party_name, min_ratio=0.8):
        max_party = None
        max_ratio = 0
        
        for party in self.parties.values():
            ratio = party.match(party_name)
            if ratio > max_ratio:
                max_ratio = ratio
                max_party = party
        if max_ratio < min_ratio:
            max_party = None
        return max_party


class Poll:
    """ TODO

    """
    def __init__(self,  parties, date, pollster='', error=None):
        """ TODO

        :param name:
        :return:
        """

        self.pollster = pollster
        self.date = date
        self.parties = parties
        self.error = error
        # TODO check types

    def get_party(self, party, min_ratio=0.8, join_coalitions=True,
                  return_partial=False):
                  
        # If return_partial return coalition votes even if not all parties 
        # are in the poll
        if party.name in self.parties:            
            return self.parties[party.name]

        for p in self.parties:
            ratio = party.match(p)
            if ratio > min_ratio:
                return self.parties[p]

        # This should be tested... unit tests are my friends?
        if join_coalitions and party.coalition:
            votes = 0
            for party_coal in party.coalition:                
                if party_coal.name in self.parties:
                    votes += self.parties[party_coal.name]
                else:
                    for p in self.parties:                        
                        ratio = party_coal.match(p)     
                        if ratio > min_ratio:                      
                            votes += self.parties[p]
                            break                                
                if not votes and not return_partial:
                    return None
            return votes

        return None

    def print(self):
        print('Pollster: {0}'.format(self.pollster))
        print('Date: {0}'.format(self.date))
        if self.error:
            print('Error: {0}%  '.format(self.error))
        print('-'*20)
        for name, votes in self.parties.items():
            print('{0}: {1:.2f}%'.format(name, votes))


class PollsList:
    """ TODO

    """
    def __init__(self, name=''):
        """ TODO

        :param name:
        :return:
        """
        self._name = name
        self.polls = []

    def add(self, poll):
        if isinstance(poll, PollsList):
            for p in poll.polls:
                self.polls.append(p)
        else:
            self.polls.append(poll)
        # TODO check types

    def get_party(self, party, join_coalitions=True):
        party_polls = []

        for poll in self.polls:
            poll_party = poll.get_party(party, join_coalitions=join_coalitions)
            if poll_party:
                party_polls.append((poll.date, poll_party))

        return party_polls
