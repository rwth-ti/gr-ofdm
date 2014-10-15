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

from gnuradio import gr, blocks, analog, zeromq
from gnuradio import eng_notation
from configparse import OptionParser
from gnuradio import filter

from station_configuration import station_configuration

from math import log10


import sys
import os

from transmit_path import transmit_path
from receive_path12 import receive_path
from ofdm import throughput_measure, vector_sampler
import common_options
from gr_tools import log_to_file, ms_to_file
from moms import moms

import fusb_options


import ofdm as ofdm
#import itpp

#from channel import time_variant_rayleigh_channel
from numpy import sqrt, sum, concatenate
import numpy

import copy

import channel

"""
You have 4 options:
1.) Normal operation, transmitter connected to usrp
2.) Sent captured file to usrp
3.) Capture transmitter stream to file
4.) Measure the transmitter's average output performance
"""

class ofdm_mrrc_benchmark (gr.top_block):
  def __init__ (self, options):
    gr.top_block.__init__(self, "ofdm_mrrc_benchmark")

    ##self._tx_freq            = options.tx_freq         # tranmitter's center frequency
    ##self._tx_subdev_spec     = options.tx_subdev_spec  # daughterboard to use
    ##self._fusb_block_size    = options.fusb_block_size # usb info for USRP
    ##self._fusb_nblocks       = options.fusb_nblocks    # usb info for USRP
    ##self._which              = options.which_usrp
    self._bandwidth          = options.bandwidth
    self.servants = []
    self._verbose            = options.verbose
    
    ##self._interface          = options.interface
    ##self._mac_addr           = options.mac_addr

    self._options = copy.copy( options )


    self._interpolation = 1
    
    f1 = numpy.array([-107,0,445,0,-1271,0,2959,0,-6107,0,11953,
                      0,-24706,0,82359,262144/2,82359,0,-24706,0,
                      11953,0,-6107,0,2959,0,-1271,0,445,0,-107],
                      numpy.float64)/262144.
    
    print "Software interpolation: %d" % (self._interpolation)

    bw = 1.0/self._interpolation
    tb = bw/5
    if self._interpolation > 1:
      self.tx_filter = gr.hier_block2("filter",
                                   gr.io_signature(1,1,gr.sizeof_gr_complex),
                                   gr.io_signature(1,1,gr.sizeof_gr_complex))
      self.tx_filter2 = gr.hier_block2("filter",
                                   gr.io_signature(1,1,gr.sizeof_gr_complex),
                                   gr.io_signature(1,1,gr.sizeof_gr_complex))
      self.tx_filter.connect( self.tx_filter, gr.interp_fir_filter_ccf(2,f1),
                           gr.interp_fir_filter_ccf(2,f1), self.tx_filter )
      self.tx_filter2.connect( self.tx_filter2, gr.interp_fir_filter_ccf(2,f1),
                           gr.interp_fir_filter_ccf(2,f1), self.tx_filter2 )
      print "New"

    else:
      self.tx_filter = None
      self.tx_filter2 = None
      
    self.decimation = 1
    
    if self.decimation > 1:
      bw = 0.5/self.decimation * 1
      tb = bw/5
      # gain, sampling rate, passband cutoff, stopband cutoff
      # passband ripple in dB, stopband attenuation in dB
      # extra taps
      filt_coeff = optfir.low_pass(1.0, 1.0, bw, bw+tb, 0.1, 60.0, 1)
      print "Software decimation filter length: %d" % (len(filt_coeff))
      self.rx_filter = gr.fir_filter_ccf(self.decimation,filt_coeff)
      self.rx_filter2 = gr.fir_filter_ccf(self.decimation,filt_coeff)
    else:
      self.rx_filter = None
      self.rx_filter2 = None
      
      
