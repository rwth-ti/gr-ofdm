#!/usr/bin/env python

import sys, re, time, random, pprint
import numpy
import json
import cPickle as pickle
from argparse import ArgumentParser

from gnuradio import gr

enable_ctrlport = True
try:
    import Ice
    from gnuradio.ctrlport import GNURadio
    from gnuradio import ctrlport
except:
    enable_ctrlport = False

import gr_profiler

# force controlport export configuration on at startup 
for (cat,opt) in [("ControlPort","on"), ("ControlPort","edges_list"), ("PerfCounters","on"), ("PerfCounters","export")]:
    gr.prefs().singleton().set_bool(cat,opt,True);


def add_argparser():
    parser = ArgumentParser(description='Benchmarking tool for GR flowgraphs')
    parser.add_argument('-F', '--file', type=str, default=None,
                        help='Config file listing tests to run [default=%(default)s]')
    parser.add_argument('-D', '--directory', type=str, default=None,
                        help='Directory to read the benchmark scripts from [default=%(default)s]')
    parser.add_argument('-o', '--ofile', type=str, default='output.pkl',
                        help='Output file to write to [default=%(default)s]')
    parser.add_argument('--iscripts', nargs='*', type=str, default=None,
                        help='Input benchmarking scripts to read [default=%(default)s]')
    parser.add_argument('--nitems', nargs='*', type=int,
                        help='Number of items to process [default=%(default)s]')
    parser.add_argument('--iters', nargs='*', type=int,
                        help='Number of iteration to use [default=%(default)s]')
    parser.add_argument('--cores', nargs='*', type=int, default=[0,],
                        help='Space-separated list of cores to allow use of [default=%(default)s]')
    parser.add_argument('-V', '--verbose', type=int, default=0,
                        help='verbosity level; 1=normal, 2=extra  [default=%(default)s]')
    return parser

def get_block_times(ic, tbname):
    # Get available endpoint
    ep = gr.rpcmanager_get().endpoints()[0]

    # Initialize a simple Ice client from endpoint
    base = ic.stringToProxy(ep)
    radio = GNURadio.ControlPortPrx.checkedCast(base)

    # Get all blocks with stream connections in the flowgraph
    b = radio.get(["{0}::edge list".format(tbname)])
    tb_key = b.keys()[0]
    b = b[tb_key].value.split("\n")

    # Get all blocks with message connectiosn in flowgraph
    mb = radio.getRe(["{0}::msg edges list".format(tbname)])
    tb_key = mb.keys()[0]
    b += mb[tb_key].value.split("\n")
    b = filter(None, b)

    # Split the edges list, make a set of unique blocks in flowgraph
    blocks = set()
    for block in b:
        a = block.split("->")[0].split(":")[0]
        b = block.split("->")[1].split(":")[0]
        blocks.add(a)
        blocks.add(b)

    # For each block, extract the "total work time" Perf Counter
    times = dict()
    for b in blocks:
        key = b + "::total work time"
        t = radio.get([key])
        times[b] = float(t[key].value)

    return times


