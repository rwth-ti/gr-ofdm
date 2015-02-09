#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2015 <+YOU OR YOUR COMPANY+>.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

from gnuradio import gr

class scfdma_transmitter_bc(gr.hier_block2):
    """
    docstring for block scfdma_transmitter_bc
    """
    def __init__(self, N=12, M=256, start_index=10, mapping=0, modulation=16, cp_ratio=0.25):
        gr.hier_block2.__init__(self,
            "scfdma_transmitter_bc",
            gr.io_signature(1, 1, gr.sizeof_char*1),
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
        )

        ##################################################
        # Parameters
        ##################################################
        self.N = N
        self.M = M
        self.start_index = start_index
        self.modulation = modulation
        self.cp_ratio = cp_ratio
        self.mapping = mapping

        ##################################################
        # Blocks
        ##################################################
        self.ofdm_scfdma_subcarrier_mapper_vcvc_0 = ofdm.scfdma_subcarrier_mapper_vcvc(N, M, start_index, mapping)
        self.ofdm_fbmc_symbol_creation_bvc_0 = ofdm.fbmc_symbol_creation_bvc(N, modulation)
        self.fft_vxx_0_0 = fft.fft_vcc(M, False, (), True, 1)
        self.fft_vxx_0 = fft.fft_vcc(N, True, (), True, 1)
        self.digital_ofdm_cyclic_prefixer_0 = digital.ofdm_cyclic_prefixer(M, M+int(M*cp_ratio), 0, "frame_len")

        ##################################################
        # Connections
        ##################################################
        self.connect((self.digital_ofdm_cyclic_prefixer_0, 0), (self, 0))    
        self.connect((self.fft_vxx_0, 0), (self.ofdm_scfdma_subcarrier_mapper_vcvc_0, 0))    
        self.connect((self.fft_vxx_0_0, 0), (self.digital_ofdm_cyclic_prefixer_0, 0))    
        self.connect((self.ofdm_fbmc_symbol_creation_bvc_0, 0), (self.fft_vxx_0, 0))    
        self.connect((self.ofdm_scfdma_subcarrier_mapper_vcvc_0, 0), (self.fft_vxx_0_0, 0))    
        self.connect((self, 0), (self.ofdm_fbmc_symbol_creation_bvc_0, 0))    


    def get_N(self):
        return self.N

    def set_N(self, N):
        self.N = N

    def get_M(self):
        return self.M

    def set_M(self, M):
        self.M = M

    def get_start_index(self):
        return self.start_index

    def set_start_index(self, start_index):
        self.start_index = start_index

    def get_modulation(self):
        return self.modulation

    def set_modulation(self, modulation):
        self.modulation = modulation

    def get_cp_ratio(self):
        return self.cp_ratio

    def set_cp_ratio(self, cp_ratio):
        self.cp_ratio = cp_ratio
