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
        # for now, following assumption should be made:
        # each user should be allocated with same number of subchannels.
        lb = len(boundaries)

        assert(lb>0), "The array that defines user boundaries cannot be passed as empty."
        assert(lb%2 == 0), "Unbalanced boundary definition."

        allocated = list()
        for i in range(1,(lb/2)+1):
            allocated.append(boundaries[2*i-1]-boundaries[2*i-2]+1)
            if i>=2:
                assert(allocated[i-2] == allocated[i-1]), "Each user should be allocated with same number of subchannels."

        output_signature = list()
        for i in range(lb/2):
            output_signature.append(gr.sizeof_gr_complex*(boundaries[2*i+1]-boundaries[2*i]+1))

        # print(output_signature)
        gr.hier_block2.__init__(self,
            "fbmc_receiver_multiuser_cb",
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),  # Input signature
            gr.io_signature(lb/2, lb/2, gr.sizeof_char*1)) # Output signature
            # gr.io_signaturev(lb/2, lb/2, output_signature)) # Output signature
            # gr.io_signaturev(lb/2, lb/2, [gr.sizeof_gr_complex*26,gr.sizeof_gr_complex*26,gr.sizeof_gr_complex*26,gr.sizeof_gr_complex*36])) # Output signature
        # print([gr.sizeof_gr_complex*26,gr.sizeof_gr_complex*26,gr.sizeof_gr_complex*26,gr.sizeof_gr_complex*36])

        # blocks
        self.ofdm_fbmc_receiver_demo_0 = ofdm.fbmc_receiver_demo(M, K, qam_size, syms_per_frame, M, theta_sel, sel_eq, exclude_preamble, sel_preamble, zero_pads, extra_pad)
        asymms = list()
        for i in range(lb/2):
            asymms.append(ofdm.fbmc_asymmetrical_vector_mask_vcvc(M,boundaries[2*i],boundaries[2*i+1]))
            # print(str(i))

        sym_est = list()
        for i in range(lb/2):
            sym_est.append(ofdm.fbmc_symbol_estimation_vcb(allocated[i], qam_size))

        # connections
        self.connect((self, 0), (self.ofdm_fbmc_receiver_demo_0, 0))
        for i in range(lb/2):
            self.connect((self.ofdm_fbmc_receiver_demo_0, 0), (asymms[i], 0))
            self.connect((asymms[i], 0),(sym_est[i], 0))
            self.connect((sym_est[i], 0),(self,i))