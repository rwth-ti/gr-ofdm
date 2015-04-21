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
from gnuradio import digital

from gnuradio.filter import firdes
from ofdm import add_vcc
import math

class fbmc_overlapping_parallel_to_serial_vcc(gr.hier_block2):
    """
    docstring for block fbmc_overlapping_parallel_to_serial_vcc
    """
    def __init__(self, M):
        gr.hier_block2.__init__(self,
            "overlapping_parallel_to_serial_vcc",
            gr.io_signature(2, 2, gr.sizeof_gr_complex*M),  # Input signature
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1)) # Output signature

        # Variables
        self.M = M

        # Assertions
        assert (M>0 and int(math.log(M,2))==math.log(M,2)), "M should be of 2^n!"

        # Blocks
        self.vector_to_stream0 = blocks.vector_to_stream(gr.sizeof_gr_complex*M/2, 2)
        self.vector_to_stream1 = blocks.vector_to_stream(gr.sizeof_gr_complex*M/2, 2)
        self.delay = blocks.delay(gr.sizeof_gr_complex*M/2, 1)
        self.adder = blocks.add_vcc(M/2)

        # Connections
        self.connect((self,0),self.vector_to_stream0)
        self.connect((self,1),self.vector_to_stream1)
        self.connect(self.vector_to_stream0, (self.adder,0))
        self.connect(self.vector_to_stream1, self.delay)
        self.connect(self.delay, (self.adder,1))
        self.connect((self.adder,0), blocks.vector_to_stream(gr.sizeof_gr_complex, M/2),(self,0))

    def get_M(self):
        return self.M
    def set_M(self, M):
        self.M = M
        self.blocks_delay_0.set_dly(self.M/2)
