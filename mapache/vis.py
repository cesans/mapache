# mapache, @cesans 2016 (c)

import matplotlib.pylab as plt
import matplotlib
import numpy as np
from matplotlib.ticker import FuncFormatter
from matplotlib import gridspec
from sklearn import gaussian_process

class SingleBars:
    
    def __init__(self, poll, parties, elections=None, join_coalitions=True):
         
        self._fig, ax = plt.subplots()

        plt.rcParams['xtick.labelsizfe'] = 16
        plt.rcParams['axes.labelweight'] = 'bold'
        plt.rcParams['font.weight'] = 'normal'
        plt.rcParams['xtick.major.pad']='16'
        plt.rcParams['axes.titlesize'] = 20
        plt.rcParams['axes.titleweight'] = 'bold'

        parties_votes = []

        for i, p in enumerate(parties.parties.values()):    
                parties_votes.append((p, poll.get_party(p,join_coalitions)))
                
        parties_votes.sort(key=lambda x: x[1], reverse=True)
        parties_votes = []
        for i, p in enumerate(parties.parties.values()):    
            parties_votes.append((p, poll.get_party(p,join_coalitions)))
            
        parties_votes.sort(key=lambda x: x[1], reverse=True)
        width = 0.6
        left_lim = 0.1
        plt.title(poll.pollster + poll.date.strftime(' - %-d %b'), loc='left', x=0, y=1.1, fontdict={'ha':'left'})
        names = []
        for i, (p, votes) in enumerate(parties_votes):    
            a = ax.bar(left_lim+i, votes, width=width, color=p.color, edgecolor='none')
            ax.text(left_lim+i+width/2, votes-4, '{0}%'.format(votes), 
                   fontdict={'weight':'bold', 'color':'w', 'fontsize':'20', 'ha':'center', 'va':'center'})
            names.append(p.short_name)
            if elections:
                vot =elections.get_party(p,join_coalitions)
                if a:
                    plt.plot([left_lim+i-0.1*width, left_lim+i+width+0.1*width], [vot, vot], color=[0.2,0.2,0.2], linewidth=3)

        idx = np.arange(len(parties.parties))+width/2 + left_lim
        ax.set_xticks(idx)
        ax.set_xlim([0, idx[-1]+width/2 + left_lim])
        ax.set_xticklabels(names);
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.xaxis.set_ticks_position('none') 
        ax.yaxis.set_ticks_position('none') 
        if poll.error:
            plt.figtext(0.125,.94,'({}% error)'.format(poll.error), fontdict={'fontsize': 12})
            
    def export(self, filename):
        """ TODO
        :param filename:
        :return:
        """        
        self._fig.savefig(filename)
def _percentage_formatter(y, _):
    """ TODO
    :param y:
    :return:
    """

    s = str(y)

    if matplotlib.rcParams['text.usetex'] is True:
        return s + r'$\%$'
    else:
        return s + '%'


class TimeSeries:
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
            
        range_lengths = []
        for c in self.columns:
            dates = [p.date for p in c['polls'].polls]
            range_lengths.append(max(dates) - min(dates))
        # range_lengths = [c['polls']['dates'][-1] - c['polls']['dates'][0] for c in self.columns]
        
        range_lengths_nonzero = [r for r in range_lengths if r != 0]
        total_length = (sum(range_lengths) / (1 - (len(self.columns) - len(range_lengths_nonzero)) * 0.1))
        range_lengths = [r / total_length if r != 0 else 0.1 for r in range_lengths]
        print(range_lengths)
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
        formatter = FuncFormatter(_percentage_formatter)
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
            ax.scatter(x, y, c=np.append(self.parties[partyname].color, [0.6]), edgecolors='none', s=40,
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
                color=np.append(self.parties[partyname].color, [0.1]), fc='b', ec='None',
                label='95% confidence interval')
