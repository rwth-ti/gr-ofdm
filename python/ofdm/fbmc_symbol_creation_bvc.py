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

import math

class fbmc_symbol_creation_bvc(gr.hier_block2):
    """
    docstring for block fbmc_symbol_creation_bvc
    """
    def __init__(self, M=256, qam_size=4):
        gr.hier_block2.__init__(self,
            "fbmc_symbol_creation_bvc",
            gr.io_signature(1, 1, gr.sizeof_char*1),  # Input signature
            gr.io_signature(1, 1, gr.sizeof_gr_complex*M)) # Output signature

        ##################################################
        # Parameters
        ##################################################
        self.M = M
        self.qam_size=qam_size

        # Assertions
        assert (M>0 and qam_size>0), "M and qam_size should be larger than zero!"
        assert ( int(math.log(M,2))==math.log(M,2)), "M should be of 2^n!"
        assert (qam_size==4 or qam_size==16 or qam_size==64 or qam_size==256 ), "Only 4-,16-,64-,256-qam constellations are supported."
        ##################################################
        # Blocks
        ##################################################
        self.digital_chunks_to_symbols_xx_0 = digital.chunks_to_symbols_bc((digital.qam.qam_constellation(qam_size).points()), D=1)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, M)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_stream_to_vector_0, 0), (self, 0))
        self.connect((self, 0), (self.digital_chunks_to_symbols_xx_0, 0))
        self.connect((self.digital_chunks_to_symbols_xx_0, 0), (self.blocks_stream_to_vector_0, 0))
