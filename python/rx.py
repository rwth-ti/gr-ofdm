#!/usr/bin/env python

from gnuradio import gr
from gnuradio import eng_notation
from configparse import OptionParser

from gnuradio import blocks
from uhd_interface import uhd_receiver

from receive_path import receive_path

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
        self.connect(self.source, self.rxpath)

        if not options.no_decoding:
            self.rxpath.publish_rx_performance_measure()

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
