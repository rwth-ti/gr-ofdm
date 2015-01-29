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

import ofdm

class fbmc_receiver_multiuser_cb(gr.hier_block2):
    """
    docstring for block fbmc_receiver_multiuser_cb
    """
    def __init__(self, M=1024, K=4, qam_size=16, syms_per_frame=10, boundaries=[], theta_sel=0, sel_eq=0, exclude_preamble=0, sel_preamble=0, zero_pads=1, extra_pad=False):
        output_signature = list()
        for i in range(len(boundaries)/2):
            output_signature.append(gr.sizeof_gr_complex*(boundaries[2*i+1]-boundaries[2*i]+1))

        # print(output_signature)
        gr.hier_block2.__init__(self,
            "fbmc_receiver_multiuser_cb",
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),  # Input signature
            gr.io_signaturev(len(boundaries)/2, len(boundaries)/2, output_signature)) # Output signature
            # gr.io_signaturev(len(boundaries)/2, len(boundaries)/2, [gr.sizeof_gr_complex*26,gr.sizeof_gr_complex*26,gr.sizeof_gr_complex*26,gr.sizeof_gr_complex*36])) # Output signature
        # print([gr.sizeof_gr_complex*26,gr.sizeof_gr_complex*26,gr.sizeof_gr_complex*26,gr.sizeof_gr_complex*36])

        # blocks
        self.ofdm_fbmc_receiver_demo_0 = ofdm.fbmc_receiver_demo(M, K, qam_size, syms_per_frame, M, theta_sel, sel_eq, exclude_preamble, sel_preamble, zero_pads, extra_pad)
        asymms = list()
        for i in range(len(boundaries)/2):
            asymms.append(ofdm.fbmc_asymmetrical_vector_mask_vcvc(M,boundaries[2*i],boundaries[2*i+1]))
            # print(str(i))

        # connections
        self.connect((self, 0), (self.ofdm_fbmc_receiver_demo_0, 0))
        for i in range(len(boundaries)/2):
            self.connect((self.ofdm_fbmc_receiver_demo_0, 0), (asymms[i], 0))
            self.connect((asymms[i], 0),(self,i))
            # print(str(i))







        # Parameters

        # self.M = M
        # self.K = K
        # self.qam_size = qam_size
        # self.syms_per_frame = syms_per_frame
        # self.boundaries = boundaries
        # self.theta_sel = theta_sel
        # self.sel_eq = sel_eq
        # self.exclude_preamble = exclude_preamble
        # self.sel_preamble= sel_preamble
        # self.zero_pads= zero_pads
        # self.extra_pad= extra_pad

        # # Blocks

        # self.fbmc_receiver_demo_0 = ofdm.fbmc_receiver_demo(M=M, K=K, qam_size=qam_size, syms_per_frame=syms_per_frame, carriers=M, theta_sel=theta_sel, sel_eq=sel_eq, exclude_preamble=exclude_preamble, sel_preamble=sel_preamble, zero_pads=1, extra_pad=False)
        # self.list_asymmetrical
