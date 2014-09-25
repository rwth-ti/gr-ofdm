#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2014 <+YOU OR YOUR COMPANY+>.
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
from gnuradio import fft
from gnuradio.fft import window
from gnuradio.filter import firdes
from grc_gnuradio import blks2 as grc_blks2
from gnuradio import blocks

import ofdm
import math
from fbmc_symbol_creation_bvc import fbmc_symbol_creation_bvc
# import

class fbmc_transmitter_hier_bc(gr.hier_block2):
    """
    docstring for block fbmc_transmitter_hier_bc
    """
    def __init__(self, M=1024, K=4, qam_size=16, syms_per_frame=10, carriers=924, theta_sel=0, exclude_preamble=0, sel_preamble=0, zero_pads=1, extra_pad=False):
        gr.hier_block2.__init__(self,
            "fbmc_transmitter_hier_bc",
            gr.io_signature(1, 1, gr.sizeof_char*1),
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
        )

        ##################################################
        # Parameters
        ##################################################
        self.syms_per_frame = syms_per_frame
        self.qam_size = qam_size
        self.K = K
        self.M = M
        self.exclude_preamble = exclude_preamble
        self.theta_sel = theta_sel
        self.zero_pads = zero_pads

        ##################################################
        # Variables
        ##################################################

        # Assertions
        assert(M>0 and K>0 and qam_size>0), "M, K and qam_size should be bigger than 0"
        assert((math.log(M)/math.log(2))==int(math.log(M)/math.log(2))), "M shouldbe a power of 2"
        assert(K==4), "for now only K=4 s supported."
        assert(qam_size==4 or qam_size==16 or qam_size==64 or qam_size==256 ), "Only 4-,16-,64-,256-qam constellations are supported."
        assert(theta_sel==0 or theta_sel==1)
        assert(exclude_preamble==0 or exclude_preamble==1)

        ##################################################
        # Blocks
        ##################################################
        self.fft_vxx_0_0 = fft.fft_vcc(M, False, (), True, 1)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vcc(([1.0/(M*0.6863)]*M))
        self.fbmc_symbol_creation_bvc_0 = ofdm.fbmc_symbol_creation_bvc(carriers, qam_size)
        self.vector_padding_0 = ofdm.vector_padding(carriers,M,-1)
        self.fbmc_separate_vcvc_0 = ofdm.fbmc_separate_vcvc(M, 2)
        self.fbmc_polyphase_network_vcvc_0_0 = ofdm.fbmc_polyphase_network_vcvc(M, K, K*M-1, False)
        self.fbmc_polyphase_network_vcvc_0 = ofdm.fbmc_polyphase_network_vcvc(M, K, K*M-1, False)
        self.fbmc_overlapping_parallel_to_serial_vcc_0 = ofdm.fbmc_overlapping_parallel_to_serial_vcc(M)
        self.fbmc_oqam_preprocessing_vcvc_0 = ofdm.fbmc_oqam_preprocessing_vcvc(M, 0, theta_sel)
        self.fbmc_insert_preamble_vcvc_0 = ofdm.fbmc_insert_preamble_vcvc(M, syms_per_frame, sel_preamble, zero_pads,extra_pad)
        self.fbmc_beta_multiplier_vcvc_0 = ofdm.fbmc_beta_multiplier_vcvc(M, K, K*M-1, 0)
        self.blks2_selector_0 = grc_blks2.selector(
            item_size=gr.sizeof_gr_complex*M,
            num_inputs=2,
            num_outputs=1,
            input_index=exclude_preamble,
            output_index=0,
        )

        ##################################################
        # Connections
        ##################################################
        self.connect((self.fbmc_symbol_creation_bvc_0, 0), (self.vector_padding_0,0))
        self.connect((self.vector_padding_0,0),(self.fbmc_oqam_preprocessing_vcvc_0, 0))
        self.connect((self, 0), (self.fbmc_symbol_creation_bvc_0, 0))
        self.connect((self.fbmc_beta_multiplier_vcvc_0, 0), (self.fft_vxx_0_0, 0))
        self.connect((self.fft_vxx_0_0, 0), (self.blocks_multiply_const_vxx_0,0))
        self.connect((self.blocks_multiply_const_vxx_0,0), (self.fbmc_separate_vcvc_0, 0))
        self.connect((self.fbmc_polyphase_network_vcvc_0, 0), (self.fbmc_overlapping_parallel_to_serial_vcc_0, 0))
        self.connect((self.fbmc_polyphase_network_vcvc_0_0, 0), (self.fbmc_overlapping_parallel_to_serial_vcc_0, 1))
        self.connect((self.fbmc_separate_vcvc_0, 1), (self.fbmc_polyphase_network_vcvc_0_0, 0))
        self.connect((self.fbmc_separate_vcvc_0, 0), (self.fbmc_polyphase_network_vcvc_0, 0))
        self.connect((self.fbmc_overlapping_parallel_to_serial_vcc_0, 0), (self, 0))
        self.connect((self.fbmc_oqam_preprocessing_vcvc_0, 0), (self.blks2_selector_0, 1))
        self.connect((self.fbmc_oqam_preprocessing_vcvc_0, 0), (self.fbmc_insert_preamble_vcvc_0, 0))
        self.connect((self.fbmc_insert_preamble_vcvc_0, 0), (self.blks2_selector_0, 0))
        self.connect((self.blks2_selector_0, 0), (self.fbmc_beta_multiplier_vcvc_0, 0))