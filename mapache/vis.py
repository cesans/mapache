# mapache, @cesans 2016 (c)

import matplotlib.pylab as plt
import matplotlib
import numpy as np
from matplotlib.ticker import FuncFormatter
from matplotlib import gridspec
from sklearn import gaussian_process


class PollVis:
    """ TODO
    """

    def __init__(self, parties):
        """ TODO

        :param parties:
        :return:
        """
        self.parties = parties
        self.columns = []
        self.__up_to_date = False
        self.__fig = None

    def add_column(self, polls, main=False):
        """ TODO

        :param polls:
        :param main:
        :return:
        """
        self.__fig = None

        self.columns.append({'polls': polls, 'main': main})

    def show(self):
        """ TODO
        :return:
        """

        if self.__fig is None:
            self.__create_fig()
        plt.show()

    def export(self, filename):
        """ TODO
        :param filename:
        :return:
        """
        # TODO
        if self.__fig is None:
            self.__create_fig()

        print(filename)

        pass

    def __create_fig(self):
        """ TODO
        :return:
        """
        self.__fig = plt.figure()

        if not self.columns:
            print('No columns have been added')
            return

        range_lengths = [c['polls']['dates'][-1] - c['polls']['dates'][0] for c in self.columns]
        range_lengths_nonzero = [r for r in range_lengths if r != 0]
        total_length = (sum(range_lengths) / (1 - (len(self.columns) - len(range_lengths_nonzero)) * 0.1))
        range_lengths = [r / total_length if r != 0 else 0.1 for r in range_lengths]

        gs = gridspec.GridSpec(1, len(self.columns), width_ratios=range_lengths)

        for i, c in enumerate(self.columns):
            ax = plt.subplot(gs[i])
            first = False
            last = False
            if i == 0:
                first = True
            if i == len(self.columns) - 1:
                last = True
            self.__draw_column(c['polls'], ax, first, last)

        max_percentage = 0
        for i, c in enumerate(self.columns):
            for name, percentages in c['polls']['parties'].items():
                max_percentage = max(max_percentage, percentages.max())
        yticks = [tick for tick in [10, 20, 30, 40, 50, 60, 70, 80, 90] if tick < max_percentage]
        for g in gs:
            ax = plt.subplot(g)
            ax.set_yticks(yticks, minor=False)
            ax.set_ylim(0, min(max_percentage + 5, 100))

    def __draw_column(self, polls, ax, first=False, last=False):
        """ TODO

        :param polls:
        :param first:
        :param last:
        :return:
        """

        self.__fig = None

        single = len(polls['dates']) == 1

        title_loc = 'left'
        if single:
            title_loc = 'center'

        ax.set_title(polls['title'], loc=title_loc)

        for name, percentages in polls['parties'].items():
            self.__scatter(polls['dates'], percentages, ax, name, single)
            if not single:
                self.__gp(polls['dates'], percentages, ax, name)
            if last:
                plt.text(polls['dates'][-1] + 0.2, percentages[-1], self.parties[name].short_name,
                         color=self.parties[name].color, weight='bold', verticalalignment='center')

        ax.set_yticks([10, 20, 30, 40, 50, 60, 70, 80, 90], minor=False)
        ax.yaxis.grid(True, which='major')
        ax.yaxis.grid(True, which='minor')
        ax.spines['top'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(True)
        ax.spines['left'].set_visible(False)
        ax.yaxis.set_ticks_position('none')
        ax.xaxis.set_ticks_position('bottom')
        formatter = FuncFormatter(self.__percentage_formatter)
        ax.get_yaxis().set_major_formatter(formatter)

        ax.set_xlim(polls['dates'][0] - 0.5, polls['dates'][-1] + 0.5)

        if not first:
            ax.set_yticklabels([])

        if single:
            ax.set_xticks(polls['dates'].reshape(1), minor=False)

    def __scatter(self, x, y, ax, partyname, single=False):
        """ TODO
        :param single:
        :return:
        """

        if single:
            ax.scatter(x, y, 70, c=self.parties[partyname].color, edgecolors='none', label=u'Observations')
        else:
            ax.scatter(x, y, c=np.append(self.parties[partyname].color, 0.6), edgecolors='none', s=40,
                       label=u'Observations')

    def __gp(self, x, y, ax, partyname):
        """ TODO

        :param x:
        :param ax:
        :param partyname:
        :return:
        """

        x_dense = np.atleast_2d(np.linspace(x[0] - 0.5, x[-1] + 0.5, 1000)).T

        np.random.seed(1)
        gp = gaussian_process.GaussianProcess(corr='squared_exponential', theta0=1e-1,
                                              thetaL=1e-3, thetaU=1,
                                              random_start=100, nugget=10 - 8)
        gp.fit(x, y)
        y_pred, mse = gp.predict(x_dense, eval_MSE=True)
        sigma = np.sqrt(mse)

        ax.plot(x_dense, y_pred, 'b-', label=u'Prediction', c=self.parties[partyname].color)
        ax.fill(np.concatenate([x_dense, x_dense[::-1]]),
                np.concatenate([y_pred - 1.9600 * sigma,
                                (y_pred + 1.9600 * sigma)[::-1]]),
                scolor=np.append(self.parties[partyname].color, 0.1), fc='b', ec='None',
                label='95% confidence interval')

    def __percentage_formatter(self, y, position):
        """ TODO
        :param y:
        :param position:
        :return:
        """

        # Ignore the passed in position. This has the effect of scaling the default
        # tick locations.
        s = str(y)

        # The percent symbol needs escaping in latex
        if matplotlib.rcParams['text.usetex'] is True:
            return s + r'$\%$'
        else:
            return s + '%'
