#!/usr/bin/env python
#
# Copyright 2004 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
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

from gnuradio import gr, blks2, optfir
from gnuradio import eng_notation
from configparse import OptionParser
from gnuradio import optfir

from station_configuration import station_configuration

from math import log10
from corba_servants import corba_data_buffer_servant
from corba_servants import *


import sys

from transmit_path2 import transmit_path
from receive_path21 import receive_path
from ofdm import throughput_measure, vector_sampler, corba_rxbaseband_sink
from common_options import common_tx_rx_usrp_options
from gr_tools import log_to_file, ms_to_file
from moms import moms

import fusb_options

from omniORB import CORBA, PortableServer
import CosNaming
from corba_stubs import ofdm_ti,ofdm_ti__POA
from corba_servants import general_corba_servant
from corba_servants import corba_data_buffer_servant,corba_push_vector_f_servant

import ofdm as ofdm
#import itpp

#from channel import time_variant_rayleigh_channel
from numpy import sqrt, sum, concatenate
import numpy

import copy

"""
You have 4 options:
1.) Normal operation, transmitter connected to usrp
2.) Sent captured file to usrp
3.) Capture transmitter stream to file
4.) Measure the transmitter's average output performance
"""

class ofdm_benchmark (gr.top_block):
  def __init__ (self, options):
    gr.top_block.__init__(self, "ofdm_benchmark")

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
    
    config = station_configuration()
    
    self.enable_info_tx("info_tx", "pa_user")
#    if not options.no_cheat:
#      self.txpath.enable_channel_cheating("channelcheat")
    self.txpath.enable_txpower_adjust("txpower")
    self.txpath.publish_txpower("txpower_info")
    
    if options.disable_equalization or options.ideal:
        #print "CHANGE set_k"
        self.rxpath.enable_estim_power_adjust("estim_power")
        #self.rxpath.publish_estim_power("txpower_info")
         
    #self.enable_txfreq_adjust("txfreq")
    
    

    if options.imgxfer:
      self.rxpath.setup_imgtransfer_sink()
    
    if not options.no_decoding:
      self.rxpath.publish_rx_performance_measure()
      
    


    self.dst	= (self.rxpath,0)
    
    if options.force_rx_filter:
      print "Forcing rx filter usage"
      self.connect( self.rx_filter, self.dst )
      self.dst = self.rx_filter
    
    
    if options.measure:
      self.m = throughput_measure(gr.sizeof_gr_complex)
      self.connect( self.m, self.dst )
      self.dst = self.m


    if options.snr is not None:
      if options.berm is not False:
          noise_sigma = 380 #empirically given, gives the received SNR range of (1:28) for tx amp. range of (500:10000) which is set in rm_ber_measurement.py
          #check for fading channel 
      else:
          snr_db = options.snr
          snr = 10.0**(snr_db/10.0)
          noise_sigma = sqrt( config.rms_amplitude**2 / snr )
          
      print " Noise St. Dev. %d" % (noise_sigma)
      awgn_chan = gr.add_cc()
      awgn_noise_src = ofdm.complex_white_noise( 0.0, noise_sigma )
      self.connect( awgn_chan, self.dst )
      self.connect( awgn_noise_src, (awgn_chan,1) )
      self.dst = awgn_chan



    if options.freqoff is not None:
      freq_shift = gr.multiply_cc()
      norm_freq = options.freqoff / config.fft_length
      freq_off_src = gr.sig_source_c(1.0, gr.GR_SIN_WAVE, norm_freq, 1.0, 0.0 )
      self.connect( freq_off_src, ( freq_shift, 1 ) )
      dst = self.dst
      self.connect( freq_shift, dst )
      self.dst = freq_shift


    if options.multipath:
      if options.itu_channel:
        fad_chan = itpp.tdl_channel(  ) #[0, -7, -20], [0, 2, 6]
          #fad_chan.set_norm_doppler( 1e-9 )
          #fad_chan.set_LOS( [500.,0,0] )
        fad_chan.set_channel_profile( itpp.ITU_Pedestrian_A, 5e-8 )
        fad_chan.set_norm_doppler( 1e-8 )
      else:
        fad_chan = gr.fir_filter_ccc(1,[1.0,0.0,2e-1+0.1j,1e-4-0.04j])
        
      self.connect( fad_chan, self.dst )
      self.dst = fad_chan

    if options.samplingoffset is not None:
      soff = options.samplingoffset
      interp = moms(1000000+soff,1000000)

      self.connect( interp, self.dst )
      self.dst = interp
      
      if options.record:
       log_to_file( self, interp, "data/interp_out.compl" )
    
    tmm =gr.throttle(gr.sizeof_gr_complex,self._bandwidth)
    tmm2 =gr.throttle(gr.sizeof_gr_complex,self._bandwidth)
    tmm_add = gr.add_cc()

    self.connect( tmm, tmm_add )
    self.connect( tmm2, (tmm_add,1) )

    self.connect( tmm_add, self.dst )

    self.dst = tmm
    self.dst2 = tmm2
   
    
    inter = gr.interleave(gr.sizeof_gr_complex)
    deinter = gr.deinterleave(gr.sizeof_gr_complex)
    
    self.connect(inter, deinter)
    self.connect((deinter,0),self.dst)
    self.connect((deinter,1),self.dst2)
    self.dst = inter
    self.dst2 = (inter,1)
    
    
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
        
    
    self.connect( self.txpath,self.dst )
    self.connect( (self.txpath,1),self.dst2 )
    #log_to_file( self, self.txpath, "data/txpath_out.compl" )
    #log_to_file( self, self.txpath,1), "data/txpath2_out.compl" )
    
    
    if options.cheat:
      self.txpath.enable_channel_cheating("channelcheat")

    
      
    print "Hit Strg^C to terminate"

    if options.event_rxbaseband:
      self.publish_rx_baseband_measure()
      
      
    if options.with_old_gui:
      self.publish_spectrum(256)
      self.rxpath.publish_ctf("ctf_display")
      self.rxpath.publish_ber_measurement(["ber"])
      self.rxpath.publish_average_snr(["totalsnr"])
      if options.sinr_est:
        self.rxpath.publish_sinrsc("sinrsc_display")
      

    
    print "Hit Strg^C to terminate"


    # Display some information about the setup
    if self._verbose:
        self._print_verbage()

