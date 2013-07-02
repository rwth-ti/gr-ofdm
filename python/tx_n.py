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

try:
  from gnuradio import uhd
except:
  pass

import sys

from transmit_path import transmit_path
from ofdm_swig import throughput_measure
from common_options import common_tx_rx_usrp_options
from gr_tools import log_to_file, ms_to_file

import fusb_options

from omniORB import CORBA, PortableServer
import CosNaming
from corba_stubs import ofdm_ti,ofdm_ti__POA
from corba_servants import general_corba_servant

import ofdm_swig as ofdm
#import itpp

#from channel import time_variant_rayleigh_channel
from numpy import sqrt
import numpy

import copy

coding=1

"""
You have 4 options:
1.) Normal operation, transmitter connected to usrp
2.) Sent captured file to usrp
3.) Capture transmitter stream to file
4.) Measure the transmitter's average output performance
"""

class ofdm_tx (gr.top_block):
  def __init__ (self, options):
    gr.top_block.__init__(self, "ofdm_tx")

    self._tx_freq            = options.tx_freq         # tranmitter's center frequency
    self._tx_subdev_spec     = options.tx_subdev_spec  # daughterboard to use
    self._fusb_block_size    = options.fusb_block_size # usb info for USRP
    self._fusb_nblocks       = options.fusb_nblocks    # usb info for USRP
    self._which              = options.which_usrp
    self._bandwidth          = options.bandwidth
    self.servants = []
    
    
    self._interface          = options.interface
    self._mac_addr           = options.mac_addr

    self._options = copy.copy( options )


    self._interpolation = 1
    
    f1 = numpy.array([-107,0,445,0,-1271,0,2959,0,-6107,0,11953,
                      0,-24706,0,82359,262144/2,82359,0,-24706,0,
                      11953,0,-6107,0,2959,0,-1271,0,445,0,-107],
                      numpy.float64)/262144.
    
    print "Software interpolation: %d" % (self._interpolation)

    bw = 0.5/self._interpolation
    tb = bw/5
    if self._interpolation > 1:
      self.filter = gr.hier_block2("filter",
                                   gr.io_signature(1,1,gr.sizeof_gr_complex),
                                   gr.io_signature(1,1,gr.sizeof_gr_complex))
      self.filter.connect( self.filter, gr.interp_fir_filter_ccf(2,f1),
                           gr.interp_fir_filter_ccf(2,f1), self.filter )
      
      print "New"
#      
#      
#      self.filt_coeff = optfir.low_pass(1.0, 1.0, bw, bw+tb, 0.2, 60.0, 0)
#      self.filter = gr.interp_fir_filter_ccf(self._interpolation,self.filt_coeff)
#      print "Software interpolation filter length: %d" % (len(self.filt_coeff))
    else:
      self.filter = None
      
      
    if not options.from_file is None:
      # sent captured file to usrp
      self.src = gr.file_source(gr.sizeof_gr_complex,options.from_file)
      self._setup_usrp_sink()
      if hasattr(self, "filter"):
        self.connect(self.src,self.filter,self.u) #,self.filter
      else:
        self.connect(self.src,self.u)
      
      return 
    
    
    
    self._setup_tx_path(options)
    
    config = station_configuration()
    
    self.enable_info_tx("info_tx", "pa_user")
