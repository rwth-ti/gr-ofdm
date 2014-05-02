#!/usr/bin/env python

from gnuradio import gr, blocks, digital, analog
#from ofdm import snr_estimator
from receive_path import receive_path
from uhd_interface import uhd_receiver
import random, numpy
import os
import zmqblocks
from configparse import OptionParser

class bm_receiver_usrp:
    '''
    @title: Benchmark TIGR receiver
    '''
    
    def __init__(self, N, data_blocks=10):
        # N - the number of OFDM frames analyzed
        self.N = N
        self.subcarriers = 200
        self.cp_length = 16
        self.data_blocks = 10
        self.verbose = False
        self.fft_length = 256
        self.coding = 0
        #self.rms_amplitude = 1000
        self.log = False
        self.est_preamble = 1
        self.static_allocation = 0
        self.lab_special_case = 0
        self.nopunct = 1
        self.bandwidth = 2500000
        self.rx_freq = 2480020000.0
        self.ber_window = 500000
        self.disable_time_sync = False
        self.disable_freq_sync = False
        self.disable_phase_tracking = False
        self.disable_ctf_enhancer = True
        self.disable_equalization = False
        self.scatter_plot_before_phase_tracking = False
        self.enable_erasure_decision = False
        self.scatterplot = False
        self.sfo_feedback = False
        self.enable_ber2 = False
        self.sinr_est = False
        self.logcir = False
        self.ideal = False
        self.tx_hostname = 'tabur'
        self.bm = True
        #self.sps = 4
        #self.eb = 0.25

        # Generate some random bits
        #rndm = random.Random()
        #rndm.seed(0)
        #self.src_data_bpsk = tuple([rndm.randint(0,1) for i in range(0, self.N)])
        #self.src_data_qpsk = tuple([rndm.randint(0,1) for i in range(0, 2*self.N)])
        #self.src_data_8psk = tuple([rndm.randint(0,1) for i in range(0, 3*self.N)])

    def setup_receiver_usrp0(self):
        self.tb = gr.top_block()
        

        
        
        
        
        self.rxpath = receive_path(self)
        
        self.rpc_mgr_rx = zmqblocks.rpc_manager()
        self.rpc_mgr_rx.set_reply_socket("tcp://*:5550")
        self.rpc_mgr_rx.start_watcher()

       ## Adding interfaces
        self.rpc_mgr_rx.add_interface("set_scatter_subcarrier",self.rxpath.set_scatterplot_subc)

        #pts, code = digital.psk_2_0x0()
        #constellation = digital.constellation_psk(pts, code, 2)
        #vlen=208
        #data = [1]*vlen

        #self.src = blocks.vector_source_c(data,True,vlen)
        #self.limit = blocks.head(gr.sizeof_gr_complex*vlen, self.N)
        #self.snr_est = snr_estimator(vlen,8)
        
        #self.p2u = blocks.unpacked_to_packed_bb(1, gr.GR_MSB_FIRST)
        #self.mod = digital.generic_mod(constellation, True, self.sps, True, self.eb)
     
        
    

    def run_receiver_usrp0(self):
        #self.src.rewind()
        """
        try:
            self.tb.run()
        except KeyboardInterrupt,ex:
            self.tb.stop()
        """
        #self.snk = blocks.null_sink(gr.sizeof_gr_complex)
        self.src = uhd_receiver( 'type=usrp2',self.bandwidth, self.rx_freq,0.0)


        self.tb.connect(self.src,self.rxpath)
        self.tb.run()

"""
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
        """

