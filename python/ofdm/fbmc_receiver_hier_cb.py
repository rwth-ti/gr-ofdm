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

import warnings
import math

from gnuradio import blocks
from gnuradio import fft
from gnuradio import gr
from gnuradio.fft import window
from gnuradio.filter import firdes
from grc_gnuradio import blks2 as grc_blks2
import ofdm

class fbmc_receiver_hier_cb(gr.hier_block2):
    """
    docstring for block fbmc_receiver_hier_cb
    """
    def __init__(self, M=1024, K=4, qam_size=16, syms_per_frame=10, carriers=924, theta_sel=0, sel_eq=0, exclude_preamble=0, center_preamble=None, zero_pads=1):
        gr.hier_block2.__init__(self,
            "fbmc_receiver_hier_cb",
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
            gr.io_signature(1, 1, gr.sizeof_char*1),
        )

        ##################################################
        # Parameters
        ##################################################
        self.theta_sel = theta_sel
        self.exclude_preamble = exclude_preamble
        self.sel_eq = sel_eq
        self.M = M
        self.K = K
        self.qam_size = qam_size
        self.syms_per_frame = syms_per_frame

        ##################################################
        # Variables
        ##################################################
        # only zero_pads|center preamble|zero_pads type of preambles are supported.
        # center preambles are assumed to be normalized to 1.
        if center_preamble is None:
            self.center_preamble = center_preamble = [1, -1j, -1, 1j]
        else:
            self.center_preamble = center_preamble
        self.preamble = preamble = [0]*M*zero_pads+center_preamble*((int)(M/len(center_preamble)))+[0]*M*zero_pads

        if self.exclude_preamble == 1 and self.sel_eq != 3:
            self.sel_eq = sel_eq = 3
            warnings.warn("Since exclude_preamble is set as 1, sel_eq is forced to be 3 (no equalizer)")

        self.skip = skip = 0
        if exclude_preamble == 1 or sel_eq == 3 or sel_eq== 0:
            self.skip = skip = 0
        else:
            self.skip = skip = 1
        self.preamble_length = preamble_length = len(preamble)

        # Assertions
        assert(M>0 and K>0 and qam_size>0), "M, K and qam_size should be bigger than 0"
        assert((math.log(M)/math.log(2))==int(math.log(M)/math.log(2))), "M should be a power of 2"
        assert(K==4), "for now only K=4 s supported."
        assert(qam_size==4 or qam_size==16 or qam_size==64 or qam_size==128 or qam_size==256 ), "Only 4-,16-,64-,128-,256-qam constellations are supported."
        assert(theta_sel==0 or theta_sel==1)
        assert(exclude_preamble==0 or exclude_preamble==1)
        assert((preamble_length/M)==int((preamble_length/M))), "Preamble length should be xM"


        ##################################################
        # Blocks
        ##################################################
        self.fft_vxx_0 = fft.fft_vcc(M, True, (), True, 1)
        self.fbmc_symbol_estimation_vcb_0 = ofdm.fbmc_symbol_estimation_vcb(carriers, qam_size)
        self.fbmc_subchannel_processing_vcvc_0 = ofdm.fbmc_subchannel_processing_vcvc(M, syms_per_frame, (preamble), sel_eq)
        self.fbmc_separate_vcvc_1 = ofdm.fbmc_separate_vcvc(M, 2)
        self.fbmc_remove_preamble_vcvc_0 = ofdm.fbmc_remove_preamble_vcvc(M, syms_per_frame, preamble_length)
        self.fbmc_polyphase_network_vcvc_0_1 = ofdm.fbmc_polyphase_network_vcvc(M, K, K*M-1, True)
        self.fbmc_polyphase_network_vcvc_0_0_0 = ofdm.fbmc_polyphase_network_vcvc(M, K, K*M-1, True)
        self.fbmc_overlapping_serial_to_parallel_cvc_0 = ofdm.fbmc_overlapping_serial_to_parallel_cvc(M)
        self.vector_mask_0 = ofdm.vector_mask(M,int((M-carriers)/2),carriers,[])
        self.fbmc_oqam_postprocessing_vcvc_0 = ofdm.fbmc_oqam_postprocessing_vcvc(M, 0, theta_sel)
        self.fbmc_junction_vcvc_0 = ofdm.fbmc_junction_vcvc(M, 2)
        self.fbmc_beta_multiplier_vcvc_1 = ofdm.fbmc_beta_multiplier_vcvc(M, K, K*M-1, 0)
        self.blocks_skiphead_0_0 = blocks.skiphead(gr.sizeof_gr_complex*M, skip)
        self.blocks_skiphead_0 = blocks.skiphead(gr.sizeof_gr_complex*M, 2*K-1-1)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vcc(([1.0/(M*0.6863)]*M))
        self.blks2_selector_0 = grc_blks2.selector(
            item_size=gr.sizeof_gr_complex*M,
            num_inputs=2,
            num_outputs=1,
            input_index=exclude_preamble,
            output_index=0,
        )
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex*M)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.fbmc_oqam_postprocessing_vcvc_0, 0), (self.vector_mask_0, 0))
        self.connect((self.vector_mask_0, 0), (self.fbmc_symbol_estimation_vcb_0, 0))
        self.connect((self.fbmc_symbol_estimation_vcb_0, 0), (self, 0))
        self.connect((self.blks2_selector_0, 0), (self.blocks_skiphead_0_0, 0))
        self.connect((self.fbmc_beta_multiplier_vcvc_1, 0), (self.blocks_skiphead_0, 0))
        self.connect((self.fbmc_separate_vcvc_1, 1), (self.fbmc_polyphase_network_vcvc_0_0_0, 0))
        self.connect((self.fbmc_separate_vcvc_1, 0), (self.fbmc_polyphase_network_vcvc_0_1, 0))
        self.connect((self.fbmc_overlapping_serial_to_parallel_cvc_0, 0), (self.fbmc_separate_vcvc_1, 0))
        self.connect((self.blocks_skiphead_0_0, 0), (self.fbmc_oqam_postprocessing_vcvc_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.fbmc_beta_multiplier_vcvc_1, 0))
        self.connect((self.blocks_skiphead_0, 0), (self.fbmc_subchannel_processing_vcvc_0, 0))
        self.connect((self.fbmc_polyphase_network_vcvc_0_1, 0), (self.fbmc_junction_vcvc_0, 0))
        self.connect((self.fbmc_polyphase_network_vcvc_0_0_0, 0), (self.fbmc_junction_vcvc_0, 1))
        self.connect((self.fbmc_subchannel_processing_vcvc_0, 0), (self.fbmc_remove_preamble_vcvc_0, 0))
        self.connect((self.fbmc_junction_vcvc_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.fbmc_subchannel_processing_vcvc_0, 0), (self.blks2_selector_0, 1))
        self.connect((self.fbmc_subchannel_processing_vcvc_0, 1), (self.blocks_null_sink_0, 0))
        self.connect((self.fbmc_remove_preamble_vcvc_0, 0), (self.blks2_selector_0, 0))
        self.connect((self, 0), (self.fbmc_overlapping_serial_to_parallel_cvc_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_multiply_const_vxx_0, 0))