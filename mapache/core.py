"""Core features of mapache."""

# -*- coding: utf-8 -*-

import numpy as np

import matplotlib.pylab as plt
import matplotlib

from sklearn.cluster import KMeans
from sklearn.utils import shuffle

from PIL import Image
import base64
from io import BytesIO
import urllib.request

import warnings


class Party:
    """Implements a political party."""

    def __init__(self, name, logo_url, short_name=None, full_name=None,
                 extra_names=None, thumbnail_url=None):
        """Create political party.

        Args:
            name (str): Name of the party. The preferred name to be used,
                        although other names can be provided. If ``short_name``
                        is not indicated, ``name`` will be used to crate an
                        abbreviation.
            picture_url (Optional[str]): url to the party logo, the color for
                        the party will be generated from the image.
            short_name (Optional[List[str]]): Abbreviation of the party name to
                        be displayed when there is no space for ``name``.
                        Maximum of 7 characters.
            full_name (Optional[str]): Official, full name of the part
            extra_names (Optional[List[str]]): Any number of extra names of the
                        party to help matching the party to polls (eg. names
                        in different languages).
        """
        self.name = name
        self.set_logo(logo_url)
        self.set_thumbnail(thumbnail_url)

        length_abreviation = 7

        if not short_name:
            short_name = self._create_abbreviation(name, length_abreviation)
        if not full_name:
            full_name = name
        if not extra_names:
            extra_names = []

        self.full_name = full_name
        self.short_name = short_name[:length_abreviation]
        self.extra_names = extra_names
        self.coalition = None

    def __str__(self):
        """Text for ``print()``.

        Returns:
                str: Party information
        """
        toprint = ''
        toprint += 'Name: {0}\n'.format(self.name)
        toprint += 'Full name: {0}\n'.format(self.full_name)
        toprint += 'Short name: {0}\n'.format(self.short_name)
        if self.coalition:
            toprint += 'In this coalition: '
            toprint += ','.join(map(str, self.coalition))
        toprint += '\n'
        return(toprint)

    def set_logo(self, url):
        """Set the logo and updates the party color.

        The image is download from ``url`` and the color of the party
        ``self.color`` is updated to the principal color of the image

        Args:
            url (str): url to a image with the logo of the party
        """
        self._logo = self._get_image(url)
        self.color = self._get_color(self._logo)

    def get_logo(self, url):
        """Current logo of the party.

        Returns:
            PIL.Image: Current logo of the party
        """
        return self._logo

    def set_thumbnail(self, url=None):
        """Set the thumbnail of the party.

        The size of the thumbnail will be 80x80 and squared images are
        preferred. If no url is provided the logo of the party will be used
        as the thumbnail.

        Args:
            url (Optional[str]): url to a image with the small logo
                                 of the party
        """
        if not url:
            if self._logo:
                self._thumbnail = self._logo.copy()
        else:
            self._thumbnail = self._get_image(url)

        w, h = self._thumbnail.size

        self._thumbnail.thumbnail((80, 80), Image.ANTIALIAS)

    def get_thumbnail(self, url):
        """Current thumbnail of the party.

        Returns:
            PIL.Image: Current thumbnail of the party
        """
        return self._thumbnail

    def add_to_coalition(self, party):
        """Consider this party a coalition and add a party to it.

        When the first party is added this party becomes a coalition. The
        parties in the coalition will be used to match the party with polls
        if the opposite is not specified.

        Args:
            party (mapache.Party): party to be added to the coalition
        """
        if not self.coalition:
            self.coalition = [party]
        else:
            self.coalition.append(party)

    def get_coalition(self):
        """Return parties being part of the coalition."""
        return self.coalition

    def get_all_names(self):
        """All names of the party.

        Returns:
            (list): all the names of the party (long, short, extra...)
        """
        return set((self.extra_names + [self.full_name] +
                   [self.name] + [self.short_name]))

    def match(self, party_name):
        """Evaluate how well a name matches this party.

        mapache.core._levenshtein_distance is used for the comparison.
        All names of the party are used in the comparison.

        Args:
            party_name (str): name to be evaluated
        """
        max_ratio = 0
        for name in self.get_all_names():
            max_ratio = max(max_ratio,
                            self._levenshtein_distance(name,
                                                       party_name)['ratio'])
        return(max_ratio)

    def show(self):
        """Show the information of the party.

        Displays the names, parties in the coalition and the logo of the party.
        The logo is displayed as a matplotlib image.
        """
        print(self)

        fig = plt.imshow(np.array(self._logo))

        plt.axis('off')
        fig.axes.get_xaxis().set_visible(False)
        fig.axes.get_yaxis().set_visible(False)

    def show_color(self):
        """Show the color selected for the party_name.

        A patch with the color of the party and its abreviation in white
        is displayed using matplotlib.
        """
        plt.rcParams['figure.figsize'] = (3, 3)

        fig, ax = plt.subplots()
        ax.set_aspect('equal', 'datalim')

        r = matplotlib.patches.Rectangle((0, 0), 1, 1, color=self.color)
        ax.add_patch(r)
        ax.text(0.5, 0.5, self.short_name,
                fontdict={'weight': 'bold', 'color': 'w', 'fontsize': '30',
                          'ha': 'center', 'va': 'center'})

        ax.axis('off')

    def _get_color(self, img, pixels_to_sample=1000, nclusters=5):
        """Select the principal color of an image.

        A number of pixels is randomly sampled and used to cluster the colors
        in the image. Then each pixel of the image is assigned to a cluster to
        find the main color of the image.
        The most frequent color is preferred and whites (all RGB values > 0.9)
        are discarded.

        Args:
            img (PIL.image): logo of the party
            pixels_to_sample (Optional[int[)): number of pixels to sample
            nclusters (Optional[int]): number of colors(clusters) to consider
        Returns:
            (List[float]): RGB (0 to 1) list with the main color of the party
                           or None if the selection fails (eg. because it is
                           white)
        """
        img = np.array(img, dtype=np.uint8) / 255.
        w, h, d = tuple(img.shape)
        image_array = np.reshape(img, (w * h, d))
        if d == 4:
            image_array = image_array[image_array[:, -1] == 1]

        # pixels_to_sample pixels are randomly extracted from the image
        image_array_sample = shuffle(image_array,
                                     random_state=0)[:pixels_to_sample]

        # the pixels are clustered in n_clusters
        kmeans = KMeans(n_clusters=nclusters,
                        random_state=0).fit(image_array_sample)
        colors = kmeans.cluster_centers_[:, :3]

        # all the pixels in the image are assigned to a cluster and the cluster
        # with more pixels is selected as sthe main color of the image
        # white colors (all RGB values > 0.9) are discarded
        unique, counts = np.unique(kmeans.predict(image_array),
                                   return_counts=True)
        for idx in np.argsort(counts)[::-1]:
            if any(colors[unique[idx]] < 0.9):
                color = colors[unique[idx]]
                return color

        return None

    def _get_image(self, url):
        """Download an image.

        The image is downloaded and resized to a width of 240

        TODO: set maximum height as well

        Args:
            url (str): url of the image

        Returns:
            PIL.Image: image
        """
        img = Image.open(urllib.request.urlopen(url))
        w, h = img.size
        img = img.resize((240, int(h / w * 240)), Image.ANTIALIAS)
        return img

    def _create_abbreviation(self, name, max_characters=7):
        """Create an abbreviation (short_name) from a longer name.

        If the name is longer than max_characters:
            - Take the first letter of each word in the name
            If only one or two words:
                - Take the first 3 laters of the first word

            Transform to upper case.
        TODO: smarter algorithm to generate the abbreviation?

        Args:
            name (str): name of the party, probably too long
        Results:
            (name): abbreviation limited to ``max_characters`` chars

        """
        abbreviation = name
        
        if len(abbreviation) > max_characters:
            new_ab = ''.join([x[0] for x in abbreviation.split(" ")])
            if len(new_ab) <= 2:
                new_ab = abbreviation[:3]
            abbreviation = new_ab
            abbreviation = abbreviation.upper()
        return abbreviation

    def _levenshtein_distance(self, str1, str2):
        """Compute the levenshtein distance between two strings.

        The Levenshtein distance between two strings is the minmium number
        of char additions, deletions or sustitutions to get from the first
        string to the second one.

        Adapted from:
                https://rosettacode.org/wiki/Levenshtein_distance#Iterative

        Args:
            str1 (str): first string
            str2 (str): second string

        Returns:
            Dict: 'distance': the Levenshtein distance
                  'ratio': (len(str1)+len(str1)-distance)/(len(str1)+len(str1))
        """
        if not (str1 and str2):
            return {'distance': 0, 'ratio': 0}
        str1, str2 = str1.upper(), str2.upper()
        m = len(str1)
        n = len(str2)
        lensum = float(m + n)
        d = []
        for i in range(m + 1):
            d.append([i])
        del d[0][0]
        for j in range(n + 1):
            d[0].append(j)
        for j in range(1, n + 1):
            for i in range(1, m + 1):
                if str1[i - 1] == str2[j - 1]:
                    d[i].insert(j, d[i - 1][j - 1])
                else:
                    minimum = min(d[i - 1][j] + 1, d[i]
                                  [j - 1] + 1, d[i - 1][j - 1] + 2)
                    d[i].insert(j, minimum)
        ldist = d[-1][-1]
        ratio = (lensum - ldist) / lensum
        return {'distance': ldist, 'ratio': ratio}


