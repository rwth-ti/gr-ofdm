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

from gnuradio import gr, filter_blocks
from gnuradio import eng_notation
from configparse import OptionParser


from station_configuration import station_configuration

try:
  from gnuradio import uhd
except:
  pass

import sys

from receive_path12 import receive_path as receive_path_12
from receive_path22_neu import receive_path as receive_path_22
from ofdm import throughput_measure, vector_sampler, corba_rxbaseband_sink, multiply_const_ccf
from numpy import sum,concatenate
from common_options import common_tx_rx_usrp_options
from math import log10
import fusb_options
import numpy
import copy

from corba_servants import corba_data_buffer_servant,corba_push_vector_f_servant
from gr_tools import log_to_file
from omniORB import CORBA

"""
You have three options:
1.) Run the ofdm receiver online, connected to usrp
2.) Record a stream from usrp to disk, without processing
    use --to-file=xx
3.) Run the ofdm receiver offline with a previously recorded stream
    use --from-file=xx
    with --online-work, you can force the receiver process the data online
"""

class ofdm_rx (gr.top_block):
  def __init__ (self, options):
    gr.top_block.__init__(self, "ofdm_rx")

    config = self.config = station_configuration()

    self._verbose            = options.verbose
    self._rx_freq            = options.rx_freq         # receiver's center frequency
    self._rx_gain            = options.rx_gain         # receiver's gain
    self._rx_subdev_spec0     = options.rx_subdev_spec  # daughterboard to use
    self._rx_subdev_spec1     = options.rx_subdev_spec  # daughterboard to use
    self._fusb_block_size    = options.fusb_block_size # usb info for USRP
    self._fusb_nblocks       = options.fusb_nblocks    # usb info for USRP
    self._bandwidth          = options.bandwidth       # total bandwidth. not the signal bandwidth!
    self._which              = options.which_usrp
    self.servants = []

    self._interface          = options.interface
    self._mac_addr           = options.mac_addr
    self._options               = copy.copy(options)


    self.decimation = 1
    
#    if self.decimation > 1:
#      bw = 0.5/self.decimation * 1
#      tb = bw/5
      # gain, sampling rate, passband cutoff, stopband cutoff
      # passband ripple in dB, stopband attenuation in dB
      # extra taps
#      filt_coeff = optfir.low_pass(1.0, 1.0, bw, bw+tb, 0.1, 60.0, 1)
#      print "Software decimation filter length: %d" % (len(filt_coeff))
#      self.filter = gr.fir_filter_ccf(self.decimation,filt_coeff)
#    else:
#      self.filter = None
      
      
    if self.decimation > 1:
      self.filter =  blks2.pfb_arb_resampler_ccf(1./self.decimation, taps=None, flt_size=32, atten=80)
    else:
      self.filter = None



    if options.to_file is not None:
      # record without processing
      self._setup_usrp_source()
      self._configure_usrp(options)
      self.dst = gr.file_sink(gr.sizeof_gr_complex,options.to_file)
      self.connect(self.u,self.filter,self.dst)
      print "Hit Strg^C to terminate"
      return



      # use file as receiver input

    self._setup_rx_path(options)

    if options.imgxfer:
      self.rxpath.setup_imgtransfer_sink()


    #self.rxpath.publish_ber_measurement(["ber"])
    #self.rxpath.publish_average_snr(["totalsnr","totalsnr_pa"])


    #self.rxpath.publish_ctf("ctf_display")
#    if options.sinr_est:
#        self.rxpath.publish_sinrsc("sinrsc_display")
    #self.rxpath.publish_packetloss("packetloss")



    if not options.no_decoding:
      self.rxpath.publish_rx_performance_measure()



    if options.from_file is not None:
      if options.measure:
        f = open(options.from_file,"rb")
        config = self.config = station_configuration()
        c = config.block_length*config.frame_length*10
        data = numpy.fromfile(file=f,dtype=numpy.complex64,count=c)
        print len(data)
        f.close()
        self.src = gr.vector_source_c(data.tolist(),True)
        self.tm = throughput_measure(gr.sizeof_gr_complex)
      else:
        self.src = gr.file_source(gr.sizeof_gr_complex,options.from_file)
        self.tm = gr.throttle(gr.sizeof_gr_complex,1e5)
        print "FROM FILE"

      if options.force_filter:
        print "Forcing filter usage"
      else:
        self.filter = gr.kludge_copy(gr.sizeof_gr_complex)

      self.connect( self.src, self.tm, self.filter, self.rxpath )

    else:
      # online receiving, optionally log to file
      # Set up USRP source; also adjusts decim, samples_per_symbol, and bitrate
      self._setup_usrp_source()
      if options.dyn_freq:
          self.enable_rxfreq_remote_adjust("rxfreq")
      self._configure_usrp(options)

      self.enable_rxgain_remote_adjust("rxgain")

      
      if self.filter is not None:
        self.connect( self.u, self.filter, self.rxpath )
      else:
        #self.connect( (self.u_mimo,0), multiply_const_ccf( 6.4),(self.rxpath,0) )
        self.connect( (self.u0, 0), (self.rxpath,0) )
        self.connect( (self.u0, 1), (self.rxpath,1) )
        #log_to_file( self, (self.u_mimo,0), "data/deint_1.compl" )
        #log_to_file( self, (self.u_mimo,1), "data/deint_2.compl" )
        

    if options.event_rxbaseband:
      self.publish_rx_baseband_measure()