##    if not options.from_file is None:
##      # sent captured file to usrp
##      self.src = gr.file_source(gr.sizeof_gr_complex,options.from_file)
##      self._setup_usrp_sink()
##      if hasattr(self, "filter"):
##        self.connect(self.src,self.filter,self.u) #,self.filter
##      else:
##        self.connect(self.src,self.u)
##      
##      return 
    
    
    
    self._setup_tx_path(options)
    self._setup_rx_path(options)
    self._setup_rpc_manager()
    
    config = self.config = station_configuration()
    
    #self.enable_txfreq_adjust("txfreq")
    
    

    if options.imgxfer:
      self.rxpath.setup_imgtransfer_sink()
    
    if not options.no_decoding:
      self.rxpath.publish_rx_performance_measure()
      
    


    self.dst	= (self.rxpath,0)
    self.dst2 	= (self.rxpath,1)
    
    if options.force_rx_filter:
      print "Forcing rx filter usage"
      self.connect( self.rx_filter, self.dst )
      self.connect( self.rx_filter2, self.dst2 )
      self.dst = self.rx_filter
      self.dst2 = self.rx_filter2
    
    
    if options.measure:
      self.m = throughput_measure(gr.sizeof_gr_complex)
      self.m2 = throughput_measure(gr.sizeof_gr_complex)
      self.connect( self.m, self.dst )
      self.connect( self.m2, self.dst2 )
      self.dst = self.m
      self.dst2 = self.m2


    if options.snr is not None:
      if options.berm is not None:
          noise_sigma = 380/32767.0 #empirically given, gives the received SNR range of (1:28) for tx amp. range of (500:10000) which is set in rm_ber_measurement.py
          print " Noise St. Dev. %f" % (noise_sigma)#check for fading channel 
      else:
          snr_db = options.snr
          snr = 10.0**(snr_db/10.0)
          noise_sigma = sqrt( config.rms_amplitude**2 / snr )
          
      print " Noise St. Dev. %f" % (noise_sigma)
      awgn_chan = blocks.add_cc()
      awgn_chan2 = blocks.add_cc()
      awgn_noise_src = analog.fastnoise_source_c(analog.GR_GAUSSIAN, noise_sigma, 0, 8192)
      awgn_noise_src2 = analog.fastnoise_source_c(analog.GR_GAUSSIAN, noise_sigma*8, 0, 8192)
      self.connect( awgn_chan, self.dst )
      self.connect( awgn_chan2, self.dst2 )
      self.connect( awgn_noise_src, (awgn_chan,1) )
      self.connect( awgn_noise_src2, (awgn_chan2,1) )  
      self.dst = awgn_chan
      self.dst2 = awgn_chan2



    if options.freqoff is not None:
      freq_off = self.freq_off = channel.freq_offset(options.freqoff )
      freq_off2 = self.freq_off2  = channel.freq_offset(options.freqoff )
      dst = self.dst
      dst2 = self.dst2
      self.connect( freq_off, dst )
      self.connect( freq_off2, dst2 )
      self.dst = freq_off
      self.dst2 = freq_off2
      self.rpc_mgr_tx.add_interface("set_freq_offset",self.freq_off.set_freqoff)
      self.rpc_mgr_tx.add_interface("set_freq_offset2",self.freq_off2.set_freqoff)


    if options.multipath:
      if options.itu_channel:
        self.fad_chan = channel.itpp_channel(options.bandwidth)
          #fad_chan.set_norm_doppler( 1e-9 )
          #fad_chan.set_LOS( [500.,0,0] )
        self.fad_chan2 = channel.itpp_channel(options.bandwidth)
        self.fad_chan.set_channel_profile( itpp.ITU_Pedestrian_A, 5e-8 )
        self.fad_chan.set_norm_doppler( 1e-8 )
        self.fad_chan2.set_channel_profile( itpp.ITU_Pedestrian_A, 5e-8 )
        self.fad_chan2.set_norm_doppler( 1e-8 )
        self.rpc_mgr_tx.add_interface("set_channel_profile",self.fad_chan.set_channel_profile)
        self.rpc_mgr_tx.add_interface("set_channel_profile",self.fad_chan2.set_channel_profile)
      else:
        fad_chan = filter.fir_filter_ccc(1,[1.0,0.0,2e-1+0.1j,1e-4-0.04j])
        fad_chan2 = filter.fir_filter_ccc(1,[1.0,0.0,2e-1+0.1j,1e-4-0.04j])
        
      self.connect( self.fad_chan, self.dst )
      self.connect( self.fad_chan2, self.dst2 )
      self.dst = self.fad_chan
      self.dst2 = self.fad_chan2

    if options.samplingoffset is not None:
      soff = options.samplingoffset
      interp = moms(1000000*(1.0+soff),1000000)
      interp2 = moms(1000000*(1.0+soff),1000000)
      self.connect( interp, self.dst )
      self.connect( interp2, self.dst2 )
      self.dst = interp
      self.dst2 = interp2
      
      if options.record:
       log_to_file( self, interp, "data/interp_out.compl" )
       log_to_file( self, interp2, "data/interp2_out.compl" )
    
    tmm =blocks.throttle(gr.sizeof_gr_complex, 1e6)
    #tmm2 =blocks.throttle(gr.sizeof_gr_complex, 1e6)
    
    #self.connect( tmm, self.dst )
    #self.connect( tmm2, self.dst2 )
    #self.dst = tmm
    #self.dst2 = tmm2
    
    #inter = blocks.interleave(gr.sizeof_gr_complex)
    #deinter = blocks.deinterleave(gr.sizeof_gr_complex)
    
    # Interleaving input/output streams
    ##self.connect(inter, deinter)
    #self.connect((deinter,0),self.dst)
    #self.connect((deinter,1),self.dst2)
    #self.dst = inter
    #self.dst2 = (inter,1)
    
    
    if options.force_tx_filter:
      print "Forcing tx filter usage"
      self.connect( self.tx_filter, self.dst )
      self.connect( self.tx_filter2, self.dst2 )
      self.dst = self.tx_filter
      self.dst2 = self.tx_filter2
    if options.record:
      log_to_file( self, self.txpath, "data/txpath_out.compl" )
      log_to_file( self, self.txpath2, "data/txpath2_out.compl" )
      
    if options.nullsink:
        self.connect(gr.null_source(gr.sizeof_gr_complex), self.dst)
        self.connect(gr.null_source(gr.sizeof_gr_complex), self.dst2)
        self.dst = gr.null_sink(gr.sizeof_gr_complex)
        self.dst2 = gr.null_sink(gr.sizeof_gr_complex)
        
    
    self.connect( self.txpath,tmm,self.dst )
    self.connect( tmm,self.dst2 )
    #self.connect( self.txpath,self.dst2 )
    
    print "Hit Strg^C to terminate"

    if self._verbose:
        self._print_verbage()


  def _setup_tx_path(self,options):
    print "OPTIONS", options
    self.txpath = transmit_path(options)
    
  def _setup_rx_path(self,options):
    self.rxpath = receive_path(options)
    
  def _setup_rpc_manager(self):
   ## Adding rpc manager for Transmitter
    self.rpc_mgr_tx = zeromq.rpc_manager()
    self.rpc_mgr_tx.set_reply_socket("tcp://*:6660")
    self.rpc_mgr_tx.start_watcher()

    ## Adding rpc manager for Receiver
    self.rpc_mgr_rx = zeromq.rpc_manager()
    self.rpc_mgr_rx.set_reply_socket("tcp://*:5550")
    self.rpc_mgr_rx.start_watcher()

    ## Adding interfaces
    self.rpc_mgr_tx.add_interface("set_amplitude",self.txpath.set_rms_amplitude)
    self.rpc_mgr_tx.add_interface("get_tx_parameters",self.txpath.get_tx_parameters)
    self.rpc_mgr_tx.add_interface("set_modulation",self.txpath.allocation_src.set_allocation)
    self.rpc_mgr_rx.add_interface("set_scatter_subcarrier",self.rxpath.set_scatterplot_subc)
    


  def supply_rx_baseband(self):
    ## RX Spectrum
    if self.__dict__.has_key('rx_baseband'):
      return self.rx_baseband

    config = self.config

    fftlen = config.fft_length

    my_window = window.hamming(fftlen) #.blackmanharris(fftlen)
    rxs_sampler = vector_sampler(gr.sizeof_gr_complex,fftlen)
    rxs_trigger = gr.vector_source_b(concatenate([[1],[0]*199]),True)
    rxs_window = blocks.multiply_const_vcc(my_window)
    rxs_spectrum = gr.fft_vcc(fftlen,True,[],True)
    rxs_mag = gr.complex_to_mag(fftlen)
    rxs_avg = gr.single_pole_iir_filter_ff(0.01,fftlen)
    rxs_logdb = gr.nlog10_ff(20.0,fftlen,-20*log10(fftlen))
    rxs_decimate_rate = gr.keep_one_in_n(gr.sizeof_float*fftlen,50)

    t = self.u if self.filter is None else self.filter
    self.connect(rxs_trigger,(rxs_sampler,1))
    self.connect(t,rxs_sampler,rxs_window,
                 rxs_spectrum,rxs_mag,rxs_avg,rxs_logdb, rxs_decimate_rate)
    if self._options.log:
          log_to_file(self, rxs_decimate_rate, "data/supply_rx.float")
    self.rx_baseband = rxs_decimate_rate
    return rxs_decimate_rate

  def change_freqoff(self,val):
    self.set_freqoff(val[0])
    #self.set_freqoff2(val[0])


  def _print_verbage(self):
    """
    Prints information about the transmit path
    """
    print "\nTransmit Path:"

    print ""
    
    
    """
    Prints information about the receive path
    """
    print "\nReceive Path:"

    print ""

  def get_tx_parameters(self):
    return self.tx_parameters

  def add_options(normal, expert):
    """
    Adds usrp-specific options to the Options Parser
    """
    common_options.add_options(normal,expert)
    transmit_path.add_options(normal,expert)
    receive_path.add_options(normal,expert)