#    if not options.no_cheat:
#      self.txpath.enable_channel_cheating("channelcheat")
    self.txpath.enable_txpower_adjust("txpower")
    self.txpath.publish_txpower("txpower_info")
    #self.enable_txfreq_adjust("txfreq")
    
    
    
    if options.nullsink:
      self.dst = gr.null_sink( gr.sizeof_gr_complex )
    
    else:  
      if not options.to_file is None:
        # capture transmitter's stream to disk
        self.dst  = gr.file_sink(gr.sizeof_gr_complex,options.to_file)
        tmp = gr.throttle(gr.sizeof_gr_complex,1e5)
        self.connect( tmp, self.dst )
        self.dst = tmp
        
        if options.force_filter:
          print "Forcing filter usage"
          self.connect( self.filter, self.dst )
          self.dst = self.filter
        
      else:
        # connect transmitter to usrp
        self._setup_usrp_sink()
        if options.dyn_freq:
            self.enable_txfreq_adjust("txfreq")
            
        if self.filter is not None:
          self.connect( self.filter,self.dst )
          self.dst = self.filter
          
        if options.record:
          log_to_file( self, self.txpath, "data/txpath_out.compl" )
        
        #self.publish_spectrum( 256 )
        
      
        
        
        
    if options.measure:
      self.m = throughput_measure(gr.sizeof_gr_complex)
      self.connect( self.m, self.dst )
      self.dst = self.m
        
    if options.samplingoffset is not None:
      soff = options.samplingoffset
      interp = gr.fractional_interpolator_cc(0.0,soff)
      self.connect( interp, self.dst )
      self.dst = interp

    if options.snr is not None:
      
#      if options.berm is not None:
#          noise_sigma = 380 #empirically given, gives the received SNR range of (1:28) for tx amp. range of (500:10000) which is set in rm_ber_measurement.py
#          #check for fading channel 
#      else:
      snr_db = options.snr
      snr = 10.0**(snr_db/10.0)
      noise_sigma = sqrt( config.rms_amplitude**2 / snr )
      print " Noise St. Dev. %d" % (noise_sigma)
      awgn_chan = gr.add_cc()
      awgn_noise_src = ofdm.complex_white_noise( 0.0, noise_sigma )
      self.connect( awgn_noise_src, (awgn_chan,1) )
      self.connect( awgn_chan, self.dst )
      self.dst = awgn_chan
      
      if options.berm is False:
          fad_chan = itpp.tdl_channel(  ) #[0, -7, -20], [0, 2, 6]
          #fad_chan.set_norm_doppler( 1e-9 )
          #fad_chan.set_LOS( [500.,0,0] )
          fad_chan.set_channel_profile( itpp.ITU_Pedestrian_A, 5e-8 )
          fad_chan.set_norm_doppler( 1e-8 )
    #        fad_chan = gr.fir_filter_ccc(1,[1.0,0.0,2e-1+0.1j,1e-4-0.04j])
          self.connect( fad_chan, self.dst )
          self.dst = fad_chan


    if options.freqoff is not None:
      freq_shift = gr.multiply_cc()
      norm_freq = options.freqoff / config.fft_length
      freq_off_src = gr.sig_source_c(1.0, gr.GR_SIN_WAVE, norm_freq, 1.0, 0.0 )
      self.connect( freq_off_src, ( freq_shift, 1 ) )
      dst = self.dst
      self.connect( freq_shift, dst )
      self.dst = freq_shift
      



    
    self.connect( self.txpath, self.dst )
    
    

    if options.cheat:
      self.txpath.enable_channel_cheating("channelcheat")

    
      
    print "Hit Strg^C to terminate"



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
    
