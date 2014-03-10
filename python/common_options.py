#!/usr/bin/env python
# 
# Copyright 2014 Institute for Theoretical Information Technology,
#                RWTH Aachen University
#                www.ti.rwth-aachen.de
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

from gnuradio import eng_notation
import preambles

def add_options(normal,expert):
    def_data_blocks_per_frame = 9
    expert.add_option("", "--data-blocks", type="int", default=def_data_blocks_per_frame,
            help="set the number of data blocks per ofdm frame [default=%default]")
    normal.add_option("", "--fft-length", type="int", default=256,
            help="set the number of FFT bins [default=%default]")
    expert.add_option("", "--subcarriers", type="int", default=200,
            help="set the number of occupied FFT bins. Default: fft window size - Pilot Subcarriers")
    expert.add_option("", "--cp-length", type="int", default=None,
            help="set the number of bits in the cyclic prefix. Default: 12.5% of fft window size")
    expert.add_option("", "--bandwidth", type="eng_float", default='1M',
            help="set total bandwidth. [default=%default]")
    expert.add_option("", "--tx-hostname", type="string", default="localhost",
            help="Set Tx hostname for zeromq")
    normal.add_option("-v", "--verbose", action="store_true", default=False)
    expert.add_option("", "--log", action="store_true", default=False,
            help="enable file logs [default=%default]")
    expert.add_option("", "--static-allocation", action="store_true", default=False,
            help="Enable static resource allocation mode [default=%default]")

    preambles.default_block_header.add_options(normal,expert)

def defaults(options):
    # default values if parameters not set
    if options.subcarriers is None:
        options.subcarriers = options.fft_length-8 #TODO: pilot subcarrier number!!
    if options.cp_length is None:
        options.cp_length = int(options.fft_length/20)