#    if options.scatterplot:
#      print "Scatterplot enabled"
#      self.rxpath.filter_constellation_samples_to_file( )

      
    if options.with_old_gui:
      self.publish_rx_spectrum(256)
      self.rxpath.publish_ctf("ctf_display")
      self.rxpath.publish_ber_measurement(["ber"])
      self.rxpath.publish_average_snr(["totalsnr"])
      if options.sinr_est:
        self.rxpath.publish_sinrsc("sinrsc_display")
      


    print "Hit Strg^C to terminate"


    # Display some information about the setup
    if self._verbose:
        self._print_verbage()

  def _setup_rx_path(self,options):
    if options.tx_ant == 1:  
        self.rxpath = receive_path_12(options)
    else:
        self.rxpath = receive_path_22(options)
    #self.rxpath.setup_ber_measurement()
    #self.rxpath.setup_snr_measurement()


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

    my_window = filter.hamming(fftlen) #.blackmanharris(fftlen)
    rxs_sampler = vector_sampler(gr.sizeof_gr_complex,fftlen)
    array1 = concatenate([[1],[0]*199])
    rxs_trigger = gr.vector_source_b(array1.tolist(),True)
    rxs_window = gr.multiply_const_vcc(my_window)
    rxs_spectrum = gr.fft_vcc(fftlen,True,[],True)
    rxs_mag = gr.complex_to_mag(fftlen)
    rxs_avg = gr.single_pole_iir_filter_ff(0.01,fftlen)
    rxs_logdb = gr.nlog10_ff(20.0,fftlen,-20*log10(fftlen))
    rxs_decimate_rate = gr.keep_one_in_n(gr.sizeof_float*fftlen,50)

    t = (self.u0) if self.filter is None else self.filter
    self.connect(rxs_trigger,(rxs_sampler,1))
    self.connect(t,rxs_sampler,rxs_window,
                 rxs_spectrum,rxs_mag,rxs_avg,rxs_logdb, rxs_decimate_rate)
    if self._options.log:
          log_to_file(self, rxs_decimate_rate, "data/supply_rx.float")
    self.rx_baseband = rxs_decimate_rate
    return rxs_decimate_rate

