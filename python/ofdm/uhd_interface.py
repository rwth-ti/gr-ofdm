#!/usr/bin/env python
#
# Copyright 2010,2011 Free Software Foundation, Inc.
# 
# This file is part of GNU Radio
# 
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

from gnuradio import gr, uhd
from gnuradio import eng_notation
from gnuradio.eng_option import eng_option
from optparse import OptionParser

import sys
import os

def add_freq_option(parser):
    """
    Hackery that has the -f / --freq option set both tx_freq and rx_freq
    """
    def freq_callback(option, opt_str, value, parser):
        parser.values.rx_freq = value
        parser.values.tx_freq = value

    if not parser.has_option('--freq'):
        parser.add_option('-f', '--freq', type="eng_float",
                          action="callback", callback=freq_callback,
                          help="set Tx and/or Rx frequency to FREQ [default=%default]",
                          metavar="FREQ")

class uhd_interface:
    def __init__(self, istx, ismimo, args, bandwidth, freq=None, lo_offset=None,
                 gain=None, spec=None, antenna=None, clock_source=None, time_source=None):

        # check the USRP model name
        self._usrp_model = uhd.usrp_source(device_addr='', stream_args=uhd.stream_args('fc32')).get_usrp_info().get("mboard_id")
        print "Running USRP model:", self._usrp_model

        if(istx):
            if self._usrp_model == 'USRP1':
                # load special FPGA bitstream to get a flat frequency response
                UHD_IMAGES_DIR = os.environ.get("UHD_IMAGES_DIR")
                if UHD_IMAGES_DIR != None and UHD_IMAGES_DIR != "":
                    args = 'fpga=' + UHD_IMAGES_DIR + '/std_1rxhb_1txhb.rbf'
                else:
                    args = 'fpga=/usr/share/uhd/images/std_1rxhb_1txhb.rbf'
            self.u = uhd.usrp_sink(device_addr=args, stream_args=uhd.stream_args('fc32'))
        else:
            if(ismimo):
                self.u = uhd.usrp_source(device_addr=" addr0=192.168.10.2, addr1=192.168.10.3", stream_args=uhd.stream_args('fc32',channels=range(2)))
            else:
                self.u = uhd.usrp_source(device_addr=args, stream_args=uhd.stream_args('fc32'))


        #Make adjustments for USRP1 halfband filters
        if istx and self._usrp_model == 'USRP1':
            bandwidth=(bandwidth/2.0)

        # write the other parameters to member variables
        self._istx=istx
        self._args = args
        self._ant  = antenna
        self._ismimo = ismimo
        self._spec = spec
        self._gain = self.set_gain(gain)
        self._lo_offset = lo_offset
        self._freq = self.set_freq(freq, lo_offset)
        self._rate = self.set_sample_rate(bandwidth)
        self._clock_source = clock_source
        self._time_source = time_source

        # Set clock source to external.
        if(clock_source):
            print "clock_source: ", clock_source
            self.u.set_clock_source(clock_source, 0)

        if(time_source):
            print "time_source: ", time_source
            self.u.set_time_source(time_source, 0)

        # Set the subdevice spec
        if(spec):
            self.u.set_subdev_spec(spec, 0)

        # Set the antenna
        if(antenna):
            self.u.set_antenna(antenna, 0)


    def set_sample_rate(self, bandwidth):
        self.u.set_samp_rate(bandwidth)
        actual_bw = self.u.get_samp_rate()

        return actual_bw

    def get_sample_rate(self):
        return self.u.get_samp_rate()

    def set_gain(self, gain_rel=None):
        gain_range = self.u.get_gain_range()
        if gain_rel is None:
            if (self._istx and (self._usrp_model == 'B210')):
                self.u.set_gain(gain_range.stop())
                print 'Running a B210, needs high gain, set gain to', gain_range.stop()
                gain_abs=gain_range.stop()
            else:
                # if no gain was specified, use the mid-point in dB
                gain_abs = float(gain_range.start()+gain_range.stop())/2
                print "No gain specified."
                print "Setting gain to %f (from [%f, %f])" % \
                (gain_abs, gain_range.start(), gain_range.stop())
            	self.u.set_gain(gain_abs, 0)
        else:
            gain_delta = gain_range.stop() - gain_range.start()
            gain_abs_delta = gain_rel * gain_delta
            gain_abs = gain_range.start() + gain_abs_delta
            print "Gain range: ", gain_range
            print "Setting gain to %f dB " % gain_abs
            self.u.set_gain(gain_abs, 0)

        return gain_abs

    def set_freq(self, freq=None, lo_offset=None):
        if(freq is None):
            sys.stderr.write("You must specify -f FREQ or --freq FREQ\n")
            sys.exit(1)

        r = self.u.set_center_freq(uhd.tune_request(freq, lo_offset),0)
        if(self._ismimo):
            s = self.u.set_center_freq(uhd.tune_request(freq, lo_offset),1)

        if  r:
            return "FREQ", freq
        else:
            frange = self.u.get_freq_range()
            sys.stderr.write(("\nRequested frequency (%f) out or range [%f, %f]\n") % \
                                 (freq, frange.start(), frange.stop()))
            sys.exit(1)

