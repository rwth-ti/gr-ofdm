#!/usr/bin/env python

from gnuradio import gr, blocks, analog

class bm_sig_source:
    '''
    @title: Benchmark Signal Sources
    '''
    
    def __init__(self, N):
        self.N = N

    def run_sig_source_c(self):
        fs = 1
        ntype = analog.GR_SIN_WAVE
        freq = 0.1
        ampl = 1
        
        self.tb = gr.top_block()
        self.op = analog.sig_source_c(fs, ntype, freq, ampl)
        self.head = blocks.head(gr.sizeof_gr_complex, self.N)
        self.snk = blocks.null_sink(gr.sizeof_gr_complex)
        self.tb.connect(self.op, self.head, self.snk)
        self.tb.run()

    def run_sig_source_f(self):
        fs = 1
        ntype = analog.GR_SIN_WAVE
        freq = 10
        ampl = 1

        self.tb = gr.top_block()
        self.op = analog.sig_source_f(fs, ntype, freq, ampl)
        self.head = blocks.head(gr.sizeof_float, self.N)
        self.snk = blocks.null_sink(gr.sizeof_float)
        self.tb.connect(self.op, self.head, self.snk)
        self.tb.run()

    def run_sig_source_i(self):
        fs = 1
        ntype = analog.GR_SIN_WAVE
        freq = 10
        ampl = 1

        self.tb = gr.top_block()
        self.op = analog.sig_source_i(fs, ntype, freq, ampl)
        self.head = blocks.head(gr.sizeof_int, self.N)
        self.snk = blocks.null_sink(gr.sizeof_int)
        self.tb.connect(self.op, self.head, self.snk)
        self.tb.run()

    def run_sig_source_s(self):
        fs = 1
        ntype = analog.GR_SIN_WAVE
        freq = 10
        ampl = 1

        self.tb = gr.top_block()
        self.op = analog.sig_source_s(fs, ntype, freq, ampl)
        self.head = blocks.head(gr.sizeof_short, self.N)
        self.snk = blocks.null_sink(gr.sizeof_short)
        self.tb.connect(self.op, self.head, self.snk)
        self.tb.run()