#  def trigger_watch(self):
#      self.servants.append(corba_ndata_buffer_servant(str(unique_id),
#        self.trigger_watcher.lost_triggers,self.trigger_watcher.reset_counter))

  def publish_spectrum(self,fftlen):
    ## RX Spectrum

    fftlen = 256
    my_window = filter.hamming(fftlen) #.blackmanharris(fftlen)
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

  def change_rxgain(self,val):
    self.set_gain(val[0])

  def enable_rxgain_remote_adjust(self,unique_id):
    self.servants.append(corba_push_vector_f_servant(str(unique_id),1,
        self.change_rxgain,
        msg=""))
  
  def change_rxfreq(self,val):
    self.set_freq(val[0])
  
  def enable_rxfreq_remote_adjust(self,unique_id):
    self.servants.append(corba_push_vector_f_servant(str(unique_id),1,
        self.change_rxfreq,
        msg="Change rx frequency\n"))  

  def _setup_usrp_source(self):
    if self._rx_freq is None:
        sys.stderr.write("-f FREQ or --freq FREQ or --rx-freq FREQ must be specified\n")
        raise SystemExit

    if self._options.usrp2:
      self.u = usrp2.source_32fc(self._interface, self._mac_addr)
      self._decim = int(100e6 / self._bandwidth / self.decimation)
      self.u.set_decim(self._decim)
      
      print "USRP2 MAC address is %s" % ( self.u.mac_addr() )
    else:
      self.u0 = uhd.usrp_source(device_addr=" addr0=192.168.10.2, addr1=192.168.10.3", stream_args=uhd.stream_args(cpu_format="fc32",
                channels=range(2)))
      
      self.u0.set_clock_source("mimo", 1)
      self.u0.set_time_source("mimo", 1)
      self._decim = int(100e6 / self._bandwidth / self.decimation)
      self.u0.set_samp_rate(self._bandwidth * self.decimation)
      
      #if self._rx_subdev_spec0 is None:
         # self._rx_subdev_spec0 = self.u0.get_subdev_spec()
      #self.u0.set_subdev_spec(self._rx_subdev_spec0)
      
     # if self._rx_subdev_spec1 is None:
      #    self._rx_subdev_spec1 = self.u1.get_subdev_spec()
     # self.u1.set_subdev_spec(self._rx_subdev_spec1)
      
      
      print "USRP_0 used: ", ( self.u0.get_usrp_info().get("mboard_id").split(" ")[0])
      print "USRP_0 serial number is: ",  ( self.u0.get_usrp_info().get("mboard_serial"))  
      print "RX_0 Daughterboard used: ", ( self.u0.get_usrp_info().get("rx_id").split(" ")[0].split(",")[0])
      
      dboard_serial = self.u0.get_usrp_info().get("rx_serial")    
      if dboard_serial == "":   
                dboard_serial = "no serial"
      print "RX_0 Daughterboard serial number is: ", dboard_serial
      
      
      #MIMO modification
      #rx_ant_a="TX/RX"
      #rx_ant_b="RX2"

      ##subdev_spec_a = (0, 0) #HARD CODED FOR 2x RFX 2400
      ##subdev_spec_b = (1, 0)
        
      ##self.u.set_mux(self.u.determine_rx_mux_value(subdev_spec_a, subdev_spec_b))
      
      
      ##self._subdev_a = self.u.selected_subdev(subdev_spec_a)
      ##self._subdev_b = self.u.selected_subdev(subdev_spec_b)
      
      ##deinter = gr.deinterleave(gr.sizeof_gr_complex)
      ##self.connect(self.u, deinter)
      #self.u_mimo = deinter
      
      #for i in range(2):
         #self.connect((deinter, i), (self, i))

      
      ##adc_rate = self.u.adc_rate()
  
      ##self._decim = int(adc_rate / self._bandwidth / self.decimation)
      ##self.u.set_decim_rate(self._decim)
    
      # determine the daughterboard subdevice we're using
