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

from gnuradio import gr
from gnuradio import eng_notation
from gnuradio import zeromq
from configparse import OptionParser

from gnuradio import blocks
from uhd_interface import uhd_receiver

from receive_path import receive_path
from gr_tools import log_to_file

import os


class rx_top_block(gr.top_block):
    def __init__(self, options):
        gr.top_block.__init__(self)

        if(options.rx_freq is not None):
            self.source = uhd_receiver(options.args,
                                       options.bandwidth, options.rx_freq, 
                                       options.lo_offset, options.rx_gain,
                                       options.spec, options.antenna,
                                       options.clock_source, options.verbose)
        elif(options.from_file is not None):
            self.source = blocks.file_source(gr.sizeof_gr_complex, options.from_file)
        else:
            self.source = blocks.null_source(gr.sizeof_gr_complex)

        self.rxpath = receive_path(options)
        self._setup_rpc_manager()

        self.connect(self.source, self.rxpath)
  
        if options.scatterplot:
          print "Scatterplot enabled"

    def _setup_rpc_manager(self):
      ## Adding rpc manager for Receiver
      self.rpc_mgr_rx = zeromq.rpc_manager()
      self.rpc_mgr_rx.set_reply_socket("tcp://*:5550")
      self.rpc_mgr_rx.start_watcher()

      ## Adding interfaces
      self.rpc_mgr_rx.add_interface("set_scatter_subcarrier",self.rxpath.set_scatterplot_subc)
      self.rpc_mgr_rx.add_interface("set_snr_subcarrier",self.rxpath.set_snr_subc)

    def add_options(parser):
        parser.add_option("-c", "--cfg", action="store", type="string", default=None,
                          help="Specifiy configuration file, default: none")
        parser.add_option("","--from-file", default=None,
                          help="input file of samples to demod")

    # Make a static method to call before instantiation
    add_options = staticmethod(add_options)

def main():
    parser = OptionParser(conflict_handler="resolve")
    expert_grp = parser.add_option_group("Expert")
    rx_top_block.add_options(parser)
    receive_path.add_options(parser, expert_grp)
    uhd_receiver.add_options(parser)
    (options, args) = parser.parse_args()
    if options.cfg is not None:
        (options,args) = parser.parse_args(files=[options.cfg])
        print "Using configuration file %s" % ( options.cfg )

    tb = rx_top_block(options)

    if options.dot_graph:
        # write a dot graph of the flowgraph to file
        dot_str = tb.dot_graph()
        file_str = os.path.expanduser('rx_ofdm.dot')
        dot_file = open(file_str,'w')
        dot_file.write(dot_str)
        dot_file.close()

    try:
        tb.run()
    except [[KeyboardInterrupt]]:
        pass


if __name__ == '__main__':
    main()