def main():
    parser = add_argparser()
    args = parser.parse_args()
    verbose = args.verbose
    kwargs = {}

    ic = None
    if enable_ctrlport: 
        ic = Ice.initialize(sys.argv)

    if(args.file is None and args.iscripts is None):
        print "Please specify either a config file or a list of scripts to run.\n"
        parser.print_help()
        sys.exit(1)

    if args.file is None:
        nscripts = len(args.iscripts)
        if(args.nitems is None or args.iters is None):
            print "Please specify a number of items and number of iterations for each benchmark script provided.\n"
            parser.print_help()
            sys.exit()
            
        if(len(args.nitems) != nscripts or len(args.iters) != nscripts):
            print "Please specify a number of items and number of iterations for each benchmark script provided.\n"
            parser.print_help()
            sys.exit()

        tests = []
        for n in xrange(nscripts):
            newtest = dict()
            newtest['module'] = args.iscripts[n]
            newtest['testname'] = args.iscripts[n]
            newtest['nitems'] = args.nitems[n]
            newtest['iters'] = args.iters[n]
            tests.append(newtest)

    else:
        print args.file
        f = json.load(open(args.file, 'rb'))
        if args.directory:
            script_dir = args.directory
        else:
            try:
                script_dir = f['directory']
            except KeyError:
                script_dir = "bm_scripts"
        tests = f['tests']

    find_tests = re.compile('run*')
    tpms = gr.high_res_timer_tps()/1000.0 # ticks per millisecond
    #print "tpms", tpms

    procinfo = gr_profiler.cpuinfo()
    procver = gr_profiler.kversion()
    sysinfo = procinfo + procver
    #print sysinfo

    results = {}
    
    if args.directory:
        script_dir = args.directory
    else:
        try:
            script_dir = f['directory']
        except KeyError:
            script_dir = "bm_scripts"

    for ntest, t in enumerate(tests):
        test_name = t['module'] + "." + t['testname']
        print test_name
        qa = __import__(script_dir + '.' + t['module'], globals(), locals(), t['testname'])
        iters = t['iters']
        nitems = t['nitems']
        if(t.has_key('kwargs')):
            kwargs = t['kwargs']
        fresults = {}

        # Turn off a test by setting iters = 0
        if iters == 0:
            continue

        # Get the name of the test class in the module
        test_suite = getattr(qa, t['testname'])

        # Search for all tests in the test class
        test_funcs = []
        for f in dir(test_suite):
            testf = find_tests.match(f)
            if testf:
                test_funcs.append(testf.string)

        obj = test_suite(nitems, **kwargs)

        # Run each test case iters number of iterations
        for f in test_funcs:
            print "\nRUNNING FUNCTION: {0}.{1}".format(str(test_name), str(f))

            _program_time = numpy.array(iters*[0,])
            _all_blocks_time = numpy.array(iters*[0.0,])
            _nblocks = 0

            # Run function setup
            if hasattr(obj, f.replace("run_", "setup_")):
                _x = getattr(obj, f.replace("run_", "setup_"))()

            for i in xrange(iters):
                _start_time = gr.high_res_timer_now()
                _x = getattr(obj, f)
                _x()
                _end_time = gr.high_res_timer_now()

                _program_time[i] = _end_time - _start_time

                times = {}
                if enable_ctrlport:
                    times = get_block_times(ic, obj.tb._tb.alias())

                if _nblocks == 0:
                    n = len(times.keys())
                    _blocks_times = dict()
                    for bt in times:
                        _blocks_times[bt] = numpy.array(iters*[0.0,])

                _nblocks = len(times.keys())
                for bt in times:
                    _all_blocks_time[i] += float(times[bt])
                    _blocks_times[bt][i] = times[bt]

            pt_min = _program_time.min()/tpms
            pt_avg = _program_time.mean()/tpms
            pt_var = (_program_time/tpms).var()

            bt_min = _all_blocks_time.min()/tpms
            bt_avg = _all_blocks_time.mean()/tpms
            bt_var = (_all_blocks_time/tpms).var()

            bt_blks_min = dict()
            bt_blks_avg = dict()
            bt_blks_var = dict()
            for bt in _blocks_times:
                bt_blks_min[bt] = _blocks_times[bt].min()/tpms
                bt_blks_avg[bt] = _blocks_times[bt].mean()/tpms
                bt_blks_var[bt] = (_blocks_times[bt]/tpms).var()

            if(verbose):
                print "Num. Blocks:   {0}".format(_nblocks)
                print "Program Time:  {0:.2f} ms".format(pt_avg)
                print "     std dev:  {0:.2e} ms".format(numpy.sqrt(pt_var))
                print "Block Time:    {0:.2f} ms".format(bt_avg)
                print "     std dev:  {0:.2e} ms".format(numpy.sqrt(bt_var))
                print "Ratio:         {0:.2f}".format(bt_avg/pt_avg)
            fresults[f] = (pt_min, pt_avg, pt_var, bt_min, bt_avg, bt_var,
                           _nblocks, bt_blks_min, bt_blks_avg, bt_blks_var)
        results[t['testname']] = fresults

    #print ""
    #print results
    #print ""

    test_suite = getattr(qa, t['testname'])

    pickle.dump([sysinfo, tests, results], open(args.ofile, 'wb'))


if __name__ == "__main__":
    main()