####      if self._rx_subdev_spec is None:
####          self._rx_subdev_spec = usrp.pick_rx_subdevice(self.u)
####      self.subdev = usrp.selected_subdev(self.u, self._rx_subdev_spec)
####  
####      self.u.set_mux(usrp.determine_rx_mux_value(self.u, self._rx_subdev_spec))
####  
####      print "Using RX D'Board: %s" % (self.subdev.side_and_name())
      
      ##print "Using RX D'Board: %s" % (self._subdev_a.side_and_name())
      
      #print "Using RX D'Board: %s" % (self._subdev_b.side_and_name())
      
      ##print "USRP serial number is %s" % ( self.u.serial_number() )
    
    print "FPGA decimation: %d" % (self._decim)
    
    


  def _configure_usrp(self,options):
    
    if not options.usrp2 and options.show_rx_gain_range:
      g0 = self.u0.gain_range()
      print "Rx Gain Range: minimum = %g, maximum = %g, step size = %g" \
            % (g0[0], g0[1], g0[2])

    
    if not options.usrp2 and options.show_rx_gain_range:
      g1 = self.u0.gain_range()
      print "Rx Gain Range: minimum = %g, maximum = %g, step size = %g" \
            % (g1[0], g1[1], g1[2])

    self.set_gain(options.rx_gain)
    
    ok = self.set_freq(self._rx_freq)
    if not ok:
        print "Failed to set Rx frequency to %s" % (eng_notation.num_to_str(self._rx_freq))
        raise ValueError, eng_notation.num_to_str(self._rx_freq)

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
      rb = True
    else:
      #r = self.u.tune(self.subdev.which(), self.subdev, target_freq)
      r0 = self.u0.set_center_freq(target_freq, 0)
      r1 = self.u0.set_center_freq(target_freq, 1)
    
    if r0 and r1:
      ##print "\tr.baseband_frequency =", r0.baseband_freq
      ##print "\tr.dxc_frequency =", r0.dxc_freq
      
      ##print "\trb.baseband_frequency =", r1.baseband_freq
      ##print "\trb.dxc_frequency =", r1.dxc_freq
      return True

    return False

  def set_gain(self, gain):
    """
    Sets the analog gain in the USRP
    """
    self.gain = gain
    gain0=gain
    gain1=gain
    print "RX Gain set to %d" %(gain)

    if self._options.usrp2:
      return self.u.set_gain(gain)
    else:
     if gain is None:
           g0 = self.u0.get_gain_range()
           gain0 = float(g0.start()+g0.stop())/2
           print "\nNo gain specified."
           print "Setting gain to %f (from [%f, %f])" % \
                (gain0, g0.start(), g0.stop())
                
           g1 = self.u0.get_gain_range()
           gain1 = float(g1.start()+g1.stop())/2
           print "\nNo gain specified."
           print "Setting gain to %f (from [%f, %f])" % \
                (gain1, g1.start(), g1.stop())
                
                
     self.u0.set_gain(50, 0)
     self.u0.set_gain(50, 1)
     return gain

  #def set_auto_tr(self, enable):
    #return self._subdev_a.set_auto_tr(enable) # Experimental

  #def __del__(self):
    #if hasattr(self, "subdev"):
      #del self.subdev

  def add_options(normal, expert):
    """
    Adds receiver-specific options to the Options Parser
    """
    common_tx_rx_usrp_options(normal,expert)
    normal.add_option("-R", "--rx-subdev-spec", type="subdev", default=None,
                      help="select USRP Rx side A or B")
    normal.add_option("", "--rx-gain", type="eng_float", default=35, metavar="GAIN",
                      help="set receiver gain in dB [default=midpoint].  See also --show-rx-gain-range")
    normal.add_option("", "--show-rx-gain-range", action="store_true", default=False,
                      help="print min and max Rx gain available on selected daughterboard")
    expert.add_option("", "--rx-freq", type="eng_float", default=None,
                      help="set receive frequency to FREQ [default=%default]", metavar="FREQ")
    expert.add_option("", "--online-work", action="store_true", default=False,
                      help="Force the ofdm receiver to work during file record [default=%default]")
    expert.add_option("", "--sinr-est", action="store_true", default=False,
                      help="Enable SINR per subcarrier estimation [default=%default]")
    normal.add_option("", "--from-file", type="string", default=None,
                      help="Run Receiver on recorded stream")
    normal.add_option("", "--to-file", type="string", default=None,
                      help="Record stream from usrp to disk, no processing")
    expert.add_option("", "--measure", action="store_true", default=False,
                      help="enable throughput measure");
    expert.add_option("", "--dyn-freq", action="store_true", default=False,
                      help="enable dynamic frequency change");
    expert.add_option("", "--tx-ant", type="int", default=1,
                      help="the number of transmit antennas")
                      
    normal.add_option("-e", "--interface", type="string", default="eth0",
                          help="select Ethernet interface, default is eth0")
    normal.add_option("-m", "--mac-addr", type="string", default="",
                          help="select USRP by MAC address, default is auto-select")
    normal.add_option("", "--usrp2", action="store_true", default=False,
                      help="Use USRP2 Interface")
    expert.add_option("", "--est-preamble", type="int", default=1,
                      help="the number of channel estimation preambles (1 or 2)")


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

    receive_path_12.add_options(normal,expert)
    receive_path_22.add_options(normal,expert)

    expert.add_option("", "--force-filter", action="store_true", default=False,
                      help="force filter use while transmitting to file or measuring")

  # Make a static method to call before instantiation
  add_options = staticmethod(add_options)


  def _print_verbage(self):
    """
    Prints information about the receive path
    """
    print "\nReceive Path:"
    print "Bandwidth:       %s"    % (eng_notation.num_to_str(self._bandwidth))
    if hasattr(self, "u"):
      print "Using RX d'board %s"    % (self.subdev.side_and_name(),)
      print "Rx gain:         %g"    % (self.gain,)
      print "decim:           %3d"   % (self._decim)
      print "Rx Frequency:    %s"    % (eng_notation.num_to_str(self._rx_freq))
      print "ADC rate:        %s"    % (eng_notation.num_to_str(self.u.adc_rate()))
    print ""


