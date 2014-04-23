#!/usr/bin/env python

from gnuradio import gr, blocks, digital, analog
import random, numpy

class bm_pskmod:
    '''
    @title: Benchmark PSK modulators
    '''
    
    def __init__(self, N):
        self.N = N
        self.sps = 4
        self.eb = 0.25

        # Generate some random bits
        rndm = random.Random()
        rndm.seed(0)
        self.src_data_bpsk = tuple([rndm.randint(0,1) for i in range(0, self.N)])
        self.src_data_qpsk = tuple([rndm.randint(0,1) for i in range(0, 2*self.N)])
        self.src_data_8psk = tuple([rndm.randint(0,1) for i in range(0, 3*self.N)])

    def setup_bpsk0(self):
        self.tb = gr.top_block()

        pts, code = digital.psk_2_0x0()
        constellation = digital.constellation_psk(pts, code, 2)

        self.src = blocks.vector_source_b(self.src_data_bpsk)
        self.p2u = blocks.unpacked_to_packed_bb(1, gr.GR_MSB_FIRST)
        self.mod = digital.generic_mod(constellation, True, self.sps, True, self.eb)
        self.snk = blocks.null_sink(gr.sizeof_gr_complex)

        self.tb.connect(self.src, self.p2u, self.mod, self.snk)

    def run_bpsk0(self):
        self.src.rewind()
        self.tb.run()


    def setup_qpsk0(self):
        self.tb = gr.top_block()

        pts, code = digital.psk_4_0x0_0_1()
        constellation = digital.constellation_psk(pts, code, 4)
        
        self.src = blocks.vector_source_b(self.src_data_qpsk)
        self.p2u = blocks.unpacked_to_packed_bb(1, gr.GR_MSB_FIRST)
        self.mod = digital.generic_mod(constellation, True, self.sps, True, self.eb)
        self.snk = blocks.null_sink(gr.sizeof_gr_complex)

        self.tb.connect(self.src, self.p2u, self.mod, self.snk)

    def run_qpsk0(self):
        self.src.rewind()
        self.tb.run()



    def setup_8psk0(self):
        self.tb = gr.top_block()

        constellation = digital.psk_constellation(8)

        self.src = blocks.vector_source_b(self.src_data_8psk)
        self.p2u = blocks.unpacked_to_packed_bb(1, gr.GR_MSB_FIRST)
        self.mod = digital.generic_mod(constellation, True, self.sps, True, self.eb)
        self.snk = blocks.null_sink(gr.sizeof_gr_complex)

        self.tb.connect(self.src, self.p2u, self.mod, self.snk)

    def run_8psk0(self):
        self.src.rewind()
        self.tb.run()