class PartySet:
    """A group of parties with added funcionality.

    A group of parties with name matching capabilities (ie. return the party
    with the closest name if similar enough) and some visualization tools.
    """

    def __init__(self, context_name=''):
        """Create a PartySet.

        Args:
            context_name (str): Name of the group of parties
                                (eg.: 2016 Spanish General Elections)
        """
        self.context_name = context_name
        self.parties = {}

    def __iter__(self):
        self.__current = -1
        return self

    def extract(self, parties):
        """Create a new PartySet with a subset of the current parties.
        
        Args:
            parties (list [str]): name of the parties to extract, name matching
                                  will be used to find the correct parties

        Returns:
            PartySet: new group of parties containing those in ``parties``
        """
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
        """``__getitem__`` with name matching."""
        if key.upper() in self.parties:
            return self.parties[key.upper()]
        matched = self.match(key)
        if matched:
            warnings.warn('Party was not found, returning closest match')
            return matched
        return self.parties[key.upper()]

    def __delitem__(self, key):
        """TODO: add name matching."""
        del self.parties[key.upper()]

    def __setitem__(self, key, value):
        """TODO: add name matching."""
        self.parties[key] = value

    def __next__(self):
        """``__next__``."""
        if self.__current == len(self.parties) - 1:
            raise StopIteration
        else:
            self.__current += 1
            return self.parties[self.__current]

    def keys(self):
        return self.parties.keys()

    def add(self, party):
        self.parties[party.short_name.upper()] = party

    def _get_html_img(self, img, height=80, inline=False):
        buf = BytesIO()
        img.save(buf, format='png')
        buf.seek(0)
        img_64 = base64.b64encode(buf.read())
        display = 'block'
        if inline:
            display = 'inline-block'
        return ('''<img style="height:''' + str(height) +
                '''px ;display: {0};margin: 0 auto;"
                    src="data:image/png;base64,{1}\">
                '''.format(display, img_64.decode("utf8")))

    def show_parties(self, small=False):
        html = "<div>"
        for party in self.parties.keys():
            if not small:
                html += """<div style="margin:10px;border:1px solid #AAAAAA;
                            width: 400px; width: 50%; margin: 5px auto;
                            display:inline-block;">"""
                html += """<div style="display:inline-block; margin: 10px">"""
                html += self._get_html_img(self.parties[party]._thumbnail, 20,
                                           inline=True)
                fname = self.parties[party].full_name
                if len(fname) > 45:
                    fname = fname[:41] + '...'
                html += ("""<h3 style=\"display: inline-block;
                            margin-top:5px\";>""" +
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
                html += self._get_html_img(self.parties[party]._thumbnail, 40)
                html += ("<p style=\"text-align:center\">" +
                         self.parties[party].short_name + "</p>")
                html += "</div>"
        html += "</div>"
        return html

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

    def __init__(self,  parties, date, pollster='', error=None):

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

    def __str__(self):
        toprint = ''
        toprint += 'Pollster: {0}\n'.format(self.pollster)
        toprint += 'Date: {0}\n'.format(self.date)
        if self.error:
            toprint += 'Error: {0}% \n'.format(self.error)
        toprint += '-' * 20 + '\n'
        for name, votes in self.parties.items():
            toprint += '{0}: {1:.2f}%\n'.format(name, votes)

        return toprint


class PollsList:

    def __init__(self, name=''):
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