#    normal.add_option("-T", "--tx-subdev-spec", type="subdev", default=None,
#                      help="select USRP Tx side A or B")
    expert.add_option("", "--tx-freq", type="eng_float", default=None,
                      help="set transmit frequency to FREQ [default=%default]", metavar="FREQ")
    normal.add_option("", "--measure", action="store_true", default=False,
                      help="enable troughput measure, usrp disabled");
                      
#    normal.add_option("", "--dyn-freq", action="store_true", default=False,
#                      help="enable troughput measure, usrp disabled");

    expert.add_option("", "--snr", type="eng_float", default=None,
                      help="Simulate AWGN channel");
    expert.add_option("", "--freqoff", type="eng_float", default=None,
                      help="Simulate frequency offset [default=%default]")
    expert.add_option("", "--samplingoffset", type="eng_float", default=None,
                      help="Simulate sampling frequency offset [default=%default]")
    expert.add_option("", "--multipath", action="store_true", default=False,
                      help="Enable multipath channel")
    expert.add_option("", "--itu-channel", action="store_true", default=False,
                      help="Enable itu channel model (ported from itpp)")

    expert.add_option("", "--online-work", action="store_true", default=False,
                      help="Force the ofdm transmitter to work during file record [default=%default]")
#    normal.add_option("", "--from-file", type="string", default=None,
#                      help="Sent recorded stream with usrp")
#    normal.add_option("", "--to-file", type="string", default=None,
#                      help="Record transmitter to disk, not being sent to usrp")

    expert.add_option("", "--force-tx-filter", action="store_true", default=False,
                      help="force filter use while transmitting to file or measuring")
    
    expert.add_option("", "--force-rx-filter", action="store_true", default=False,
                      help="force filter use while transmitting to file or measuring")
    
    expert.add_option("", "--nullsink", action="store_true",
                      default=False,
                      help="Throw away samples")

    expert.add_option("", "--record", action="store_true",
                      default=False,
                      help="Record transmission stream")
    expert.add_option("", "--berm", action="store_true",
                      default=False,
                      help="BER measurement -> set fixed noise power ")
    
    expert.add_option("", "--stations", type="intx", default=1,
                      help="Mobile station count")
    
    expert.add_option("", "--sinr-est", action="store_true", default=False,
                      help="Enable SINR per subcarrier estimation [default=%default]")

    normal.add_option(
      "", "--imgxfer",
      action="store_true", default=False,
      help="Enable IMG Transfer mode")
    
    normal.add_option("", "--coding", action="store_true",
              default=False,
              help="Enable channel coding")
    normal.add_option("", "--nopunct", action="store_true",
              default=False,
              help="Disable puncturing/depuncturing")
    expert.add_option("", "--est-preamble", type="int", default=1,
                      help="the number of channel estimation preambles (1 or 2)");

  # Make a static method to call before instantiation
  add_options = staticmethod(add_options)



