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

class fbmc_vector_reshape_vcvc(gr.hier_block2):
    """
    docstring for block fbmc_vector_reshape_vcvc
    """
    def __init__(self, len_in, len_out):
        gr.hier_block2.__init__(self,
            "vector_reshape_vcvc",
            gr.io_signature(1, 1, gr.sizeof_gr_complex*len_in),  # Input signature
            gr.io_signature(1, 1, gr.sizeof_gr_complex*len_out)) # Output signature

        assert((int(len_in/len_out)==len_in/len_out) or (int(len_out/len_in)==len_out/len_in))
        vts = blocks.vector_to_stream(gr.sizeof_gr_complex*1,len_in)
        stv = blocks.stream_to_vector(gr.sizeof_gr_complex*1,len_out)
        self.connect((self,0),(vts,0))
        self.connect((vts,0),(stv,0))
        self.connect((stv,0),(self,0))