#!/usr/bin/env python

import numpy
import re
import cPickle as pickle
import operator
import matplotlib.pyplot as plt
from argparse import ArgumentParser

width = 0.2
params = {'legend.fontsize': 14}
plt.rcParams.update(params)
#plt.rc('legend', labelsize=8) 

def add_argparser():
    parser = ArgumentParser(description='Benchmarking tool for GR flowgraphs')
    parser.add_argument('-f', '--file', type=str, default='output.pkl',
                        help='Input file of pickled data [default=%(default)s]')
    parser.add_argument('-b', '--file-two', type=str, default='output.pkl',
                        help='Input file of pickled data [default=%(default)s]')
    parser.add_argument('-c', '--file-three', type=str, default='output.pkl',
                        help='Input file of pickled data [default=%(default)s]')
    parser.add_argument('-d', '--file-four', type=str, default='output.pkl',
                        help='Input file of pickled data [default=%(default)s]')
    return parser

class plotter:
    def __init__(self, test, test_3, results, results_2, results_3, results_4, fignum):
        self.test = test

        self.fignum = fignum
        self.title = self.extract_title(test)
        self.title = 'Benchmark mapper'

        self.v = v = results.values()
        self.v_2 = v_2 = results_2.values()
        #print v
        
        self.labels = results.keys()
        self.labels_2 = results_2.keys()
        
        #Manually add labels
        #self.labels = 
        
        self.pt_mins = numpy.array([vi[0]/50 for vi in v])
        self.pt_mins_2 = numpy.array([vi[0]/50 for vi in v_2])
        self.pt_avgs = numpy.array([vi[1]/50 for vi in v])
        self.pt_avgs_2 = numpy.array([vi[1]/50 for vi in v_2])
        self.pt_stddev = numpy.array([numpy.sqrt(vi[2])/50 for vi in v])
        self.pt_stddev_2 = numpy.array([numpy.sqrt(vi[2])/50 for vi in v_2])
        #self.bt_mins = numpy.array([vi[3] for vi in v])
        #self.bt_avgs = numpy.array([vi[4] for vi in v])
        #self.bt_stddev = numpy.array([numpy.sqrt(vi[5]) for vi in v])
        self.mins_x = numpy.array(xrange(len(v)))
        self.avgs_x = self.mins_x+width
        self.mins_x_2 = self.mins_x+2*width
        self.avgs_x_2 = self.mins_x_2+width

        self.fig = plt.figure(fignum, figsize=(18,10), facecolor='w')
        self.sp1 = self.fig.add_subplot(1,2,1)
        self.sp1.barh(self.mins_x, self.pt_mins, height=width,color='r',
                      alpha=0.2)
        self.sp1.barh(self.avgs_x, self.pt_avgs, height=width,xerr=self.pt_stddev,ecolor='c', 
                      capsize=5, color='r', alpha=0.85, label='Intel(R) Core(TM) i7-960  CPU@3.20GHz')
        self.sp1.barh(self.mins_x_2, self.pt_mins_2, height=width,
                      alpha=0.25)
        self.sp1.barh(self.avgs_x_2, self.pt_avgs_2, height=width,xerr=self.pt_stddev_2,ecolor='c', 
                      capsize=5, color='b', alpha=0.85, label='Intel(R) Core(TM) i7-2620M CPU@2.70GHz')
        self.sp1.set_title(self.title, fontsize=22, fontweight='bold')
        self.sp1.set_xlabel("Time (us)", fontsize=16, fontweight='bold')
        self.sp1.set_yticks(self.mins_x+width)
        self.sp1.set_yticklabels(self.labels, fontweight='bold')
        self.sp1.legend()
        
        #Adding second plot
        self.title_2 = self.extract_title(test_3)
        self.v = v = results_3.values()
        self.v_2 = v_2 = results_4.values()
        #print v
        
        self.labels = results_3.keys()
        self.labels_2 = results_4.keys()
        
        self.pt_mins = numpy.array([vi[0]/50 for vi in v])
        self.pt_mins_2 = numpy.array([vi[0]/50 for vi in v_2])
        self.pt_avgs = numpy.array([vi[1]/50 for vi in v])
        self.pt_avgs_2 = numpy.array([vi[1]/50 for vi in v_2])
        self.pt_stddev = numpy.array([numpy.sqrt(vi[2])/50 for vi in v])
        self.pt_stddev_2 = numpy.array([numpy.sqrt(vi[2])/50 for vi in v_2])
        #self.bt_mins = numpy.array([vi[3] for vi in v])
        #self.bt_avgs = numpy.array([vi[4] for vi in v])
        #self.bt_stddev = numpy.array([numpy.sqrt(vi[5]) for vi in v])
        self.mins_x = numpy.array(xrange(len(v)))
        self.avgs_x = self.mins_x+width
        self.mins_x_2 = self.mins_x+2*width
        self.avgs_x_2 = self.mins_x_2+width
        
        self.sp2 = self.fig.add_subplot(1,2,2)
        self.sp2.barh(self.mins_x, self.pt_mins, height=width,color='r',
                      alpha=0.2)
        self.sp2.barh(self.avgs_x, self.pt_avgs, height=width,xerr=self.pt_stddev,ecolor='c', 
                      capsize=5, color='r', alpha=0.85, label='Intel(R) Core(TM) i7-960  CPU@3.20GHz')
        self.sp2.barh(self.mins_x_2, self.pt_mins_2, height=width,
                      alpha=0.25)
        self.sp2.barh(self.avgs_x_2, self.pt_avgs_2, height=width,xerr=self.pt_stddev_2,ecolor='c', 
                      capsize=5, color='b', alpha=0.85, label='Intel(R) Core(TM) i7-2620M CPU@2.70GHz')
        self.sp2.set_title(self.title_2, fontsize=22, fontweight='bold')
        self.sp2.set_xlabel("Time (us)", fontsize=16, fontweight='bold')
        self.sp2.set_yticks(self.mins_x+width)
        self.sp2.set_yticklabels(self.labels, fontweight='bold')
        self.sp2.legend()
        
        """
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
        """

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
            self.plot_blocks(v)


    def plot_blocks(self, data):
        nblocks = data[6]
        block_dict = data[7]
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
        self.sp101.set_title(self.title, fontsize=22, fontweight='bold')
        self.sp101.set_xlabel("Time (ms)", fontsize=16, fontweight='bold')
        self.sp101.set_yticks(self.blks_x+width)
        self.sp101.set_yticklabels(self.blks_keys, fontweight='bold')
        self.sp101.grid()
        self.sp101.set_color_cycle(['c', 'm', 'y', 'k'])

        plt.draw()
        
        
def main():
    plt.ion()

    parser = add_argparser()
    args = parser.parse_args()

    data = pickle.load(open(args.file, 'rb'))
    tests = data[1]
    #print "tests", tests
    results = data[2]
    
    data_2 = pickle.load(open(args.file_two, 'rb'))
    tests_2 = data_2[1]
    results_2 = data_2[2]
    
    data_3 = pickle.load(open(args.file_three, 'rb'))
    tests_3 = data_3[1]
    results_3 = data_3[2]
    
    data_4 = pickle.load(open(args.file_four, 'rb'))
    tests_4 = data_4[1]
    results_4 = data_4[2]
    
    #print "tests", tests + tests_3

    nfigs = 0
    plots = []
    for t in tests:
        for t3 in tests_3:
            nfigs += 1
            plots.append(plotter(t,t3, results[t['testname']], results_2[t['testname']],results_3[t3['testname']], results_4[t3['testname']],nfigs))
    
    #nfigs = 0
    #plots = []
    #for t in tests_3:
        #nfigs += 1
       # plots.append(plotter_2(t, results_3[t['testname']], results_4[t['testname']],nfigs))
        #plots.append(plotter(t, results_2[t['testname']], nfigs))

    plt.show(block=True)


if __name__ == "__main__":
    main()
