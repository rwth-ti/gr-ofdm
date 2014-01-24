#!/usr/bin/env python

from gnuradio import eng_notation
import preambles

def add_options(normal,expert):
    def_data_blocks_per_frame = 9
    expert.add_option("", "--data-blocks", type="int", default=def_data_blocks_per_frame,
            help="set the number of data blocks per ofdm frame [default=%default]")
    normal.add_option("", "--fft-length", type="int", default=512,
            help="set the number of FFT bins [default=%default]")
    expert.add_option("", "--subcarriers", type="int", default=None,
            help="set the number of occupied FFT bins. Default: fft window size - Pilot Subcarriers")
    expert.add_option("", "--cp-length", type="int", default=None,
            help="set the number of bits in the cyclic prefix. Default: 12.5% of fft window size")
    expert.add_option("", "--bandwidth", type="eng_float", default='500k',
            help="set total bandwidth. [default=%default]")
    expert.add_option("", "--tx-hostname", type="string", default="localhost",
            help="Set Tx hostname for zeromq")
    expert.add_option("", "--rx-hostname", type="string", default="localhost",
            help="Set Rx hostname for zeromq")
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

