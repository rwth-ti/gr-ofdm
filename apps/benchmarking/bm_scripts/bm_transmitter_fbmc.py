#!/usr/bin/env python

from gnuradio import gr, blocks, digital, analog, zeromq
#from ofdm import snr_estimator
from fbmc_transmit_path import transmit_path
from uhd_interface import uhd_transmitter
import random, numpy
import os
from configparse import OptionParser

class bm_transmitter_fbmc:
    '''
    @title: Benchmark TIGR transmitter
    '''
    
    def __init__(self, N, data_blocks=10):
        #N - the number of OFDM frames analyzed * number of data symbols per frame * mapping
        self.N = N
        self.subcarriers = 208
        self.cp_length = 16
        self.data_blocks = data_blocks
        self.verbose = False
        self.fft_length = 256
        self.coding = 0
        self.rms_amplitude = 0.1
        self.log = False
        self.est_preamble = 1
        self.static_allocation = 0
        self.lab_special_case = 0
        self.nopunct = 1
        self.bandwidth = 2500000.0
        self.tx_freq = 2480000000
        self.bm = True
        self.fbmc = 1
        self.benchmarking = 1
        #self.sps = 4
        #self.eb = 0.25

        # Generate some random bits
        #rndm = random.Random()
        #rndm.seed(0)
        #self.src_data_bpsk = tuple([rndm.randint(0,1) for i in range(0, self.N)])
        #self.src_data_qpsk = tuple([rndm.randint(0,1) for i in range(0, 2*self.N)])
        #self.src_data_8psk = tuple([rndm.randint(0,1) for i in range(0, 3*self.N)])

    def setup_transmitter_fbmc0(self):
        self.tb = gr.top_block()
        self.txpath = transmit_path(self)
        
        self.rpc_mgr_tx = zeromq.rpc_manager()
        self.rpc_mgr_tx.set_reply_socket("tcp://*:6660")
        self.rpc_mgr_tx.start_watcher()

       ## Adding interfaces
        self.rpc_mgr_tx.add_interface("set_amplitude",self.txpath.set_rms_amplitude)
        self.rpc_mgr_tx.add_interface("get_tx_parameters",self.txpath.get_tx_parameters)
        self.rpc_mgr_tx.add_interface("set_modulation",self.txpath.allocation_src.set_allocation)        

        #pts, code = digital.psk_2_0x0()
        #constellation = digital.constellation_psk(pts, code, 2)
        #vlen=208
        #data = [1]*vlen

        #self.src = blocks.vector_source_c(data,True,vlen)
        #self.limit = blocks.head(gr.sizeof_gr_complex*vlen, self.N)
        #self.snr_est = snr_estimator(vlen,8)
        
        #self.p2u = blocks.unpacked_to_packed_bb(1, gr.GR_MSB_FIRST)
        #self.mod = digital.generic_mod(constellation, True, self.sps, True, self.eb)
        #self.snk = blocks.null_sink(gr.sizeof_gr_complex)
               
        
    

    def run_transmitter_fbmc0(self):
        #self.src.rewind()
        """
        try:
            self.tb.run()
        except KeyboardInterrupt,ex:
            self.tb.stop()
        """
        #self.snk = uhd_transmitter( 'type=usrp2',self.bandwidth, 2480000000.0,0.0)
        self.snk = blocks.null_sink(gr.sizeof_gr_complex)
        self.file_sink = blocks.file_sink(gr.sizeof_gr_complex,'tx_out_benchmarking.compl')


        self.tb.connect(self.txpath,self.snk)
        self.tb.connect(self.txpath,self.file_sink) 
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