#  def set_rms_amplitude(self, ampl):
#    """
#    Sets the rms amplitude sent to the USRP
#    @param: ampl 0 <= ampl < 32768
#    """
#
#    # The standard output amplitude depends on the subcarrier number. E.g.
#    # if non amplified, the amplitude is sqrt(subcarriers).
#
#    self.rms = max(0.0, min(ampl, 32767.0))
#    scaled_ampl = ampl/math.sqrt(self.config.subcarriers)
#    self._amplification = scaled_ampl
#    self._amplifier.set_k(self._amplification)  
    
  def change_txfreq(self,val):
    self.set_freq(val[0])  
    
  def enable_txfreq_adjust(self,unique_id):
    self.servants.append(corba_push_vector_f_servant(str(unique_id),1,
        self.change_txfreq,
        msg="Changing tx frequency\n"))
    print "enable_txfreq_adjust"

  def _setup_tx_path(self,options):
    self.txpath = transmit_path(options)
    
    for i in range( options.stations ):
      print "Registering mobile station with ID %d" % ( i+1 )
      self.txpath.add_mobile_station( i+1, )
    
    

  def _setup_usrp_sink(self):
    """
    Creates a USRP sink, determines the settings for best bitrate,
    and attaches to the transmitter's subdevice.
    """
    if self._tx_freq is None:
      sys.stderr.write("-f FREQ or --freq FREQ or --tx-freq FREQ must be specified\n")
      raise SystemExit

    if self._options.usrp2:
      self.u = usrp2.sink_32fc(self._interface, self._mac_addr)
      self.dst = self.u
      print "Using USRP2, as you wish, my master"
      print "USRP2 MAC address is %s" % ( self.u.mac_addr() )
      
      self._interp = 100e6 / self._bandwidth / self._interpolation
      self.u.set_interp(int(self._interp))
    else:
      self.u = uhd.usrp_sink(device_addr="", stream_args=uhd.stream_args('fc32'))
      #self.uc = gr.complex_to_interleaved_short()
      #self.connect( self.uc, self.u )
      self.dst = self.u
      #print "USRP serial number is %s" % ( self.u.serial_number() )
    
      print "Using new USRP1 tx chain with halfband filters on FPGA"
      
      self._interp = int(100e6 / self._bandwidth / self._interpolation)
      #print "XXXXXXXXXXXXXXXXX", self._bandwidth * self._interpolation
      self.u.set_samp_rate(self._bandwidth * self._interpolation)
      
      # determine the daughterboard subdevice we're using
      if self._tx_subdev_spec is None:
          self._tx_subdev_spec = self.u.get_subdev_spec()
      self.u.set_subdev_spec(self._tx_subdev_spec)
      
    
      print "USRP used: ", ( self.u.get_usrp_info().get("mboard_id").split(" ")[0])
      print "USRP serial number is: ",  ( self.u.get_usrp_info().get("mboard_serial"))  
      print "TX Daughterboard used: ", ( self.u.get_usrp_info().get("tx_id").split(" ")[0].split(",")[0])
      
      dboard_serial = self.u.get_usrp_info().get("tx_serial")    
      if dboard_serial == "":   
                dboard_serial = "no serial"
      print "TX Daughterboard serial number is: ", dboard_serial
    
    print "FPGA interpolation",self._interp

    # Set center frequency of USRP
    ok = self.set_freq(self._tx_freq)
    if not ok:
      print "Failed to set Tx frequency to %s" % (eng_notation.num_to_str(self._tx_freq),)
      raise ValueError

    # Set the USRP for maximum transmit gain
    # (Note that on the RFX cards this is a nop.)
    if self._options.usrp2:
      self.set_gain(0.3) # ??????????????????????????????
    else:
      #g = self.u.get_gain_range()
      #print "Rx Gain Range: ", g
      g=0
      self.set_gain(g)
    print "Starte Strahlenwaffe mit maximaler Leistung"
    print "And now, young jedi, you will die !!!"