def main():
  

  parser = OptionParser(conflict_handler="resolve")

  expert_grp = parser.add_option_group("Expert")

  ofdm_rx.add_options(parser, expert_grp)
  receive_path_12.add_options(parser, expert_grp)
  receive_path_22.add_options(parser, expert_grp)
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


  rx = ofdm_rx(options)

  try:
    r = gr.enable_realtime_scheduling()
    if r != gr.RT_OK:
      print "Couldn't enable realtime scheduling"
    else:
      print "Enabled realtime scheduling"

    orb = CORBA.ORB_init(sys.argv,CORBA.ORB_ID)
    runtime = rx
    string_rx = runtime.dot_graph()
    
    dot_file = open("text_rx.dot",'w')
    dot_file.write(string_rx)
    dot_file.close()

    runtime.start()
    orb.run()
  except Exception,ex:
    print "ui"
    print repr(ex)

  except:
    print "Whatever"

  try:
    runtime.stop()

    # somewhat messy hack
    try:
      rx.rxs_msgq.flush()
      rx.rxs_msgq.insert_tail(gr.message(1))
    except:
      print "Could not flush msgq"
      pass

    runtime.wait()


    if options.measure:
      print "min",rx.tm.get_min()
      print "max",rx.tm.get_max()
      print "avg",rx.tm.get_avg()

    runtime = None
    rx = None

  except Exception,ex:
    print "Caught exception:",repr(ex)

  except:
    pass


  return

  if not hasattr(rx, "rxpath"):
    return

  if hasattr(rx.rxpath, "trigger_watcher"):
    print "Lost trigger: %d" % (rx.rxpath.trigger_watcher.lost_triggers())



  if not rx.rxpath.demod.has_key("test_demod"):
    return

  data = rx.rxpath.demod["test_demod"].dst.data()
  print "Received %d bits" % (len(data))

  data_sym = rx.rxpath.demod["test_demod"].src.data

  # verify with simulation
  vec = rx.rxpath.demod["test_demod"].frame_trigger_sink.data()
  rft_count = sum(vec)
  print "Received ofdm blocks: %d" % (rft_count)

  assert(int(len(data)/len(data_sym))*len(data_sym) == len(data))

  # if BER of symbol is greater than this value, the symbol is shown
  min_ber = 0.1
  sym_text = []
  sym_count = 0

  syms = len(data)/len(data_sym)
  total_errors = 0
  for j in range(syms):
    e = 0

    for k in range(len(data_sym)):
      i = j*len(data_sym)+k
      e += data[i] ^ data_sym[i%len(data_sym)]

    #if j < 50:
      #print "Block %d, bit errors: %d" % (j,e)

    if e > min_ber*len(data_sym):
      sym_text.append(str(data[j*len(data_sym):(j+1)*len(data_sym)])+"\n")
      sym_count += 1
    total_errors += e

  print "Bit errors: %d" % (total_errors)
  print "Bit error rate: %s" % (float(total_errors)/len(data))

  print "%d erroneous symbols with BER higher than %f" %(sym_count,min_ber)
#  if sym_count <= 10:
#    print ''.join(sym_text)
#  else:
#    print "More than 10 Symbols in error"
#    #print ''.join(sym_text[0:10])

  snr = rx.rxpath.total_snr_sink.data()
  #print "The first 100 SNR estimates:"
  #print snr[0:100]

  block_length = rx.rxpath.block_length

  if hasattr(rx.rxpath.receiver,"tm_level_sink") and hasattr(rx.rxpath.receiver, "freq_offset_sink"):
    vec = rx.rxpath.receiver.tm_level_sink.data()
    eps = rx.rxpath.receiver.freq_offset_sink.data()
    #for i in range(len(vec)):
    #  print "%3d: tm %.5f freq %.8f" % (i,vec[i],eps[i])

  if hasattr(rx.rxpath.receiver,"real_frame_trigger"):
    vec = rx.rxpath.receiver.real_frame_trigger.data()

    last_trigger = -1
    # acquire
    for i in range(len(vec)):
      if vec[i] == 1:
        last_trigger = i
        break

    if last_trigger > -1:
      # track
      trig = 1
      print "First trigger: %d" % (last_trigger)
      ideal_distance = block_length*rx.rxpath.frame_length
      print "Ideal distance: %d" % (ideal_distance)
      for i in range(last_trigger+1,len(vec)):
        if vec[i] == 1:
          trig += 1
          delta_dist = i - last_trigger - ideal_distance
          if delta_dist <> 0:
            print "Trigger %d not as expected: %d, at %d" % (trig,delta_dist,i)
          last_trigger = i

  if hasattr(rx.rxpath.receiver, "frame_trigger_sink"):
    vec = rx.rxpath.receiver.frame_trigger_sink.data()
    print "Frame trigger stream: %d, Trigger points: %d" % (len(vec),sum(vec))


if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    print "oh mein gott!"
    pass
