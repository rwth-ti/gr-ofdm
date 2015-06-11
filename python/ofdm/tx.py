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

from gnuradio import gr, filter, zeromq
from gnuradio import eng_notation
from configparse import OptionParser

from gnuradio import blocks
from uhd_interface import uhd_transmitter

from transmit_path import transmit_path
from fbmc_transmit_path import transmit_path as fbmc_transmit_path

import os

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
            self.file = blocks.file_sink(gr.sizeof_gr_complex, options.to_file)
            self.sink = blocks.throttle(gr.sizeof_gr_complex,1e6)
            self.connect( self.sink, self.file )
        else:
            self.sink = blocks.null_sink(gr.sizeof_gr_complex)
            
            



        self._setup_tx_path(options)
        self._setup_rpc_manager()

        if options.freqoff is not None:
            freq_off = self.freq_off = channel.freq_offset(options.freqoff )
            self.connect(self.txpath, freq_off)
            self.txpath = freq_off
            self.rpc_mgr_tx.add_interface("set_freq_offset",self.freq_off.set_freqoff)

        if options.multipath:
          if options.itu_channel:
            self.fad_chan = channel.itpp_channel(options.bandwidth)
            self.rpc_mgr_tx.add_interface("set_channel_profile",self.fad_chan.set_channel_profile)
          else:
            self.fad_chan = filter.fir_filter_ccc(1,[1.0,0.0,2e-1+0.1j,1e-4-0.04j])

          self.connect(self.txpath, self.fad_chan)
          self.txpath = self.fad_chan


        self.connect(self.txpath, self.sink)


    def _setup_tx_path(self,options):
        print "OPTIONS", options
        if options.fbmc:
            print "fbmc_transmit_path"
            self.txpath = fbmc_transmit_path(options)
        else:
            self.txpath = transmit_path(options)

    def set_tx_gain(self, gain):
        return self.sink.set_gain(gain)

    def _setup_rpc_manager(self):
      ## Adding rpc manager for Transmitter
        self.rpc_mgr_tx = zeromq.rpc_manager()
        self.rpc_mgr_tx.set_reply_socket("tcp://*:6660")
        self.rpc_mgr_tx.start_watcher()

       ## Adding interfaces
        self.rpc_mgr_tx.add_interface("set_amplitude",self.txpath.set_rms_amplitude)
        self.rpc_mgr_tx.add_interface("get_tx_parameters",self.txpath.get_tx_parameters)
        self.rpc_mgr_tx.add_interface("set_modulation",self.txpath.allocation_src.set_allocation)
        self.rpc_mgr_tx.add_interface("set_tx_gain",self.set_tx_gain)

    def add_options(parser):
        parser.add_option("-c", "--cfg", action="store", type="string", default=None,
                          help="Specifiy configuration file, default: none")
        parser.add_option("","--to-file", default=None,
                          help="Output file for modulated samples")
        parser.add_option("", "--multipath", action="store_true", default=False,
                          help="Enable multipath channel")
        parser.add_option('', '--fbmc', action='store_true', default=False,
                      help='Enable FBMC')
        parser.add_option("", "--to-file", type="string", default=None,
                      help="Record transmitter to disk, not being sent to usrp")

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

    if options.dot_graph:
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
