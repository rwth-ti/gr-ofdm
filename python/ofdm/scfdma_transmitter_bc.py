#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Transmitter
# Generated: Fri Feb  6 18:41:31 2015
##################################################

# Call XInitThreads as the _very_ first thing.
# After some Qt import, it's too late

from gnuradio import digital
from gnuradio import fft
from gnuradio import gr
from gnuradio.fft import window
from gnuradio.filter import firdes
import fbmc
import ofdm

class Transmitter(gr.hier_block2):

    def __init__(self, N=12, M=256, modulation=16, start_index=0, cp_length=0.25):
        gr.hier_block2.__init__(
            self, "SC-FDMA Transmitter",
            gr.io_signature(1, 1, gr.sizeof_char*1),
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
        )

        ##################################################
        # Parameters
        ##################################################
        self.N = N
        self.M = M
        self.modulation = modulation
        self.start_index = start_index
        self.cp_length = cp_length

        ##################################################
        # Blocks
        ##################################################
        self.ofdm_scfdma_subcarrier_mapper_vcvc_0 = ofdm.scfdma_subcarrier_mapper_vcvc(N, M, start_index, 0)
        self.fft_vxx_1 = fft.fft_vcc(M, False, (), True, 1)
        self.fft_vxx_0 = fft.fft_vcc(N, True, (), True, 1)
        self.fbmc_symbol_creation_bvc_0 = fbmc.symbol_creation_bvc(N, modulation)
        self.digital_ofdm_cyclic_prefixer_0 = digital.ofdm_cyclic_prefixer(M, M+int(M*cp_length), 0, "frame_len")

        ##################################################
        # Connections
        ##################################################
        self.connect((self.digital_ofdm_cyclic_prefixer_0, 0), (self, 0))    
        self.connect((self.fbmc_symbol_creation_bvc_0, 0), (self.fft_vxx_0, 0))    
        self.connect((self.fft_vxx_0, 0), (self.ofdm_scfdma_subcarrier_mapper_vcvc_0, 0))    
        self.connect((self.fft_vxx_1, 0), (self.digital_ofdm_cyclic_prefixer_0, 0))    
        self.connect((self.ofdm_scfdma_subcarrier_mapper_vcvc_0, 0), (self.fft_vxx_1, 0))    
        self.connect((self, 0), (self.fbmc_symbol_creation_bvc_0, 0))    


    def get_N(self):
        return self.N

    def set_N(self, N):
        self.N = N

    def get_M(self):
        return self.M

    def set_M(self, M):
        self.M = M

    def get_modulation(self):
        return self.modulation

    def set_modulation(self, modulation):
        self.modulation = modulation

    def get_start_index(self):
        return self.start_index

    def set_start_index(self, start_index):
        self.start_index = start_index

    def get_cp_length(self):
        return self.cp_length

    def set_cp_length(self, cp_length):
        self.cp_length = cp_length

