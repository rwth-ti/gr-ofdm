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
from gnuradio import blocks

import math

class fbmc_remove_preamble_vcvc(gr.hier_block2):
    """
    docstring for block fbmc_remove_preamble_vcvc
    """
    def __init__(self, M, syms_per_frame, preamble_length):
        gr.hier_block2.__init__(self,
            "fbmc_remove_preamble_vcvc",
            gr.io_signature(1, 1, gr.sizeof_gr_complex*M),
            gr.io_signature(1, 1, gr.sizeof_gr_complex*M),
        )

        # Parameters
        self.M = M
        self.syms_per_frame = syms_per_frame
        self.preamble_length = preamble_length

        # Assertions
        assert (M>0 and syms_per_frame>0), "M and syms_per_frame should be larger than zero!"
        assert ( int(math.log(M,2))==math.log(M,2)), "M should be of 2^n!"
        assert (self.preamble_length>0), "Preamble should be predefined."
        assert (self.preamble_length%M == 0), "preamble should be a multiple of M"

        # Blocks
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, M)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, M)
        self.blocks_keep_m_in_n_0 = blocks.keep_m_in_n(gr.sizeof_gr_complex, 2*syms_per_frame*M, 2*syms_per_frame*M+preamble_length, preamble_length)

        # Connections
        self.connect((self, 0), (self.blocks_vector_to_stream_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self, 0))
        self.connect((self.blocks_keep_m_in_n_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.blocks_vector_to_stream_0, 0), (self.blocks_keep_m_in_n_0, 0))
