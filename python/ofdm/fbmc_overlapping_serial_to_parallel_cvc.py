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
from gnuradio.filter import firdes

from fbmc_vector_reshape_vcvc import fbmc_vector_reshape_vcvc
import ofdm_swig as ofdm

class fbmc_overlapping_serial_to_parallel_cvc(gr.hier_block2):
    """
    docstring for block fbmc_overlapping_serial_to_parallel_cvc
    """
    def __init__(self, M):
        gr.hier_block2.__init__(self,
            "overlap_serial_to_parallel_cvc",
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
            gr.io_signature(1, 1, gr.sizeof_gr_complex*M),
        )

        ##################################################
        # Parameters
        ##################################################
        self.M = M

        ##################################################
        # Blocks
        ##################################################
        ##self.fbmc_vector_reshape_vcvc_1 = fbmc_vector_reshape_vcvc(M/2, M)
        ##self.fbmc_vector_reshape_vcvc_0 = fbmc_vector_reshape_vcvc(M, M/2)
        self.fbmc_vector_copy_vcvc_0 = ofdm.fbmc_vector_copy_vcvc(M/2, 2)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, M/2)
        # self.blocks_skiphead_0 = blocks.skiphead(gr.sizeof_gr_complex*M/2, 1)

        ##################################################
        # Connections
        ##################################################
        # self.connect((self.blocks_skiphead_0, 0), (self.fbmc_vector_reshape_vcvc_1, 0))
        self.connect((self, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fbmc_vector_copy_vcvc_0, 0))
        # self.connect((self.fbmc_vector_copy_vcvc_0, 0), (self, 0))
        # self.connect((self.fbmc_vector_copy_vcvc_0, 0), (self.fbmc_vector_reshape_vcvc_0, 0))
        # self.connect((self.fbmc_vector_reshape_vcvc_0, 0), (self.blocks_skiphead_0, 0))
        # self.connect((self.fbmc_vector_reshape_vcvc_0, 0), (self, 0))
        

        # self.fbmc_vector_copy_vcvc_0 = fbmc.vector_copy_vcvc(M, 2)
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, M/2)
        self.blocks_stream_to_vector_0_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*M/2, 2)
        # self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, M)
        self.blocks_skiphead_0 = blocks.skiphead(gr.sizeof_gr_complex*M/2, 1)

        # ##################################################
        # # Connections
        # ##################################################
        # self.connect((self.blocks_stream_to_vector_0, 0), (self.fbmc_vector_copy_vcvc_0, 0))
#         self.connect((self.fbmc_vector_copy_vcvc_0, 0), (self.blocks_vector_to_stream_0, 0))
#         # self.connect((self.blocks_vector_to_stream_0, 0), (self.blocks_stream_to_vector_0_0, 0))
#         self.connect((self.blocks_vector_to_stream_0, 0), (self.blocks_skiphead_0, 0))
#         self.connect((self.blocks_skiphead_0, 0), (self.blocks_stream_to_vector_0_0, 0))
#         # self.connect((self, 0), (self.blocks_stream_to_vector_0, 0))
#         self.connect((self.blocks_stream_to_vector_0_0, 0), (self, 0))
        
        self.connect((self.fbmc_vector_copy_vcvc_0, 0),(self.blocks_skiphead_0, 0))
        self.connect((self.blocks_skiphead_0, 0), (self.blocks_stream_to_vector_0_0, 0))
        # self.connect((self, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.blocks_stream_to_vector_0_0, 0), (self, 0))


# QT sink close method reimplementation

    def get_M(self):
        return self.M

    def set_M(self, M):
        self.M = M