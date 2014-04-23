#!/usr/bin/env python

import numpy
from gnuradio import gr, blocks, filter

class fir_filters_equal:
    '''
    @title: Benchmark Equal Len. FIR Filters
    '''
    
    def __init__(self, N, mfirs=0, ntaps=0):
        self.N = N
        self.mfirs = mfirs
        self.ntaps = ntaps

    def run_fir_filters_fff(self):
        self.blocks = []
        self.tb = gr.top_block()
        self.blocks.append(blocks.null_source(gr.sizeof_float))
        self.blocks.append(blocks.head(gr.sizeof_float, self.N))

        # Set up mfirs filters with new taps for each filter
        for m in xrange(self.mfirs):
            taps = numpy.random.random(self.ntaps)
            self.blocks.append(filter.fir_filter_fff(1, taps))
            #self.blocks[m].set_processor_affinity([m,])

        # Add a null sink
        self.blocks.append(blocks.null_sink(gr.sizeof_float))

        # Connect the blocks and run
        self.tb.connect(*self.blocks)
        self.tb.run()

    def run_fir_filters_ccf(self):
        self.blocks = []
        self.tb = gr.top_block()
        self.blocks.append(blocks.null_source(gr.sizeof_gr_complex))
        self.blocks.append(blocks.head(gr.sizeof_gr_complex, self.N))

        # Set up mfirs filters with new taps for each filter
        for m in xrange(self.mfirs):
            taps = numpy.random.random(self.ntaps)
            self.blocks.append(filter.fir_filter_ccf(1, taps))
            #self.blocks[m].set_processor_affinity([m,])

        # Add a null sink
        self.blocks.append(blocks.null_sink(gr.sizeof_gr_complex))

        # Connect the blocks and run
        self.tb.connect(*self.blocks)
        self.tb.run()

class fir_filters_nonequal:
    '''
    @title: Benchmark Non-Equal Len. FIR Filters
    '''
    
    def __init__(self, N, mfirs=0, ntaps=0, mult=1):
        self.N = N
        self.mfirs = mfirs
        self.ntaps = ntaps
        self.mult = mult

    def run_fir_filters_fff(self):
        self.blocks = []
        self.tb = gr.top_block()
        self.blocks.append(blocks.null_source(gr.sizeof_float))
        self.blocks.append(blocks.head(gr.sizeof_float, self.N))

        # First filter is much larger than others
        taps = numpy.random.random(self.mult*self.ntaps)
        self.blocks.append(filter.fir_filter_fff(1, taps))
        self.blocks[0].set_processor_affinity([0,])

        # Set up rest of mfirs filters with new taps for each filter
        for m in xrange(1, self.mfirs):
            taps = numpy.random.random(self.ntaps)
            self.blocks.append(filter.fir_filter_fff(1, taps))
        #self.blocks[m].set_processor_affinity([1,])
        #self.blocks[m].set_processor_affinity([1,])
        #self.blocks[m].set_processor_affinity([1,])
        #self.blocks[m].set_processor_affinity([1,])
        #self.blocks[m].set_processor_affinity([1,])
        #self.blocks[m].set_processor_affinity([1,])
        #self.blocks[m].set_processor_affinity([1,])

        # Add a null sink
        self.blocks.append(blocks.null_sink(gr.sizeof_float))

        # Connect the blocks and run
        self.tb.connect(*self.blocks)
        self.tb.run()

    def run_fir_filters_ccf(self):
        self.blocks = []
        self.tb = gr.top_block()
        self.blocks.append(blocks.null_source(gr.sizeof_gr_complex))
        self.blocks.append(blocks.head(gr.sizeof_gr_complex, self.N))

        # First filter is much larger than others
        taps = numpy.random.random(self.mult*self.ntaps)
        self.blocks.append(filter.fir_filter_ccf(1, taps))

        # Set up mfirs filters with new taps for each filter
        for m in xrange(1, self.mfirs):
            taps = numpy.random.random(self.ntaps)
            self.blocks.append(filter.fir_filter_ccf(1, taps))

        # Add a null sink
        self.blocks.append(blocks.null_sink(gr.sizeof_gr_complex))

        # Connect the blocks and run
        self.tb.connect(*self.blocks)
        self.tb.run()

