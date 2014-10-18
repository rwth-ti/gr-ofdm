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
from uhd_interface import uhd_mimo_receiver

from receive_path import receive_path as receive_path
from receive_path12 import receive_path as receive_path_12
from gr_tools import log_to_file

import os


class rx_top_block(gr.top_block):
    def __init__(self, options):
        gr.top_block.__init__(self)

        if(options.rx_freq is not None):
            if options.rx_ant == 1:
                self.source = uhd_receiver(options.args,
                                       options.bandwidth, options.rx_freq, 
                                       options.lo_offset, options.rx_gain,
                                       options.spec, options.antenna,
                                       options.clock_source, options.time_source,options.verbose)
            else:
                self.source = uhd_mimo_receiver(options.args,
                                       options.bandwidth, options.rx_freq, 
                                       options.lo_offset, options.rx_gain,
                                       options.spec, options.antenna,
                                       options.clock_source, options.time_source, options.verbose)
        elif(options.from_file is not None):
            self.source = blocks.file_source(gr.sizeof_gr_complex, options.from_file)
        else:
            self.source = blocks.null_source(gr.sizeof_gr_complex)
        '''
        if options.tx_ant == 1:
            if options.rx_ant == 1:
                self.rxpath = receive_path(options)
                self._setup_rpc_manager()
                self.connect(self.source, self.rxpath)
            else:
                self.rxpath = receive_path_12(options)
                self._setup_rpc_manager()
                self.connect(self.source, self.rxpath)
                self.connect((self.source,1), (self.rxpath,1)) 
                '''
        self._setup_rx_path(options)        
        self._setup_rpc_manager()
        self.dst    = (self.rxpath,0)

        #self.dst2     = (self.rxpath,1)
        self.connect((self.source,0), self.dst)
        #self.connect((self.source,1), blocks.null_sink(gr.sizeof_gr_complex))     
        #self.connect((self.source,1), self.dst2)        
                
        #self._setup_rpc_manager()

        #self.connect(self.source, self.rxpath)
  
        if options.scatterplot:
          print "Scatterplot enabled"
    
    def set_rx_gain(self, gain):
        self.source.set_gain(gain)      

    def _setup_rpc_manager(self):
      ## Adding rpc manager for Receiver
      self.rpc_mgr_rx = zeromq.rpc_manager()
      self.rpc_mgr_rx.set_reply_socket("tcp://*:5550")
      self.rpc_mgr_rx.start_watcher()

      ## Adding interfaces
      self.rpc_mgr_rx.add_interface("set_scatter_subcarrier",self.rxpath.set_scatterplot_subc)
      self.rpc_mgr_rx.add_interface("set_rx_gain",self.set_rx_gain)
      
      
    def _setup_rx_path(self,options):
        if options.tx_ant == 1:
            if options.rx_ant == 1:
                self.rxpath = receive_path(options)
                #self._setup_rpc_manager()
                #self.connect(self.source, self.rxpath)
            else:
                print "1X21X21X21X2"
                self.rxpath = receive_path_12(options)
                #self._setup_rpc_manager()
                #self.connect(self.source, self.rxpath)
                #self.connect((self.source,1), (self.rxpath,1)) 

    def add_options(parser):
        parser.add_option("-c", "--cfg", action="store", type="string", default=None,
                          help="Specifiy configuration file, default: none")
        parser.add_option("","--from-file", default=None,
                          help="input file of samples to demod")
        parser.add_option("", "--tx-ant", type="int", default=1,
                      help="the number of transmit antennas")
        parser.add_option("", "--rx-ant", type="int", default=1,
                      help="the number of receive antennas")

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
