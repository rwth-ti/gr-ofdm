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

from gnuradio import analog
from gnuradio import blocks
from gnuradio import channels
from gnuradio import gr
from gnuradio.filter import firdes
from grc_gnuradio import blks2 as grc_blks2
import math

class fbmc_channel_hier_cc(gr.hier_block2):
    """
    docstring for block fbmc_channel_hier_cc
    """
    def __init__(self, channel_excluded=0, sel_taps=0, freq_offset=0, noise_excluded=0, sel_noise_type=0, SNR=20):
        gr.hier_block2.__init__(self,
            "fbmc_channel_hier_cc",
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
        )

        ##################################################
        # Parameters
        ##################################################
        self.freq_offset = freq_offset
        self.sel_noise_type = sel_noise_type
        self.sel_taps = sel_taps
        self.SNR = SNR
        self.channel_excluded = channel_excluded
        self.noise_excluded = noise_excluded

        ##################################################
        # Variables
        ##################################################
        self.taps = taps = (1)
        if sel_taps == 0:
            self.taps = taps = (0.998160541385960,0.0605566335500750,0.00290305927764350)
        elif sel_taps == 1:
            self.taps = taps = (0.748212004186014,0.317358833370450,0.572776845645705,0,0.0538952624324030,0.0874078808126807,0,0,0,0.0276407988816600,0,0,0,0.00894438719057275)
        elif sel_taps ==2:
            self.taps = taps = (0.463990169152204,0.816124099344485,0,0.292064507384192,0,0,0,0,0.146379002496595,0,0,0,0.0923589067029112,0,0,0,0,0,0,0,0,0,0,0,0,0.0582745305123628)
        
        noise_type = analog.GR_GAUSSIAN
        if sel_noise_type == 200:
            noise_type = analog.GR_UNIFORM
        elif sel_noise_type ==201:
            noise_type = analog.GR_GAUSSIAN
        elif sel_noise_type == 202:
            noise_type = analog.GR_LAPLACIAN
        elif sel_noise_type ==203:
            noise_type = analog.GR_IMPULSE

        ##################################################
        # Blocks
        ##################################################
        self.channels_channel_model_0 = channels.channel_model(
            noise_voltage=0.0,
            frequency_offset=freq_offset,
            epsilon=1.0,
            taps=taps,
            noise_seed=0,
            block_tags=False
        )
        self.blocks_null_source_0 = blocks.null_source(gr.sizeof_gr_complex*1)
        self.blocks_add_xx_0 = blocks.add_vcc(1)
        self.blks2_selector_1 = grc_blks2.selector(
            item_size=gr.sizeof_gr_complex*1,
            num_inputs=2,
            num_outputs=1,
            input_index=noise_excluded,
            output_index=0,
        )
        self.blks2_selector_0 = grc_blks2.selector(
            item_size=gr.sizeof_gr_complex*1,
            num_inputs=2,
            num_outputs=1,
            input_index=channel_excluded,
            output_index=0,
        )
        self.analog_fastnoise_source_x_0 = analog.fastnoise_source_c(noise_type, math.pow(10,-1*SNR/10), 0, 8192)

        ##################################################
        # Connections
        ##################################################
        self.connect((self, 0), (self.channels_channel_model_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self, 0))
        self.connect((self.blks2_selector_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.channels_channel_model_0, 0), (self.blks2_selector_0, 0))
        self.connect((self, 0), (self.blks2_selector_0, 1))
        self.connect((self.analog_fastnoise_source_x_0, 0), (self.blks2_selector_1, 0))
        self.connect((self.blocks_null_source_0, 0), (self.blks2_selector_1, 1))
        self.connect((self.blks2_selector_1, 0), (self.blocks_add_xx_0, 1))