################################################################################
################################################################################

def main():
  parser = OptionParser(conflict_handler="resolve")
  expert_grp = parser.add_option_group("Expert")

  ofdm_mrrc_benchmark.add_options(parser, expert_grp)
  transmit_path.add_options(parser, expert_grp)
  receive_path.add_options(parser, expert_grp)
  fusb_options.add_options(expert_grp)

  parser.add_option( 
    "-c", "--cfg",
    action="store", type="string", default=None,
    help="Specifiy configuration file, default: none",
    config="false" )
  
  (options, args) = parser.parse_args()
  
  if options.cfg is not None:
    (options,args) = parser.parse_args(files=[options.cfg])
    print "Using configuration file %s" % ( options.cfg )

  benchmark = ofdm_mrrc_benchmark(options)
  runtime = benchmark

  r = gr.enable_realtime_scheduling()
  if r != gr.RT_OK:
    print "Couldn't enable realtime scheduling"
  else:
    print "Enabled realtime scheduling"

  try:
    if options.dot_graph:
      string_benchmark = runtime.dot_graph()
      filetx = os.path.expanduser('benchmark_mrrc_ofdm.dot')
      dot_file = open(filetx,'w')
      dot_file.write(string_benchmark)
      dot_file.close()
    
    runtime.run()
    #runtime.start()
    try:
      tx.txpath._control._id_source.ready()
    except:
      pass
  
  except KeyboardInterrupt:
    runtime.stop()

    runtime.wait()
    

  if options.measure:
    print "min",tx.m.get_min()
    print "max",tx.m.get_max()
    print "avg",tx.m.get_avg()

if __name__ == '__main__':
  main()