#-------------------------------------------------------------------#
#   TRANSMITTER
#-------------------------------------------------------------------#

class uhd_transmitter(uhd_interface, gr.hier_block2):
    def __init__(self, args, bandwidth, freq=None, lo_offset=None, gain=None,
                 spec=None, antenna=None, clock_source=None, time_source=None, verbose=False):
        gr.hier_block2.__init__(self, "uhd_transmitter",
                                gr.io_signature(1,1,gr.sizeof_gr_complex),
                                gr.io_signature(0,0,0))


        # Set up the UHD interface as a transmitter
        uhd_interface.__init__(self, True, False, args, bandwidth,
                               freq, lo_offset, gain, spec, antenna, clock_source, time_source)

        self.connect(self, self.u)

        if(verbose):
            self._print_verbage()

    def add_options(parser):
        add_freq_option(parser)
        parser.add_option("-a", "--args", type="string", default="",
                          help="UHD device address args [default=%default]")
        parser.add_option("", "--spec", type="string", default=None,
                          help="Subdevice of UHD device where appropriate")
        parser.add_option("-A", "--antenna", type="string", default=None,
                          help="select Rx Antenna where appropriate")
        parser.add_option("", "--tx-freq", type="eng_float", default=None,
                          help="set transmit frequency to FREQ [default=%default]",
                          metavar="FREQ")
        parser.add_option("", "--lo-offset", type="eng_float", default=0,
                          help="set local oscillator offset in Hz (default is 0)")
        parser.add_option("", "--tx-gain", type="eng_float", default=None,
                          help="set relative transmit gain (default is midpoint)")
        parser.add_option("-C", "--clock-source", type="string", default=None,
                          help="select clock source (e.g. 'external', 'mimo') [default=%default]")
        parser.add_option("-T", "--time-source", type="string", default=None,
                          help="select time source (e.g. 'external') [default=%default]")
        parser.add_option("-v", "--verbose", action="store_true", default=False)

    # Make a static method to call before instantiation
    add_options = staticmethod(add_options)

    def _print_verbage(self):
        """
        Prints information about the UHD transmitter
        """
        print "\nUHD Transmitter:"
        print "UHD Args:     %s"    % (self._args)
        print "Freq:         %sHz"  % (eng_notation.num_to_str(self._freq))
        print "LO Offset:    %sHz"  % (eng_notation.num_to_str(self._lo_offset))
        print "Gain:         %f dB" % (self._gain)
        print "Sample Rate:  %ssps" % (eng_notation.num_to_str(self._rate))
        print "Antenna:      %s"    % (self._ant)
        print "Subdev Sec:   %s"    % (self._spec)
        print "Clock Source: %s"    % (self._clock_source)
        print "TimeSource: %s"    % (self._time_source)



#-------------------------------------------------------------------#
#   RECEIVER
#-------------------------------------------------------------------#