#    if not options.to_file is None:
#      log_to_file(self, self.txpath, options.to_file)
#      log_to_file(self, self.filter, "data/tx_filter.compl")
#      log_to_file(self, self.filter, "data/tx_filter.float",mag=True)
#      ms_to_file(self, self.filter, "data/tx_filter_power.float")

  def publish_spectrum(self,fftlen):
    spectrum = gr.fft_vcc(fftlen,True,[],True)
    mag = gr.complex_to_mag(fftlen)
    logdb = gr.nlog10_ff(20.0,fftlen,-20*log10(fftlen))
    decimate_rate = gr.keep_one_in_n(gr.sizeof_gr_complex*fftlen,10)

    msgq = gr.msg_queue(10)
    msg_sink = gr.message_sink(gr.sizeof_float*fftlen,msgq,True)

    self.connect(self.filter,gr.stream_to_vector(gr.sizeof_gr_complex,fftlen),
                 decimate_rate,spectrum,mag,logdb,msg_sink)

    self.servants.append(corba_data_buffer_servant("tx_spectrum",fftlen,msgq))


  def _setup_tx_path(self,options):
    self.txpath = transmit_path(options)
    
    for i in range( options.stations ):
      print "Registering mobile station with ID %d" % ( i+1 )
      self.txpath.add_mobile_station( i+1 )
    
  def _setup_rx_path(self,options):
    self.rxpath = receive_path(options)  
    
    
  def publish_rx_baseband_measure(self):
    config = self.config
    vlen = config.fft_length
    self.rx_baseband_sink = rx_sink = corba_rxbaseband_sink("alps",config.ns_ip,
                                    config.ns_port,vlen,config.rx_station_id)

      # 1. frame id
      #self.connect(self.rxpath._id_decoder,(rx_sink,0))

      # 2. channel transfer function
    rx_bband = self.supply_rx_baseband()
    print "Supplied"
    self.connect( rx_bband, (rx_sink,0) )


  def supply_rx_baseband(self):
    ## RX Spectrum
    if self.__dict__.has_key('rx_baseband'):
      return self.rx_baseband

    config = self.config

    fftlen = config.fft_length

    my_window = window.hamming(fftlen) #.blackmanharris(fftlen)
    rxs_sampler = vector_sampler(gr.sizeof_gr_complex,fftlen)
    rxs_trigger = gr.vector_source_b(concatenate([[1],[0]*199]),True)
    rxs_window = gr.multiply_const_vcc(my_window)
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


  def publish_rx_spectrum(self,fftlen):
    ## RX Spectrum

    fftlen = 256
    my_window = window.hamming(fftlen) #.blackmanharris(fftlen)
    rxs_sampler = vector_sampler(gr.sizeof_gr_complex,fftlen)
    rxs_trigger = gr.vector_source_b(concatenate([[1],[0]*199]),True)
    rxs_window = gr.multiply_const_vcc(my_window)
    rxs_spectrum = gr.fft_vcc(fftlen,True,[],True)
    rxs_mag = gr.complex_to_mag(fftlen)
    rxs_avg = gr.single_pole_iir_filter_ff(0.01,fftlen)
    rxs_logdb = gr.nlog10_ff(20.0,fftlen,-20*log10(fftlen))
    rxs_decimate_rate = gr.keep_one_in_n(gr.sizeof_float*fftlen,1)
    msgq = gr.msg_queue(5)
    rxs_msg_sink = gr.message_sink(gr.sizeof_float*fftlen,msgq,True)
    self.connect(rxs_trigger,(rxs_sampler,1))
    t = self.u if self.filter is None else self.filter
    self.connect(t,rxs_sampler,rxs_window,
                 rxs_spectrum,rxs_mag,rxs_avg,rxs_logdb, rxs_decimate_rate,
                 rxs_msg_sink)
    self.servants.append(corba_data_buffer_servant("spectrum",fftlen,msgq))

    print "RXS trigger unique id", rxs_trigger.unique_id()
    
    print "Publishing RX baseband under id: spectrum"

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

  def enable_info_tx(self,unique_id,userid):
    """
    create servant for info_tx interface and give him our specifications.
    only fixed data should go here!
    """

    config = station_configuration()
    carrier_freq = 0.0
    bandwidth = self._bandwidth or 2e6
    if config.coding:
        bits = 6*config.data_subcarriers*config.frame_data_blocks # max. QAM256
    else:
        bits = 8*config.data_subcarriers*config.frame_data_blocks # max. QAM256
    samples_per_frame = config.frame_length*config.block_length
    tb = samples_per_frame/bandwidth
    infotx = info_tx_i(subcarriers= config.data_subcarriers,
                       fft_window=config.fft_length,
                       cp_length=config.cp_length,
                       carrier_freq=carrier_freq,
                       symbol_time=config.block_length/bandwidth,
                       bandwidth=bandwidth,
                       subbandwidth=bandwidth/config.fft_length,
                       max_datarate=(bits/tb),
                       burst_length=config.frame_length
                       )
    self.servants.append(general_corba_servant(str(unique_id),infotx))
    
    print "Enabled info_tx, id: %s" % (unique_id)

  def add_options(normal, expert):
    """
    Adds usrp-specific options to the Options Parser
    """
    common_tx_rx_usrp_options(normal,expert)
    transmit_path.add_options(normal,expert)
    receive_path.add_options(normal,expert)

