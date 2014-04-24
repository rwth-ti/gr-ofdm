#!/usr/bin/env python


import numpy
import re
import cPickle as pickle
import operator
import matplotlib.pyplot as plt
from argparse import ArgumentParser



width = 0.4

def add_argparser():
    parser = ArgumentParser(description='Benchmarking tool for GR flowgraphs')
    parser.add_argument('-f', '--file', type=str, default='output.pkl',
                        help='Input file of pickled data [default=%(default)s]')
    parser.add_argument('-b', '--file-two', type=str, default='output.pkl',
                        help='Input file of pickled data [default=%(default)s]')
    parser.add_argument("-n", "--nitems", type=int, default=1000000,
                      help="Number of processed items [default=%default]")
    return parser

class plotter:
    def __init__(self, test, results,results_2, fignum,nitems):
        self.test = test

        self.fignum = fignum
        self.title = self.extract_title(test)
        self.nitems = nitems

        self.v = v = results.values()
        self.v_2 = v_2 = results_2.values()
        #print v
        
        self.labels = results.keys()
        self.pt_mins = numpy.array([vi[0] for vi in v])
        self.pt_avgs = numpy.array([vi[1] for vi in v])
        self.pt_stddev = numpy.array([numpy.sqrt(vi[2]) for vi in v])
        self.bt_mins = numpy.array([vi[3] for vi in v])
        self.bt_avgs = numpy.array([vi[4] for vi in v])
        self.bt_stddev = numpy.array([numpy.sqrt(vi[5]) for vi in v])
        self.mins_x = numpy.array(xrange(len(v)))
        self.avgs_x = self.mins_x+width

        self.fig = plt.figure(fignum, figsize=(18,10), facecolor='w')
        self.sp1 = self.fig.add_subplot(1,2,1)
        self.sp1.barh(self.mins_x, self.pt_mins, height=width,
                      alpha=0.55, label='minimum')
        self.sp1.barh(self.avgs_x, self.pt_avgs, height=width, xerr=1./self.pt_stddev,
                      capsize=5, color='r', alpha=0.55, label='average')
        self.sp1.set_title(self.title, fontsize=22, fontweight='bold')
        self.sp1.set_xlabel("Time (ms)", fontsize=16, fontweight='bold')
        self.sp1.set_yticks(self.mins_x+width)
        self.sp1.set_yticklabels(self.labels, fontweight='bold')
        self.sp1.legend()

        self.sp2 = self.fig.add_subplot(1,2,2)
        self.sp2.barh(self.mins_x, self.bt_mins/self.pt_mins, height=width,
                      alpha=0.55, label='minimum')
        self.sp2.barh(self.avgs_x, self.bt_avgs/self.pt_avgs, height=width,# xerr=bt_stddev,
                      capsize=5, color='r', alpha=0.55, label='average')
        self.sp2.set_title("Ratio block times / program time", fontsize=22, fontweight='bold')
        self.sp2.set_xlabel("Time (ms)", fontsize=16, fontweight='bold')
        self.sp2.set_yticks(self.mins_x+width)
        self.sp2.set_yticklabels(self.labels, fontweight='bold')
        self.sp2.legend()

        self.cid = self.fig.canvas.mpl_connect('button_release_event',
                                               self.mouse_button_callback)

    def extract_title(self, test):
        '''
        Find the title of the benchmark program from the docstring
        '''

        title = "TEST"
        find_title = re.compile('    @title*')
        qa = __import__('bm_scripts.' + test['module'], globals(), locals(), test['testname'])
        test_suite = getattr(qa, test['testname'])
        obj = test_suite(0)
        for line in obj.__doc__.split("\n"):
            title = find_title.match(line)
            if title:
                title = title.string.split("@title: ")[1]
                break
        return title
        
    def mouse_button_callback(self, event):
        y = event.ydata
        if y is not None:
            dist = [abs(y-a) for a in self.sp1.get_yticks()]
            index = dist.index(min(dist))
            v = self.v[index]
            v_2 = self.v_2[index]
            self.plot_blocks_throughput(v,v_2)


    def plot_blocks(self, data):
        nblocks = data[6]
        #print "data 6 ", data[6]
        #print "data 8 ", data[8]
        # data[7] gives minimum
        # data[8] gives average
        # data[9] gives variance

        block_dict = data[8]
        self.blks_x = numpy.array(xrange(nblocks))

        sorted_dict = sorted(block_dict.iteritems(), key=operator.itemgetter(0))
        sorted_dict.reverse()
        self.blks_times = [s[1] for s in sorted_dict]
        self.blks_keys = [s[0] for s in sorted_dict]

        self.fig100 = plt.figure(100+self.fignum, figsize=(18,10), facecolor='w')
        self.fig100.clf()
        self.sp101 = self.fig100.add_subplot(1,1,1)
        self.sp101.barh(self.blks_x, self.blks_times, height=2*width,
                        alpha=0.55)
        print self.blks_times
        self.sp101.set_title(self.title, fontsize=22, fontweight='bold')
        self.sp101.set_xlabel("Time (ms)", fontsize=16, fontweight='bold')
        self.sp101.set_yticks(self.blks_x+width)
        self.sp101.set_yticklabels(self.blks_keys, fontweight='bold')
        self.sp101.grid()
        self.sp101.set_color_cycle(['c', 'm', 'y', 'k'])

        plt.draw()
        
    def plot_blocks_throughput(self, data, data_2):
        nblocks = data[6]
        nblocks_2 = data_2[6]
        #print "data 6 ", data[6]
        #print "data 7 ", data[7]
        # data[7] gives minimum
        # data[8] gives average
        # data[9] gives variance

        block_dict = data[8]
        block_dict_2 = data_2[8]
        self.blks_x = numpy.array(xrange(nblocks))
        self.blks_x_2 = numpy.array(xrange(nblocks_2))

        sorted_dict = sorted(block_dict.iteritems(), key=operator.itemgetter(0))
        sorted_dict.reverse()
        self.blks_times = [s[1] for s in sorted_dict]
        self.blks_keys = [s[0] for s in sorted_dict]
        
        sorted_dict_2 = sorted(block_dict_2.iteritems(), key=operator.itemgetter(0))
        sorted_dict_2.reverse()
        self.blks_times_2 = [s[1] for s in sorted_dict_2]
        self.blks_keys_2 = [s[0] for s in sorted_dict_2]

        self.fig100 = plt.figure(100+self.fignum, figsize=(18,10), facecolor='w')
        self.fig100.clf()
        self.sp101 = self.fig100.add_subplot(1,1,1)
        
        self.blks_times[:] = [x/self.nitems*1000 for x in self.blks_times]
        self.blks_times_2[:] = [x/self.nitems*1000 for x in self.blks_times_2] 
        print "self.blks_times ", self.blks_times
        
        self.sp101.barh(self.blks_x, self.blks_times, height=width,
                        color='r',alpha=0.85, label='Intel(R) Core(TM) i7-960  CPU@3.20GHz')
        self.sp101.barh(self.blks_x_2+width, self.blks_times_2, height=width,
                        color='b',alpha=0.85, label='Intel(R) Core(TM) i7-2620M CPU@2.70GHz')
        #print self.blks_times
        self.sp101.set_title(self.title, fontsize=22, fontweight='bold')
        self.sp101.set_xlabel("Time per OFDM symbol (us)", fontsize=16, fontweight='bold')
        self.sp101.set_yticks(self.blks_x+width)
        self.sp101.set_yticklabels(self.blks_keys, fontweight='bold')
        self.sp101.grid()
        self.sp101.legend()
        #self.sp101.set_color_cycle(['c', 'm', 'y', 'k'])

        plt.draw()
        #plt.savefig('test_figure.pgf')    


def main():
    plt.ion()

    parser = add_argparser()
    args = parser.parse_args()

    data = pickle.load(open(args.file, 'rb'))
    tests = data[1]
    results = data[2]
    #print results
    data_2 = pickle.load(open(args.file_two, 'rb'))
    tests_2 = data_2[1]
    results_2 = data_2[2]
    
    nitems = args.nitems


    nfigs = 0
    plots = []
    for t in tests:
        nfigs += 1
        plots.append(plotter(t, results[t['testname']], results_2[t['testname']], nfigs, nitems))

    plt.show(block=True)


if __name__ == "__main__":
    main()
