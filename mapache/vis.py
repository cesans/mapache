# mapache, @cesans 2016 (c)

import matplotlib.pylab as plt
import matplotlib
import numpy as np
from sklearn import gaussian_process
import time
import datetime

class SingleBars:
    
    def __init__(self, poll, parties, elections=None, join_coalitions=True):
        plt.rcParams['figure.figsize'] = (12, 6)

        self._fig, ax = plt.subplots()

        plt.rcParams['xtick.labelsize'] = 16
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
        #TODO sure?
        plt.rcParams['figure.figsize'] = (18,12)
        
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
            # TODO add get_dates() to ListPolls!!
            dates = [p.date for p in c['polls'].polls]
            range_lengths.append((max(dates) - min(dates)).days)
        # range_lengths = [c['polls']['dates'][-1] - c['polls']['dates'][0] for c in self.columns]
        
        range_lengths_nonzero = [r for r in range_lengths if r != 0]
        total_length = (sum(range_lengths) / (1 - (len(self.columns) - len(range_lengths_nonzero)) * 0.1))
        range_lengths = [r / total_length if r != 0 else 0.1 for r in range_lengths]
        gs = matplotlib.gridspec.GridSpec(1, len(self.columns), width_ratios=range_lengths)

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
            for poll in c['polls'].polls:
                for name, percentages in poll.parties.items():
                    max_percentage = max(max_percentage, np.max(percentages))
                
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

        #From type!!
        dates = [p.date for p in polls.polls]

        single = len(dates) == 1

        title_loc = 'left'
        if single:
            title_loc = 'center'

        ax.set_title(polls._name, loc=title_loc)
        
        self.__scatter(polls, self.parties, ax, single, last)
        if not single:
            self.__gp(polls, self.parties, ax)        

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
        formatter = matplotlib.ticker.FuncFormatter(_percentage_formatter)
        ax.get_yaxis().set_major_formatter(formatter)

        # ax.set_xlim(polls['dates'][0] - 0.5, polls['dates'][-1] + 0.5)

        if not first:
            ax.set_yticklabels([])

        if single:
            #TODO fix!
            ax.set_xticks([polls.polls[0].date], minor=False)
            pass

    def __scatter(self, polls, parties, ax, single=False, last=False):
        """ TODO
        :param single:
        :return:
        """
        
        last_date = datetime.datetime.min
        
        for party in parties.parties.values():
            polls_party = polls.get_party(party)
            
            dates = [x[0] for x in polls_party]
            votes = [x[1] for x in polls_party]           

            if single:
                ax.scatter(dates, votes, 70, c=party.color, edgecolors='none', label=u'Observations')
            else:
                ax.scatter(dates, votes, c=np.append(party.color, [0.6]), edgecolors='none', s=40,
                       label=u'Observations')
            
            last_date = max(last_date, max(dates))
        
        
        if last:
            # TODO move to last point of regression, not poll
            #TODO add name label at the end!
            for party in parties.parties.values():
                 polls_party = polls.get_party(party)
                 
                 last_date_arg = np.argmin([x[0] for x in polls_party])
                 votes = polls_party[last_date_arg][1]
                 polls_party = polls.get_party(party)           
                 plt.text(last_date, votes, '  ' + party.short_name,
                          color=party.color, weight='bold', 
                          verticalalignment='center', fontsize=20)

            
    def __gp(self,polls, parties, ax):
        """ TODO

        :param x:
        :param ax:
        :param partyname:
        :return:
        """
        for party in parties.parties.values():
            polls_party = polls.get_party(party)
            
            dates = [x[0] for x in polls_party]
            votes = [x[1] for x in polls_party]           
        
            x = dates
            y = votes

            # + 0.5 - 0.5?
            
            x_dense = np.atleast_2d(np.linspace(time.mktime(x[0].timetuple()),
                                                time.mktime(x[-1].timetuple()), 1000)).T
            #x_dense = np.atleast_2d(np.linspace(x[0], x[-1], 1000)).T

            np.random.seed(1)            
            gp = gaussian_process.GaussianProcess(corr='squared_exponential', theta0=1e-1,
                                                  thetaL=1e-3, thetaU=1,
                                                  random_start=100, nugget=10 - 8)
            x = [time.mktime(xi.timetuple()) for xi in x]
            gp.fit(np.reshape(x, (-1, 1)) + np.random.randn(len(x),1)*0.01, np.reshape(y,(-1, 1)))
            y_pred, mse = gp.predict(x_dense, eval_MSE=True)
            sigma = np.sqrt(mse)
            x_dense = [datetime.datetime.fromtimestamp(xi) for xi in x_dense]
            ax.plot(x_dense, y_pred, 'b-', label=u'Prediction', c=party.color, linewidth=3)
            # TODO Check and (maybe) fix?
            #  ax.fill(np.concatenate([x_dense, x_dense[::-1]]),
            #        np.concatenate([y_pred - 1.9600 * sigma,
            #                        (y_pred + 1.9600 * sigma)[::-1]]),
            #       color=np.append(party.color, [0.1]), fc='b', ec='None',
            #     label='95% confidence interval')
