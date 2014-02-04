#!/usr/bin/env python

from gnuradio import gr
from gnuradio import eng_notation
from configparse import OptionParser

from gnuradio import blocks
from uhd_interface import uhd_transmitter

from transmit_path import transmit_path

import os
import zmqblocks

import channel

class tx_top_block(gr.top_block):
    def __init__(self, options):
        gr.top_block.__init__(self)

        if(options.tx_freq is not None):
            self.sink = uhd_transmitter(options.args,
                                        options.bandwidth, options.tx_freq, 
                                        options.lo_offset, options.tx_gain,
                                        options.spec, options.antenna,
                                        options.clock_source, options.verbose)
        elif(options.to_file is not None):
            self.sink = blocks.file_sink(gr.sizeof_gr_complex, options.to_file)
        else:
            self.sink = blocks.null_sink(gr.sizeof_gr_complex)

        self._setup_tx_path(options)
        self._setup_rpc_manager()

        if options.freqoff is not None:
            freq_off = self.freq_off = channel.freq_offset(options.freqoff )
            self.connect(self.txpath, freq_off) 
            self.txpath = freq_off
            self.rpc_mgr_tx.add_interface("set_freq_offset",self.freq_off.set_freqoff)


        self.connect(self.txpath, self.sink)


    def _setup_tx_path(self,options):
        print "OPTIONS", options
        self.txpath = transmit_path(options)

    def _setup_rpc_manager(self):
      ## Adding rpc manager for Transmitter
        self.rpc_mgr_tx = zmqblocks.rpc_manager()
        self.rpc_mgr_tx.set_reply_socket("tcp://*:6660")
        self.rpc_mgr_tx.start_watcher()

       ## Adding interfaces
        self.rpc_mgr_tx.add_interface("set_amplitude",self.txpath.set_rms_amplitude)
        self.rpc_mgr_tx.add_interface("get_tx_parameters",self.txpath.get_tx_parameters)
        self.rpc_mgr_tx.add_interface("set_modulation",self.txpath.allocation_src.set_allocation) 

    def add_options(parser):
        parser.add_option("-c", "--cfg", action="store", type="string", default=None,
                          help="Specifiy configuration file, default: none")
        parser.add_option("","--to-file", default=None,
                          help="Output file for modulated samples")

    # Make a static method to call before instantiation
    add_options = staticmethod(add_options)


def main():
    parser = OptionParser(conflict_handler="resolve")
    expert_grp = parser.add_option_group("Expert")
    tx_top_block.add_options(parser)
    transmit_path.add_options(parser, expert_grp)
    uhd_transmitter.add_options(parser)
    (options, args) = parser.parse_args()
    if options.cfg is not None:
        (options,args) = parser.parse_args(files=[options.cfg])
        print "Using configuration file %s" % ( options.cfg )

    tb = tx_top_block(options)

    # write a dot graph of the flowgraph to file
    dot_str = tb.dot_graph()
    file_str = os.path.expanduser('tx_ofdm.dot')
    dot_file = open(file_str,'w')
    dot_file.write(dot_str)
    dot_file.close()

    try:
        tb.run()
    except [[KeyboardInterrupt]]:
        pass


if __name__ == '__main__':
    main()