#    normal.add_option("-T", "--tx-subdev-spec", type="subdev", default=None,
#                      help="select USRP Tx side A or B")
#    expert.add_option("", "--tx-freq", type="eng_float", default=None,
#                      help="set transmit frequency to FREQ [default=%default]", metavar="FREQ")
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
      "", "--event-rxbaseband",
      action="store_true", default=False,
      help = "Enable RX baseband via event channel alps" )
    normal.add_option("", "--with-old-gui", action="store_true", default=False,
                      help="Turn of CORBA interfaces to support old GUI")

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

"""
CORBA servant implementation of info_tx interface
"""
class info_tx_i(ofdm_ti__POA.info_tx):
  def __init__(self,**kwargs):
    self.subcarriers = kwargs['subcarriers']
    self.fft_window = kwargs['fft_window']
    self.cp_length = kwargs['cp_length']
    self.carrier_freq = kwargs['carrier_freq']
    self.symbol_time = kwargs['symbol_time']
    self.bandwidth = kwargs['bandwidth']
    self.subbandwidth = kwargs['subbandwidth']
    self.max_datarate = kwargs['max_datarate']
    self.burst_length = kwargs['burst_length']

  def _get_subcarriers(self):
    return self.subcarriers

  def _get_fft_window(self):
    return self.fft_window

  def _get_cp_length(self):
    return self.cp_length

  def _get_carrier_freq(self):
    return float(self.carrier_freq)

  def _get_symbol_time(self):
    return self.symbol_time

  def _get_bandwidth(self):
    return self.bandwidth

  def _get_subbandwidth(self):
    return self.subbandwidth

  def _get_max_datarate(self):
    return int(self.max_datarate)

  def _get_burst_length(self):
    return self.burst_length

################################################################################
################################################################################

def main():
  parser = OptionParser(conflict_handler="resolve")
  expert_grp = parser.add_option_group("Expert")

  ofdm_benchmark.add_options(parser, expert_grp)
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

  benchmark = ofdm_benchmark(options)
  runtime = benchmark

  r = gr.enable_realtime_scheduling()
  if r != gr.RT_OK:
    print "Couldn't enable realtime scheduling"
  else:
    print "Enabled realtime scheduling"

  try:
    orb = CORBA.ORB_init(sys.argv,CORBA.ORB_ID)
    string_benchmark = runtime.dot_graph()
    
    dot_file = open("benchmark_mimo21.dot",'w')
    dot_file.write(string_benchmark)
    dot_file.close()
    
    runtime.start()
    try:
      tx.txpath._control._id_source.ready()
    except:
      pass
    orb.run()
  except KeyboardInterrupt:
    runtime.stop()

    runtime.wait()
    

  if options.measure:
    print "min",tx.m.get_min()
    print "max",tx.m.get_max()
    print "avg",tx.m.get_avg()

if __name__ == '__main__':
  main()