class uhd_receiver(uhd_interface, gr.hier_block2):
    def __init__(self, args, bandwidth, freq=None, lo_offset=None, gain=None,
                 spec=None, antenna=None, clock_source=None, time_source=None, verbose=False):
        gr.hier_block2.__init__(self, "uhd_receiver",
                                gr.io_signature(0,0,0),
                                gr.io_signature(1,1,gr.sizeof_gr_complex))

        # Set up the UHD interface as a receiver
        uhd_interface.__init__(self, False, False, args, bandwidth,
                               freq, lo_offset, gain, spec, antenna, clock_source, time_source)

        self.connect(self.u, self)

        if(verbose):
            self._print_verbage()

    def add_options(parser):
        add_freq_option(parser)
        parser.add_option("-a", "--args", type="string", default="",
                          help="UHD device address args [default=%default]")
        parser.add_option("", "--spec", type="string", default=None,
                          help="Subdevice of UHD device where appropriate")
        parser.add_option("-A", "--antenna", type="string", default=None,
                          help="select Rx Antenna where appropriate")
        parser.add_option("", "--rx-freq", type="eng_float", default=None,
                          help="set receive frequency to FREQ [default=%default]",
                          metavar="FREQ")
        parser.add_option("", "--lo-offset", type="eng_float", default=0,
                          help="set local oscillator offset in Hz (default is 0)")
        parser.add_option("", "--rx-gain", type="eng_float", default=None,
                          help="set relative receive gain (default is midpoint)")
        parser.add_option("-C", "--clock-source", type="string", default=None,
                          help="select clock source (e.g. 'external', 'mimo') [default=%default]")
        parser.add_option("-T", "--time-source", type="string", default=None,
                          help="select time source (e.g. 'external') [default=%default]")
        if not parser.has_option("--verbose"):
            parser.add_option("-v", "--verbose", action="store_true", default=False)

    # Make a static method to call before instantiation
    add_options = staticmethod(add_options)

    def _print_verbage(self):
        """
        Prints information about the UHD transmitter
        """
        print "\nUHD Receiver:"
        print "UHD Args:     %s"    % (self._args)
        print "Freq:         %sHz"  % (eng_notation.num_to_str(self._freq))
        print "LO Offset:    %sHz"  % (eng_notation.num_to_str(self._lo_offset))
        print "Gain:         %f dB" % (self._gain)
        print "Sample Rate:  %ssps" % (eng_notation.num_to_str(self._rate))
        print "Antenna:      %s"    % (self._ant)
        print "Subdev Sec:   %s"    % (self._spec)
        print "Clock Source: %s"    % (self._clock_source)
        print "Time Source: %s"    % (self._time_source)

class uhd_mimo_receiver(uhd_interface, gr.hier_block2):
    def __init__(self, args, bandwidth, freq=None, lo_offset=None, gain=None,
                 spec=None, antenna=None, clock_source=None, time_source=None, verbose=False):
        gr.hier_block2.__init__(self, "uhd_receiver",
                                gr.io_signature(0,0,0),
                                gr.io_signature2(2,2,gr.sizeof_gr_complex,gr.sizeof_gr_complex))

        # Set up the UHD interface as a receiver
        uhd_interface.__init__(self, False, True, args, bandwidth,
                               freq, lo_offset, gain, spec, antenna, clock_source, time_source)


        self.u.set_clock_source("mimo", 1)
        self.u.set_time_source("mimo", 1)
        #self.u.set_time_source("mimo", 0)
        #self.u.set_clock_source("external", 1)
        #self.u.set_time_source("external", 1)
        #self.u.set_clock_source("external", 0)
        #self.u.set_time_source("external", 0)
        #self.u.set_samp_rate(bandwidth)
        #self.u.set_center_freq(freq, 0)
        #self.u.set_center_freq(freq, 1)
        self.connect((self.u,0), (self,0))
        self.connect((self.u,1), (self,1))

        if(verbose):
            self._print_verbage()

    def add_options(parser):
        add_freq_option(parser)
        parser.add_option("-a", "--args", type="string", default="",
                          help="UHD device address args [default=%default]")
        parser.add_option("", "--spec", type="string", default=None,
                          help="Subdevice of UHD device where appropriate")
        parser.add_option("-A", "--antenna", type="string", default=None,
                          help="select Rx Antenna where appropriate")
        parser.add_option("", "--rx-freq", type="eng_float", default=None,
                          help="set receive frequency to FREQ [default=%default]",
                          metavar="FREQ")
        parser.add_option("", "--lo-offset", type="eng_float", default=0,
                          help="set local oscillator offset in Hz (default is 0)")
        parser.add_option("", "--rx-gain", type="eng_float", default=None,
                          help="set receive gain in dB (default is midpoint)")
        parser.add_option("-C", "--clock-source", type="string", default=None,
                          help="select clock source (e.g. 'external', 'mimo') [default=%default]")
        parser.add_option("-T", "--time-source", type="string", default=None,
                          help="select time source (e.g. 'external') [default=%default]")
        if not parser.has_option("--verbose"):
            parser.add_option("-v", "--verbose", action="store_true", default=False)

    # Make a static method to call before instantiation
    add_options = staticmethod(add_options)

    def _print_verbage(self):
        """
        Prints information about the UHD transmitter
        """
        print "\nUHD Receiver:"
        print "UHD Args:     %s"    % (self._args)
        print "Freq:         %sHz"  % (eng_notation.num_to_str(self._freq))
        print "LO Offset:    %sHz"  % (eng_notation.num_to_str(self._lo_offset))
        print "Gain:         %f dB" % (self._gain)
        print "Sample Rate:  %ssps" % (eng_notation.num_to_str(self._rate))
        print "Antenna:      %s"    % (self._ant)
        print "Subdev Sec:   %s"    % (self._spec)
        print "Clock Source: %s"    % (self._clock_source)
        print "Time Source: %s"    % (self._time_source)
