#!/usr/bin/env python

from gnuradio import gr, blocks, digital, analog
from gnuradio.filter import firdes
from gnuradio.digital.utils import mod_codes
import random, numpy

class bm_pskdemod:
    '''
    @title: Benchmark PSK demodulators
    '''
    
    def __init__(self, N):
        self.N = N
        self.sps = 4
        self.eb = 0.25
        self.freq_bw = 2*numpy.pi/100.0
        self.timing_bw = 2*numpy.pi/100.0
        self.timing_max_dev = 0.5
        self.phase_bw = 2*numpy.pi/100.0
        self.fll_ntaps = 55
        self.fmin = -0.25
        self.fmax = 0.25
        self.nfilts = 32
        self.ntaps = 11 * int(self.sps*self.nfilts)
        self.taps = firdes.root_raised_cosine(self.nfilts, self.nfilts*self.sps,
                                              1.0, self.eb, self.ntaps)

        # Generate some random bits
        rndm = random.Random()
        rndm.seed(0)
        self.src_data_bpsk = tuple([rndm.randint(0,1) for i in range(0, self.N)])
        self.src_data_qpsk = tuple([rndm.randint(0,1) for i in range(0, 2*self.N)])
        self.src_data_8psk = tuple([rndm.randint(0,1) for i in range(0, 3*self.N)])

    def setup_bpsk0(self):
        self.tb = gr.top_block()

        # Build the constellation object
        arity = 2
        bps = 1
        pts, code = digital.psk_2_0x0()
        constellation = digital.constellation_psk(pts, code, 2)

        # Create BPSK data to pass to the demodulator
        src = blocks.vector_source_b(self.src_data_bpsk)
        p2u = blocks.unpacked_to_packed_bb(1, gr.GR_MSB_FIRST)
        mod = digital.generic_mod(constellation, True, self.sps, True, self.eb)
        snk = blocks.vector_sink_c()

        tb = gr.top_block()
        tb.connect(src, p2u, mod, snk)
        tb.run()

        self.src = blocks.vector_source_c(snk.data())
        self.freq_recov = digital.fll_band_edge_cc(self.sps, self.eb,
                                                   self.fll_ntaps, self.freq_bw)
        self.time_recov = digital.pfb_clock_sync_ccf(self.sps, self.timing_bw, self.taps,
                                                     self.nfilts, self.nfilts//2, self.timing_max_dev)
        self.receiver = digital.constellation_receiver_cb(
            constellation.base(), self.phase_bw, self.fmin, self.fmax)
        self.diffdec = digital.diff_decoder_bb(arity)
        self.symbol_mapper = digital.map_bb(
            mod_codes.invert_code(constellation.pre_diff_code()))
        self.unpack = blocks.unpack_k_bits_bb(bps)
        self.snk = blocks.null_sink(gr.sizeof_char)

        self.tb.connect(self.src, self.freq_recov, self.time_recov, self.receiver)
        self.tb.connect(self.receiver, self.diffdec, self.symbol_mapper, self.unpack)
        self.tb.connect(self.unpack, self.snk)

    def run_bpsk0(self):
        self.src.rewind()
        self.tb.run()

    # QPSK 
    def setup_qpsk0(self):
        self.tb = gr.top_block()

        # Build the constellation object
        arity = 4
        bps = 2
        pts, code = digital.psk_4_0x0_0_1()
        constellation = digital.constellation_psk(pts, code, 4)

        # Create QPSK data to pass to the demodulator
        src = blocks.vector_source_b(self.src_data_qpsk)
        p2u = blocks.unpacked_to_packed_bb(1, gr.GR_MSB_FIRST)
        mod = digital.generic_mod(constellation, True, self.sps, True, self.eb)
        snk = blocks.vector_sink_c()

        tb = gr.top_block()
        tb.connect(src, p2u, mod, snk)
        tb.run()


        self.src = blocks.vector_source_c(snk.data())
        self.freq_recov = digital.fll_band_edge_cc(self.sps, self.eb,
                                                   self.fll_ntaps, self.freq_bw)
        self.time_recov = digital.pfb_clock_sync_ccf(self.sps, self.timing_bw, self.taps,
                                                     self.nfilts, self.nfilts//2, self.timing_max_dev)
        self.receiver = digital.constellation_receiver_cb(
            constellation.base(), self.phase_bw, self.fmin, self.fmax)
        self.diffdec = digital.diff_decoder_bb(arity)
        self.symbol_mapper = digital.map_bb(
            mod_codes.invert_code(constellation.pre_diff_code()))
        self.unpack = blocks.unpack_k_bits_bb(bps)
        self.snk = blocks.null_sink(gr.sizeof_char)

        self.tb.connect(self.src, self.freq_recov, self.time_recov, self.receiver)
        self.tb.connect(self.receiver, self.diffdec, self.symbol_mapper, self.unpack)
        self.tb.connect(self.unpack, self.snk)

    def run_qpsk0(self):
        self.src.rewind()
        self.tb.run()


    # 8PSK 
    def setup_8psk0(self):
        self.tb = gr.top_block()

        # Build the constellation object
        arity = 8
        bps = 3
        constellation = digital.psk_constellation(8)

        # Create 8PSK data to pass to the demodulator
        src = blocks.vector_source_b(self.src_data_8psk)
        p2u = blocks.unpacked_to_packed_bb(1, gr.GR_MSB_FIRST)
        mod = digital.generic_mod(constellation, True, self.sps, True, self.eb)
        snk = blocks.vector_sink_c()

        tb = gr.top_block()
        tb.connect(src, p2u, mod, snk)
        tb.run()


        self.src = blocks.vector_source_c(snk.data())
        self.freq_recov = digital.fll_band_edge_cc(self.sps, self.eb,
                                                   self.fll_ntaps, self.freq_bw)
        self.time_recov = digital.pfb_clock_sync_ccf(self.sps, self.timing_bw, self.taps,
                                                     self.nfilts, self.nfilts//2, self.timing_max_dev)
        self.receiver = digital.constellation_receiver_cb(
            constellation.base(), self.phase_bw, self.fmin, self.fmax)
        self.diffdec = digital.diff_decoder_bb(arity)
        self.symbol_mapper = digital.map_bb(
            mod_codes.invert_code(constellation.pre_diff_code()))
        self.unpack = blocks.unpack_k_bits_bb(bps)
        self.snk = blocks.null_sink(gr.sizeof_char)

        self.tb.connect(self.src, self.freq_recov, self.time_recov, self.receiver)
        self.tb.connect(self.receiver, self.diffdec, self.symbol_mapper, self.unpack)
        self.tb.connect(self.unpack, self.snk)

    def run_8psk0(self):
        self.src.rewind()
        self.tb.run()