#    self.u.enable_detailed_profiling()

    #if not self._options.usrp2:
      #self.u.set_enable(True)

  def set_freq(self, target_freq):
    """
    Set the center frequency we're interested in.

    @param target_freq: frequency in Hz
    @rypte: bool

    Tuning is a two step process.  First we ask the front-end to
    tune as close to the desired frequency as it can.  Then we use
    the result of that operation and our target_frequency to
    determine the value for the digital up converter.
    """
    if self._options.usrp2:
      r = self.u.set_center_freq(target_freq)
    else:
      r = self.u.set_center_freq(target_freq, 0)
    if r:
        return True

    return False

  def set_gain(self, gain):
    """
    Sets the analog gain in the USRP
    """
    self.gain = gain
    if self._options.usrp2:
      self.u.set_gain(gain)
    else:
      self.u.set_gain(gain,0)

  #def set_auto_tr(self, enable):
   # """
   # Turns on auto transmit/receive of USRP daughterboard (if exits; else ignored)
  ##  """
  # # if not self._options.usrp2:
  #    return self.subdev.set_auto_tr(enable)
 #   else:
 #     return True

  #def __del__(self):
    #if hasattr(self, "subdev"):
     # del self.subdev

  def _print_verbage(self):
    """
    Prints information about the transmit path
    """
    print "\nTransmit Path:"
    print "Bandwidth:       %s"    % (eng_notation.num_to_str(self._bandwidth))
    if "self.u" in vars(self):
      print "Using TX d'board %s"    % (self.subdev.side_and_name(),)
      print "Tx gain:         %g"    % (self.gain,)
      print "FPGA interp:    %3d"    % (self._interp)
      print "Software interp:%3d"    % (self._interpolation)
      print "Tx Frequency:    %s"    % (eng_notation.num_to_str(self._tx_freq))
      print "DAC rate:        %s"    % (eng_notation.num_to_str(self.u.dac_rate()))
    print ""

  def enable_info_tx(self,unique_id,userid):
    """
    create servant for info_tx interface and give him our specifications.
    only fixed data should go here!
    """

    config = station_configuration()
    carrier_freq = self._tx_freq or 0.0
    bandwidth = self._bandwidth or 2e6
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

    normal.add_option("-T", "--tx-subdev-spec", type="subdev", default=None,
                      help="select USRP Tx side A or B")
    expert.add_option("", "--tx-freq", type="eng_float", default=None,
                      help="set transmit frequency to FREQ [default=%default]", metavar="FREQ")
    normal.add_option("", "--measure", action="store_true", default=False,
                      help="enable troughput measure, usrp disabled");
                      
    normal.add_option("", "--dyn-freq", action="store_true", default=False,
                      help="enable troughput measure, usrp disabled");

    expert.add_option("", "--snr", type="eng_float", default=None,
                      help="Simulate AWGN channel");
    expert.add_option("", "--freqoff", type="eng_float", default=None,
                      help="Simulate frequency offset [default=%default]")
    expert.add_option("", "--samplingoffset", type="eng_float", default=None,
                      help="Simulate sampling frequency offset [default=%default]")
    expert.add_option("", "--berm", action="store_true", default=False,
                      help="Enable static AWGN power for BER measurement")

    expert.add_option("", "--online-work", action="store_true", default=False,
                      help="Force the ofdm transmitter to work during file record [default=%default]")
    normal.add_option("", "--from-file", type="string", default=None,
                      help="Sent recorded stream with usrp")
    normal.add_option("", "--to-file", type="string", default=None,
                      help="Record transmitter to disk, not being sent to usrp")

    expert.add_option("", "--force-filter", action="store_true", default=False,
                      help="force filter use while transmitting to file or measuring")
    
    expert.add_option("", "--nullsink", action="store_true",
                      default=False,
                      help="Throw away samples")
    
    normal.add_option("-e", "--interface", type="string", default="eth0",
                          help="select Ethernet interface, default is eth0")
    normal.add_option("-m", "--mac-addr", type="string", default="",
                          help="select USRP by MAC address, default is auto-select")
    normal.add_option("", "--usrp2", action="store_true", default=False,
                      help="Use USRP2 Interface")
    

    expert.add_option("", "--record", action="store_true",
                      default=False,
                      help="Record transmission stream")
    
    expert.add_option("", "--stations", type="intx", default=1,
                      help="Mobile station count")
    
    normal.add_option("", "--coding", action="store_true",
              default=False,
              help="Enable channel coding")

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

  ofdm_tx.add_options(parser, expert_grp)
  transmit_path.add_options(parser, expert_grp)
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

  tx = ofdm_tx(options)
  runtime = tx

  r = gr.enable_realtime_scheduling()
  if r != gr.RT_OK:
    print "Couldn't enable realtime scheduling"
  else:
    print "Enabled realtime scheduling"

  try:
    orb = CORBA.ORB_init(sys.argv,CORBA.ORB_ID)
    string_tx = runtime.dot_graph()
    
    dot_file = open("text_tx.dot",'w')
    dot_file.write(string_tx)
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
