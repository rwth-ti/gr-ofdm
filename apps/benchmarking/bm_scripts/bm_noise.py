#!/usr/bin/env python

from gnuradio import gr, blocks, analog

class bm_noise:
    '''
    @title: Benchmark Noise and Fastnoise Source
    '''
    
    def __init__(self, N):
        self.N = N

    def run_noise_source_c(self):
        ntype = analog.GR_GAUSSIAN
        ampl = 10
        seed = 0

        self.blocks = []
        self.tb = gr.top_block()
        self.blocks.append(analog.noise_source_c(ntype, ampl, seed))
        self.blocks.append(blocks.head(gr.sizeof_gr_complex, self.N))
        self.blocks.append(blocks.null_sink(gr.sizeof_gr_complex))
        self.tb.connect(*self.blocks)
        self.tb.run()

    def run_noise_source_f(self):
        ntype = analog.GR_GAUSSIAN
        ampl = 10
        seed = 0

        self.blocks = []
        self.tb = gr.top_block()
        self.blocks.append(analog.noise_source_f(ntype, ampl, seed))
        self.blocks.append(blocks.head(gr.sizeof_float, self.N))
        self.blocks.append(blocks.null_sink(gr.sizeof_float))
        self.tb.connect(*self.blocks)
        self.tb.run()

    def run_noise_source_i(self):
        ntype = analog.GR_GAUSSIAN
        ampl = 10
        seed = 0

        self.blocks = []
        self.tb = gr.top_block()
        self.blocks.append(analog.noise_source_i(ntype, ampl, seed))
        self.blocks.append(blocks.head(gr.sizeof_int, self.N))
        self.blocks.append(blocks.null_sink(gr.sizeof_int))
        self.tb.connect(*self.blocks)
        self.tb.run()

    def run_noise_source_s(self):
        ntype = analog.GR_GAUSSIAN
        ampl = 10
        seed = 0

        self.blocks = []
        self.tb = gr.top_block()
        self.blocks.append(analog.noise_source_s(ntype, ampl, seed))
        self.blocks.append(blocks.head(gr.sizeof_short, self.N))
        self.blocks.append(blocks.null_sink(gr.sizeof_short))
        self.tb.connect(*self.blocks)
        self.tb.run()


    # FAST NOISE SOURCES

    def run_fastnoise_source_c(self):
        ntype = analog.GR_GAUSSIAN
        ampl = 10
        seed = 0

        self.blocks = []
        self.tb = gr.top_block()
        self.blocks.append(analog.fastnoise_source_c(ntype, ampl, seed))
        self.blocks.append(blocks.head(gr.sizeof_gr_complex, self.N))
        self.blocks.append(blocks.null_sink(gr.sizeof_gr_complex))
        self.tb.connect(*self.blocks)
        self.tb.run()

    def run_fastnoise_source_f(self):
        ntype = analog.GR_GAUSSIAN
        ampl = 10
        seed = 0

        self.blocks = []
        self.tb = gr.top_block()
        self.blocks.append(analog.fastnoise_source_f(ntype, ampl, seed))
        self.blocks.append(blocks.head(gr.sizeof_float, self.N))
        self.blocks.append(blocks.null_sink(gr.sizeof_float))
        self.tb.connect(*self.blocks)
        self.tb.run()

    def run_fastnoise_source_i(self):
        ntype = analog.GR_GAUSSIAN
        ampl = 10
        seed = 0

        self.blocks = []
        self.tb = gr.top_block()
        self.blocks.append(analog.fastnoise_source_i(ntype, ampl, seed))
        self.blocks.append(blocks.head(gr.sizeof_int, self.N))
        self.blocks.append(blocks.null_sink(gr.sizeof_int))
        self.tb.connect(*self.blocks)
        self.tb.run()

    def run_fastnoise_source_s(self):
        ntype = analog.GR_GAUSSIAN
        ampl = 10
        seed = 0

        self.blocks = []
        self.tb = gr.top_block()
        self.blocks.append(analog.fastnoise_source_s(ntype, ampl, seed))
        self.blocks.append(blocks.head(gr.sizeof_short, self.N))
        self.blocks.append(blocks.null_sink(gr.sizeof_short))
        self.tb.connect(*self.blocks)
        self.tb.run()

