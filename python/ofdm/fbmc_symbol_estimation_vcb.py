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
from gnuradio import digital
from gnuradio import blocks
from gnuradio import analog


import math

class fbmc_symbol_estimation_vcb(gr.hier_block2):
    """
    docstring for block fbmc_symbol_estimation_vcb
    """
    def __init__(self, M=256, qam_size=4):
        gr.hier_block2.__init__(self,
            "fbmc_symbol_estimation_vcb",
            gr.io_signature(1, 1, gr.sizeof_gr_complex*M),
            gr.io_signature(1, 1, gr.sizeof_char*1),
        )

        ##################################################
        # Parameters
        ##################################################
        self.M = M
        self.qam_size = qam_size

        # Assertions
        assert (M>0 and qam_size>0), "M and qam_size should be larger than zero!"
        # assert ( int(math.log(M,2))==math.log(M,2)), "M should be of 2^n!"
        assert ( qam_size==4 or qam_size==16 or qam_size==64 or qam_size==256 ), "Only 4-,16-,64-,256-qam constellations are supported."

        ##################################################
        # Blocks
        ##################################################
        self.digital_constellation_decoder_cb_0 = digital.constellation_decoder_cb(digital.qam.qam_constellation(qam_size).base())
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, M)
        # self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.analog_const_source_x_0 = analog.sig_source_c(0, analog.GR_CONST_WAVE, 0, 0, 1.0/M)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.digital_constellation_decoder_cb_0, 0), (self, 0))
        self.connect((self, 0), (self.blocks_vector_to_stream_0, 0))
        self.connect((self.blocks_vector_to_stream_0, 0),(self.digital_constellation_decoder_cb_0, 0))
        # self.connect((self.blocks_multiply_xx_0, 0), (self.digital_constellation_decoder_cb_0, 0))
        # self.connect((self.blocks_vector_to_stream_0, 0), (self.blocks_multiply_xx_0, 0))
        # self.connect((self.analog_const_source_x_0, 0), (self.blocks_multiply_xx_0, 1))