#!/usr/bin/env python

from gnuradio import gr
import ofdm as ofdm
#import itpp
import numpy
from preambles import schmidl_ifo_designer, morellimengali_designer
from gr_tools import terminate_stream, log_to_file, determine_streamsize
from gr_tools import ifft as gr_ifft, char_to_float_stream
from snr_estimator import milans_snr_estimator

from numpy import sqrt, concatenate, log10
from numpy import mean, var, ceil
from numpy.random import randint, seed, random_integers


"""
There a two simulations. One estimates the MSE of the channel estimator.
The other estimates the BER.

They have in common that both simulate an AWGN channel plus a simple static
fading channel (time invariant). The MSE simulator compares the estimated
CTF to the true one and, as it name says, calculates the mean squared error.
The BER simulator indeed demodulates the data after channel equalization.
It is using two equalizer, one is the estimator+equalizer under test and the
other one is the optimal equalizer (which is simply a divide unit, because the
static fading channel allows for computing the inverse CTF before simulation
starts). The bit streams are compared to the sent data and a BER value for
each estimator/equalizer chain is estimated. We can compare the performance
of the optimal solution (which is, of course, non-causal), to the performance
of our block.
When a simulator compares two blocks, e.g. in the BER simulator, there is only
_one_ channel simulation. Both blocks work on the same samples! So we can see
how they perform under identical circumstances.

Both simulation use the same channel estimator (currently channel_estimator_02).
There are two hierarchical blocks that encapsulate the channel estimator basic
block. channel_estimator_001 is used for the MSE simulation. We assume that
only one preamble is used, and that every OFDM block is a preamble. The input
stream is from the simulated channel, the output contains the estimated CTF.
This CTF estimate is compared to the true one. Note that we don't account for
time variant channel, therefore please don't change the fading channel to
include such effects.

The simulations are tuned for speed. They use several simulator chains in
parallel and reuse the simulators. There are always several simulations runs,
whose values are averaged. Upon completion of a run, the results are collected
and the simulators are reset instead of destroyed and recreated (as long as
a reset is applicable). This solution enhanced the simulator speed
significantly.

To change parameters, have a look at test_channel_estimator. It is the last
class in this script. You can modify the settings in the two functions
start_ber_sim and start_mse_sim respectively. Which simulator is to be run
can be chosen at the last line of this script. After
  if __name__ == '__main__':
change the following function call to your choice.

The simulation results are presented in the matlab script language. You can
copy these and paste them in your matlab command window, which will give you
results in variables and nice plots.

The gaussian noise source resets its random number generator on every startup.
For the static fading channel, however, you can reproduce values if you want,
by uncommenting
  #channel.global_rng_reset( 9 )
in the class initializer of static_fading_channel. You should provide a
reasonable seed (in the example above, it is 9).

"""


verbose = False
class snr_estimator_001 (gr.hier_block2):
  """
  There is only one preamble used.
  Each OFDM block is a preamble.
  The complex valued estimated snr is on output 1.
  """

  td,fd = None,None
  vlen = 0

  def __init__( self, vlen ):

    gr.hier_block2.__init__( self,
        "channel_estimator_001",
        gr.io_signature( 1, 1, gr.sizeof_gr_complex * vlen ),
        gr.io_signature( 1, 1, gr.sizeof_float ) )

    #nondata_blocks = [1]
    #pilot_tones = [0]
    if snr_estimator_001.vlen != vlen or \
       snr_estimator_001.td is None or \
       snr_estimator_001.fd is None :
      td,fd = morellimengali_designer.create(vlen, vlen,8) #-> replace the fixed number of periodic parts->8
      snr_estimator_001.td, snr_estimator_001.fd = td,fd
      snr_estimator_001.vlen = vlen
    else:
      td,fd = snr_estimator_001.td, snr_estimator_001.fd

    self.preamble_td = td
    self.preamble_fd = fd

    uut = milans_snr_estimator( vlen, vlen, 8 )#-> replace the fixed number of periodic parts->8
    #uut.set_known_block( 0, self.preamble_fd, True )

    #trigger = gr.vector_source_b( [1], True )

    self.connect( self, uut )
    #self.connect( trigger, ( uut, 1 ) )
    self.connect( ( uut), self )

    #terminate_stream( self, ( uut, 0 ) )
    #terminate_stream( self, ( uut, 1 ) )

  def reset(self):
    pass

class channel_estimator_001 (gr.hier_block2):
  """
  There is only one preamble used.
  Each OFDM block is a preamble.
  The complex valued estimated CTF is on output 1.
  """

  td,fd = None,None
  vlen = 0

  def __init__( self, vlen ):

    gr.hier_block2.__init__( self,
        "channel_estimator_001",
        gr.io_signature( 1, 1, gr.sizeof_gr_complex * vlen ),
        gr.io_signature( 1, 1, gr.sizeof_gr_complex * vlen ) )

    nondata_blocks = [1]
    pilot_tones = [0]
    if channel_estimator_001.vlen != vlen or \
       channel_estimator_001.td is None or \
       channel_estimator_001.fd is None :
      td,fd = schmidl_ifo_designer.create(vlen, vlen)
      channel_estimator_001.td, channel_estimator_001.fd = td,fd
      channel_estimator_001.vlen = vlen
    else:
      td,fd = channel_estimator_001.td, channel_estimator_001.fd

    self.preamble_td = td
    self.preamble_fd = fd

    uut = ofdm.channel_estimator_02(vlen, pilot_tones, nondata_blocks)
    uut.set_known_block( 0, self.preamble_fd, True )

    trigger = gr.vector_source_b( [1], True )

    self.connect( self, uut )
    self.connect( trigger, ( uut, 1 ) )
    self.connect( ( uut, 2 ), self )

    terminate_stream( self, ( uut, 0 ) )
    terminate_stream( self, ( uut, 1 ) )

  def reset(self):
    pass

class channel_estimator_002 (gr.hier_block2):
  """
  There is only one preamble used. Phase tracking is disabled.
  The first OFDM block in a frame is a preamble. You can specify frame length.
  The output stream contains the equalized ofdm blocks.
  """

  td,fd = None,None
  vlen = 0

  def __init__(self, vlen, frame_length ):

    gr.hier_block2.__init__( self,
        "channel_estimator_002",
        gr.io_signature( 1, 1, gr.sizeof_gr_complex * vlen ),
        gr.io_signature( 1, 1, gr.sizeof_gr_complex * vlen ) )

    # disable phase tracking
    nondata_blocks = range(frame_length)
    pilot_tones = []

    if channel_estimator_002.vlen != vlen or \
       channel_estimator_002.td is None or \
       channel_estimator_002.fd is None :
      td,fd = schmidl_ifo_designer.create(vlen, vlen)
      channel_estimator_002.td, channel_estimator_002.fd = td,fd
      channel_estimator_002.vlen = vlen
    else:
      td,fd = channel_estimator_002.td, channel_estimator_002.fd

    self.preamble_td = td
    self.preamble_fd = fd

    uut = ofdm.channel_estimator_02(vlen, pilot_tones, nondata_blocks)
    uut.set_known_block( 0, fd, True )

    trigger = [0]*frame_length
    trigger[0] = 1
    trigger = gr.vector_source_b( trigger, True )
    self.trigger = trigger

    self.connect( self, uut, self )
    self.connect( trigger, ( uut, 1 ) )

    terminate_stream( self, ( uut, 1 ) )

  def reset(self):
    self.trigger.rewind()


class channel_estimator_003 (gr.hier_block2):
  """
  Uses channel_estimator_001.
  Improved MSE through filtering of CTF.
  """
  def __init__( self, vlen, cp_len ):

    gr.hier_block2.__init__( self,
        "channel_estimator_003",
        gr.io_signature( 1, 1, gr.sizeof_gr_complex * vlen ),
        gr.io_signature( 1, 1, gr.sizeof_gr_complex * vlen ) )

    self.ch_est = channel_estimator_001( vlen )
    self.connect( self, self.ch_est )

    cir_len = cp_len + 1
    self.cir_len = cir_len
    self.vlen = vlen

    self.preamble_td = self.ch_est.td
    self.preamble_fd = self.ch_est.fd

    # CTF -> CIR
    self.cir_est = gr.fft_vcc( vlen, False, [], False ) # IFFT
    self.connect( self.ch_est, self.cir_est )

    # CIR -> energy per sample
    self.cir_energy = gr.complex_to_mag_squared( vlen )
    self.connect( self.cir_est, self.cir_energy )

    # prepare cyclic convolution of CIR vector
    self.cyclic_cir = gr.streams_to_vector( gr.sizeof_float * vlen, 2 )
    self.connect( self.cir_energy, ( self.cyclic_cir, 0 ) )
    self.connect( self.cir_energy, ( self.cyclic_cir, 1 ) )

    # Cyclic convolution of CIR vector
    # Pad CIR vector: 0 x cp_len, CIR, CIR, 0 x cp_len
    self.serial_ccir = gr.vector_to_stream( gr.sizeof_float, vlen * 2 )
    self.padded_sccir = gr.stream_mux( gr.sizeof_float,
                                       [ cir_len-1, 2*vlen, cir_len-1 ] )

    if cir_len > 1:
      self.conv = gr.fir_filter_fff( 1, [ 1 ] * cir_len )
    else:
      self.conv = gr.kludge_copy( gr.sizeof_float )


    self.connect( self.padded_sccir, self.conv )

    self.null_source = gr.null_source( gr.sizeof_float )
    self.connect( self.cyclic_cir, self.serial_ccir )
    self.connect( self.null_source, ( self.padded_sccir, 0 ) )
    self.connect( self.serial_ccir, ( self.padded_sccir, 1 ) )
    self.connect( self.null_source, ( self.padded_sccir, 2 ) )


    # Extract search window
    self.search_window = ofdm.vector_sampler( gr.sizeof_float, vlen )
    periodic_trigger_seq = [ 0 ] * ( ( vlen + cir_len-1 ) * 2 )
    periodic_trigger_seq[ cir_len-1 + cir_len-1 + vlen-1 ] = 1
    self.sampler_trigsrc = gr.vector_source_b( periodic_trigger_seq, True )
    self.connect( self.conv, self.search_window )
    self.connect( self.sampler_trigsrc, ( self.search_window, 1 ) )

    # Find point of maximum energy
    self.cir_start = gr.argmax_fs( vlen )
    self.connect( self.search_window, self.cir_start )
    self.connect( ( self.cir_start, 1 ), gr.null_sink( gr.sizeof_short ) )

    # Set to zero all samples that do not belong to the CIR
    self.filtered_cir = ofdm.interp_cir_set_noncir_to_zero( vlen, cir_len )
    #self.filtered_cir = gr.kludge_copy( gr.sizeof_gr_complex * vlen )
    self.connect( self.cir_est, self.filtered_cir )
    self.connect( self.cir_start, ( self.filtered_cir, 1 ) )
    #self.connect( self.cir_start, gr.null_sink( gr.sizeof_short ) )

    # CIR -> CTF
    self.filtered_ctf = gr.fft_vcc( vlen, True, [], False ) # FFT
    self.scaled_fctf = gr.multiply_const_vcc( [1./vlen]*vlen )
    self.connect( self.filtered_cir, self.filtered_ctf )
    self.connect( self.filtered_ctf, self.scaled_fctf )

    # Output connection
    self.connect( self.scaled_fctf, self )

#    log_to_file( self, self.ch_est, "data/ch_est.float", True )
#    log_to_file( self, self.cir_est, "data/cir_est.float", True )
#    log_to_file( self, self.filtered_cir, "data/filtered_cir.float", True )
#    log_to_file( self, self.filtered_ctf, "data/filtered_ctf.float", True )
#    log_to_file( self, self.scaled_fctf, "data/scaled_filtered_ctf.float", True )
#
#    short_to_float = gr.short_to_float()
#    self.connect( self.cir_start, short_to_float )
#    log_to_file( self, short_to_float, "data/cir_start.float" )
#
#    log_to_file( self, self.padded_sccir, "data/padded_sccir.float" )
#    log_to_file( self, self.conv, "data/conv.float" )
#    log_to_file( self, self.search_window, "data/search_window.float" )


  def reset(self):
    self.ch_est.reset()
    self.sampler_trigsrc.rewind()

    cir_len = self.cir_len
    vlen = self.vlen

    self.disconnect( self.padded_sccir, self.conv )
    self.disconnect( self.conv, self.search_window )

    self.disconnect( self.null_source, ( self.padded_sccir, 0 ) )
    self.disconnect( self.serial_ccir, ( self.padded_sccir, 1 ) )
    self.disconnect( self.null_source, ( self.padded_sccir, 2 ) )


    # rebuild
    self.padded_sccir = gr.stream_mux( gr.sizeof_float,
                                       [ cir_len-1, 2*vlen, cir_len-1 ] )

    if cir_len > 1:
      self.conv = gr.fir_filter_fff( 1, [ 1 ] * cir_len )


    self.connect( self.padded_sccir, self.conv )

    self.connect( self.null_source, ( self.padded_sccir, 0 ) )
    self.connect( self.serial_ccir, ( self.padded_sccir, 1 ) )
    self.connect( self.null_source, ( self.padded_sccir, 2 ) )

    self.connect( self.conv, self.search_window )
    ###

class static_fading_channel ( gr.hier_block2 ):
  def __init__( self,
                LOS_power, no_taps, vlen, have_LOS = True ):
    gr.hier_block2.__init__( self,
        "static_fading_channel",
        gr.io_signature( 1, 1, gr.sizeof_gr_complex ),
        gr.io_signature( 1, 1, gr.sizeof_gr_complex ) )

    channel = ofdm.itpp_tdl_channel( [0]*no_taps, range(no_taps) ) #dummy  values
    channel.set_channel_profile_exponential( no_taps )
    channel.set_fading_type( ofdm.Static )

    #channel.global_rng_reset( 9 )

    if have_LOS:
      LOS_rel_power = numpy.zeros( channel.taps() )
      print LOS_rel_power
      LOS_rel_doppler = numpy.zeros( channel.taps() )
      LOS_rel_power[0] = 10**(LOS_power/10.0)
      channel.set_LOS( LOS_rel_power, LOS_rel_doppler )

    assert( channel.get_fading_type() == ofdm.Static )
    assert( channel.taps() == no_taps )

    self.connect( self, channel, self )

    #freq_resp = numpy.zeros(vlen)
    #print freq_resp
    freq_resp = channel.calc_frequency_response( vlen )
    self.freq_resp = concatenate([ freq_resp[len(freq_resp)/2:len(freq_resp)],
                                   freq_resp[0:len(freq_resp)/2] ]) # shift

    self.channel = channel
    self.vlen = vlen

  def reset(self):
    # sets init flag to false -> next sample generation triggers reset
    self.channel.set_fading_type( ofdm.Static )

    #freq_resp = numpy.zeros( self.vlen)
    freq_resp = self.channel.calc_frequency_response(self.vlen )
    self.freq_resp = concatenate([ freq_resp[len(freq_resp)/2:len(freq_resp)],
                                   freq_resp[0:len(freq_resp)/2] ]) # shift

class perfect_block_trigger ( gr.hier_block2 ):
  def __init__( self, block_length ):
    gr.hier_block2.__init__( self,
          "perfect_block_trigger",
          gr.io_signature( 0,0,0 ),
          gr.io_signature( 1, 1, gr.sizeof_char ) )

    perfect_trigger = [0]*block_length
    perfect_trigger[block_length-1] = 1
    trigger_src = gr.vector_source_b( perfect_trigger, True )

    self.connect( trigger_src, self )

    self.src = trigger_src

  def reset(self):
    self.src.rewind()

class vector_acc_se ( gr.hier_block2 ):
  def __init__( self, vlen, startup ):
    gr.hier_block2.__init__( self,
          "vector_acc_se",
          gr.io_signature( 1, 1, gr.sizeof_gr_complex * vlen ),
          gr.io_signature( 1, 1, gr.sizeof_float ) )

    squared_error_subc = gr.complex_to_mag_squared( vlen )
    squared_error_block = ofdm.vector_sum_vff( vlen )
    accumulated_squared_error = ofdm.accumulator_ff()

    if startup > 0:
      startup_skip = gr.skiphead( gr.sizeof_gr_complex * vlen, startup )
      self.connect( self, startup_skip, squared_error_subc, squared_error_block,
                    accumulated_squared_error, self )
    else:
      self.connect( self, squared_error_subc, squared_error_block,
                    accumulated_squared_error, self )

class vector_acc_se2 ( gr.hier_block2 ):
  """
  limited output (1 value)
  """
  def __init__( self, vlen, startup, window ):
    gr.hier_block2.__init__( self,
          "vector_acc_se2",
          gr.io_signature( 1, 1, gr.sizeof_gr_complex * vlen ),
          gr.io_signature( 1, 1, gr.sizeof_float ) )

    mse = ofdm.mean_squared_error( vlen, window, False, float(window) )

    if startup > 0:
      startup_skip = gr.skiphead( gr.sizeof_gr_complex * vlen, startup )
      self.connect( self, startup_skip, mse, self )
    else:
      self.connect( self, mse, self )

    self.mse = mse
    self.startup = startup

  def reset(self):
    self.mse.reset()
    if self.startup > 0:
      raise NotImplemented

class vector_acc_se3 ( gr.hier_block2 ):
  """
  limited output (1 value)
  """
  def __init__( self, startup, window ):
    gr.hier_block2.__init__( self,
          "vector_acc_se2",
          gr.io_signature( 1, 1, gr.sizeof_float),
          gr.io_signature( 1, 1, gr.sizeof_float ) )

    #mse = ofdm.mean_squared_error( vlen, window, False, float(window) )

    if startup > 0:
      startup_skip = gr.skiphead( gr.sizeof_float, startup )
      self.connect( self, startup_skip,self )
    else:
      self.odd= gr.add_const_ff(0.0)
      self.connect( self, self.odd,self )

    #self.mse = mse
    self.startup = startup

#  def reset(self):
#    self.mse.reset()
#    if self.startup > 0:
#      raise NotImplemented


class limit_stream_get_last_item( gr.hier_block2 ):
  def __init__( self, stream, N_, sink = None ):

    streamsize = determine_streamsize( stream )
    N = int(N_)

    gr.hier_block2.__init__( self,
          "limit_stream_get_last_item",
          gr.io_signature( 1, 1, streamsize ),
          gr.io_signature( 0,0,0) )

    self.sink = sink

    self.streamsize = streamsize
    self.N = N

    self.build_blocks(streamsize, N)
    self.connect_blocks()

  def build_blocks(self, streamsize, N ):
    self.skip = gr.skiphead( streamsize, N-1 )
    self.limit = gr.head( streamsize, 1 )

    if self.sink is None:
      if streamsize == gr.sizeof_char:
        self.dst = gr.vector_sink_b()
      if streamsize == gr.sizeof_float:
        self.dst = gr.vector_sink_f()
      if streamsize == gr.sizeof_short:
        self.dst = gr.vector_sink_s()
      if streamsize == gr.sizeof_gr_complex:
        self.dst = gr.vector_sink_c()
    else:
      self.dst = self.sink

  def connect_blocks(self):
    self.connect( self, self.skip, self.limit, self.dst )

  def disconnect_blocks(self):
    self.disconnect( self, self.skip, self.limit, self.dst )

  def reset(self):
    if self.sink is not None:
      raise SystemError,"Cannot reset user given sink"

    self.disconnect_blocks()
    self.build_blocks(self.streamsize, self.N)
    self.connect_blocks()

  def get_last_item(self):
    data = self.dst.data()
    assert( len(data) == 1 )
    return data[0]


class awgn_channel( gr.hier_block2 ):
  def __init__( self, snr_db, sigpow = 1.0, vlen = 1 ):
    gr.hier_block2.__init__( self,
          "awgn_channel",
          gr.io_signature( 1, 1, gr.sizeof_gr_complex * vlen ),
          gr.io_signature( 1, 1, gr.sizeof_gr_complex * vlen ) )

    snr = 10.0**(snr_db/10.0)
    noise_pow = float(sigpow) / snr

    noise_src = ofdm.complex_white_noise( 0.0, sqrt( noise_pow ) )
    if vlen > 1:
      channel = gr.add_vcc( vlen )
    else:
      channel = gr.add_cc()

    self.connect( self, channel, self )

    if vlen > 1:
      self.connect( noise_src, gr.stream_to_vector( gr.sizeof_gr_complex, vlen),
                    ( channel, 1) )
    else:
      self.connect( noise_src, ( channel, 1 ) )

class scaled_fft( gr.hier_block2 ):
  def __init__( self, vlen ):

    gr.hier_block2.__init__( self,
        "scaled_fft",
        gr.io_signature( 1, 1, gr.sizeof_gr_complex * vlen ),
        gr.io_signature( 1, 1, gr.sizeof_gr_complex * vlen ) )

    fft = gr.fft_vcc( vlen, True, [], True )
    fft_scale = gr.multiply_const_vcc( [1.0/vlen]*vlen )

    self.connect( self, fft, fft_scale, self )

class mse_simulator_av_snr( gr.hier_block2 ):
  def __init__( self, snr_db, LOS_power, no_taps, vlen, N,
                cp_len = None, startup = 0, have_LOS = True ):
    gr.hier_block2.__init__( self,
              "mse_simulator",
              gr.io_signature(0,0,0),
              gr.io_signature(0,0,0) )

    N = int( N )
    sigpow = float( vlen )

    if cp_len is None:
      cp_len = no_taps-1

    self.vlen = vlen


    self.build_blocks(vlen, cp_len, snr_db, sigpow, startup, N, LOS_power,
                      no_taps, have_LOS)

    self.connect_blocks()

  def connect_blocks(self):
    self.connect( self.block_src, self.fading_channel, self.awgn_channel,
                  self.sampler, self.fft, self.uut, self.compare, self.mean_squared_error,self.dst )
    self.connect( self.perfect_trigger, ( self.sampler, 1 ) )

  def disconnect_blocks(self):
    self.disconnect( self.block_src, self.fading_channel, self.awgn_channel,
                     self.sampler, self.fft, self.uut, self.compare, self.mean_squared_error,self.dst )
    self.disconnect( self.perfect_trigger, ( self.sampler, 1 ) )



  def build_blocks( self, vlen, cp_len, snr_db, sigpow, startup, N,
                           LOS_power, no_taps, have_LOS ):


    self.fading_channel =  \
      static_fading_channel( LOS_power, no_taps, vlen, have_LOS )

    self.freq_resp = self.fading_channel.freq_resp
    assert( len(self.freq_resp) == vlen )

    ############################################################################
    # select channel estimator to be tested herls
    #self.uut = channel_estimator_001( vlen )
    self.uut = channel_estimator_003( vlen, cp_len)
    #self.uut = snr_estimator_001( vlen)
    ############################################################################

    block = self.uut.preamble_td
    #print abs(sigpow)
    #print sum(numpy.abs(block)**2.0)/len(block)
    assert( abs( sigpow - sum(numpy.abs(block)**2.0)/len(block) ) < 1e-4 ) # power

    self.snr_lin = 10**(snr_db/10)
    if cp_len > 0:
      block = concatenate([ block[ len(block) - cp_len : len(block) ], block ])
    self.block = block

    #self.compare = gr.add_const_vcc( -1.0 * numpy.array(self.freq_resp) )
    #self.mean_squared_error = vector_acc_se2( vlen, startup, N )

    self.compare = gr.add_const_ff(-1.0 *self.snr_lin)
    self.mean_squared_error = vector_acc_se3( startup, N )
    #self.normal = gr.multiply_const_ff(1./(snr_lin**2))

    self.dst = gr.vector_sink_f()

    self.awgn_channel = awgn_channel( snr_db, sigpow )
    self.block_src = gr.vector_source_c( self.block, True )
    self.sampler = ofdm.vector_sampler( gr.sizeof_gr_complex, vlen )
    self.perfect_trigger = perfect_block_trigger( len(self.block) )
    self.fft = scaled_fft( vlen )



  def reset(self):
    self.disconnect_blocks()
    3
    self.perfect_trigger.reset()
    self.block_src.rewind()
    #self.mean_squared_error.reset()
    self.dst.clear()
    self.uut.reset()

    self.fading_channel.reset()
    self.freq_resp = self.fading_channel.freq_resp
    assert( len(self.freq_resp) == self.vlen )

    self.compare.set_k( -1.0 *self.snr_lin2 )

    self.connect_blocks()


  def get_result( self ):
    data = self.dst.data()
    assert( len(data) == 1 )
    mse = data[0]
    return mse

class mse_simulator( gr.hier_block2 ):
  def __init__( self, snr_db, LOS_power, no_taps, vlen, N,
                cp_len = None, startup = 0, have_LOS = True ):
    gr.hier_block2.__init__( self,
              "mse_simulator",
              gr.io_signature(0,0,0),
              gr.io_signature(0,0,0) )

    N = int( N )
    sigpow = float( vlen )

    if cp_len is None:
      cp_len = no_taps-1

    self.vlen = vlen


    self.build_blocks(vlen, cp_len, snr_db, sigpow, startup, N, LOS_power,
                      no_taps, have_LOS)

    self.connect_blocks()

  def connect_blocks(self):
    self.connect( self.block_src, self.fading_channel, self.awgn_channel,
                  self.sampler, self.fft, self.uut, self.compare,
                  self.mean_squared_error, self.dst )
    self.connect( self.perfect_trigger, ( self.sampler, 1 ) )

  def disconnect_blocks(self):
    self.disconnect( self.block_src, self.fading_channel, self.awgn_channel,
                     self.sampler, self.fft, self.uut, self.compare,
                     self.mean_squared_error, self.dst )
    self.disconnect( self.perfect_trigger, ( self.sampler, 1 ) )



  def build_blocks( self, vlen, cp_len, snr_db, sigpow, startup, N,
                           LOS_power, no_taps, have_LOS ):


    self.fading_channel =  \
      static_fading_channel( LOS_power, no_taps, vlen, have_LOS )

    self.freq_resp = self.fading_channel.freq_resp
    assert( len(self.freq_resp) == vlen )

    ############################################################################
    # select channel estimator to be tested her
   # self.uut = channel_estimator_003( vlen, cp_len )
    self.uut = channel_estimator_001( vlen)
    ############################################################################

    block = self.uut.preamble_td
    #print abs(sigpow)
    #print sum(numpy.abs(block)**2.0)/len(block)
    assert( abs( sigpow - sum(numpy.abs(block)**2.0)/len(block) ) < 1e-4 ) # power


    if cp_len > 0:
      block = concatenate([ block[ len(block) - cp_len : len(block) ], block ])
    self.block = block

    self.compare = gr.add_const_vcc( -1.0 * numpy.array(self.freq_resp) )
    self.mean_squared_error = vector_acc_se2( vlen, startup, N )
    self.dst = gr.vector_sink_f()

    self.awgn_channel = awgn_channel( snr_db, sigpow )
    self.block_src = gr.vector_source_c( self.block, True )
    self.sampler = ofdm.vector_sampler( gr.sizeof_gr_complex, vlen )
    self.perfect_trigger = perfect_block_trigger( len(self.block) )
    self.fft = scaled_fft( vlen )



  def reset(self):
    self.disconnect_blocks()

    self.perfect_trigger.reset()
    self.block_src.rewind()
    self.mean_squared_error.reset()
    self.dst.clear()
    self.uut.reset()

    self.fading_channel.reset()
    self.freq_resp = self.fading_channel.freq_resp
    assert( len(self.freq_resp) == self.vlen )

    self.compare.set_k( -1.0 * numpy.array(self.freq_resp) )

    self.connect_blocks()


  def get_result( self ):
    data = self.dst.data()
    assert( len(data) == 1 )
    mse = data[0]
    return mse


class data_block_src ( gr.hier_block2 ):
  def __init__( self, bits_per_subc, vlen, nblocks = 1 ):
    gr.hier_block2.__init__( self,
          "data_block_src",
          gr.io_signature(0,0,0),
          gr.io_signature( 1, 1, gr.sizeof_gr_complex * vlen ) )

    demapper = ofdm.generic_demapper_vcb(1)
    sigconst = dict()
    for i in range(1, max( bits_per_subc ) + 1 ):
      sigconst[i] = demapper.get_constellation( i )

    self.sigconst = sigconst

    self.nblocks = nblocks
    self.vlen = vlen
    self.bpsubc = bits_per_subc

    self.gen_bit_data(nblocks, vlen, bits_per_subc)
    self.build_blocks()
    self.connect_blocks()

  def gen_bit_data(self, nblocks, vlen, bpsubc ):
    fd = [0]*(nblocks*vlen)
    #bits = [0]*(nblocks*sum(bpsubc))
    bits = random_integers( 0, 1, nblocks*sum(bpsubc) )
    ind = 0
    ind_bits = 0
    for blk in range( nblocks ):
      #fd = []
      for i in range( vlen ):
        sym = 0
        for x in range( bpsubc[ i ] ):
          #bit = randint( 0, 1 )
          sym = sym*2 + bits[ind_bits]
          #bits[ind_bits] = bit
          ind_bits += 1

        fd[ind] = self.sigconst[ bpsubc[i] ][ sym ]
        ind += 1

    self.fd = fd
    self.bitdata = bits

  def build_blocks(self):
    self.ifft = gr.fft_vcc( self.vlen, False, [], True )
    self.rebuild_blocks()

  def rebuild_blocks(self):
    self.src = gr.vector_source_c( self.fd, True, self.vlen )

  def connect_blocks(self):
    self.connect( self.src, self.ifft, self )

  def disconnect_blocks(self):
    self.disconnect( self.src, self.ifft, self )

  def reset(self):
    self.disconnect_blocks()
    self.gen_bit_data(self.nblocks, self.vlen, self.bpsubc)
    self.rebuild_blocks()
    self.connect_blocks()

  def get_bitdata( self ):
    return self.bitdata


class ofdm_frame_src ( gr.hier_block2 ):
  def __init__( self, vlen, data_blocks, preamble_block, cp_len,
                framelength, bits_per_subc ):
    gr.hier_block2.__init__( self,
        "ofdm_frame_src",
        gr.io_signature(0,0,0),
        gr.io_signature( 1, 1, gr.sizeof_gr_complex ) )


    data_block_src_i = data_block_src( bits_per_subc, vlen, data_blocks )

    mux_ctrl = concatenate([[0],[1]*(framelength-1)])

    preamble_src = gr.vector_source_c( preamble_block, True, vlen )
    self.preamble_src = preamble_src

    block_mux = ofdm.static_mux_v( vlen * gr.sizeof_gr_complex, mux_ctrl )
    block_stream = ofdm.cyclic_prefixer( vlen, vlen+cp_len )

    self.connect( preamble_src, ( block_mux, 0 ) )
    self.connect( data_block_src_i, ( block_mux, 1 ) )
    self.connect( block_mux, block_stream, self )

    self.reset_blocks = [ data_block_src_i, block_mux ]
    self.src = data_block_src_i


  def reset(self):
    for x in self.reset_blocks:
      x.reset()

    self.preamble_src.rewind()

  def get_bitdata( self ):
    return self.src.get_bitdata()



class ofdm_data_block_filter ( gr.hier_block2 ):
  def __init__( self, vlen, framelength, no_preambles = 1 ):
    gr.hier_block2.__init__( self,
          "ofdm_data_block_filter",
          gr.io_signature( 1, 1, gr.sizeof_gr_complex * vlen ),
          gr.io_signature( 1, 1, gr.sizeof_gr_complex * vlen ) )

    datablock_filter = ofdm.skip( gr.sizeof_gr_complex * vlen,
                                  framelength )
    for i in range( no_preambles ):
      datablock_filter.skip( i )

    frame_trigger = ofdm_perfect_frame_trigger( framelength )

    self.connect( self, datablock_filter, self )
    self.connect( frame_trigger, ( datablock_filter, 1 ) )

    self.frame_trigger = frame_trigger

  def reset(self):
    self.frame_trigger.reset()



class ofdm_perfect_frame_trigger ( gr.hier_block2 ):
  def __init__( self, framelength ):
    gr.hier_block2.__init__( self,
          "ofdm_perfect_frame_trigger",
          gr.io_signature(0,0,0),
          gr.io_signature( 1, 1, gr.sizeof_char ) )

    frame_trigger = [0]*framelength
    frame_trigger[0] = 1
    frame_trigger = gr.vector_source_b( frame_trigger, True )
    self.connect( frame_trigger, self )

    self.frame_trigger = frame_trigger

  def reset(self):
    self.frame_trigger.rewind()



class ofdm_ber_estimator( gr.hier_block2 ):
  def __init__( self, vlen, frame_length, no_frames,
                no_preambles, bits_per_subc, bitdata_per_frame ):
    gr.hier_block2.__init__( self,
          "ofdm_ber_estimator",
          gr.io_signature( 1, 1, gr.sizeof_gr_complex * vlen ),
          gr.io_signature(0,0,0) )

    bpsubc = [0] * ( vlen * no_preambles )
    assert( len( bits_per_subc ) == vlen )
    bpsubc.extend( bits_per_subc )


    bits_per_frame = sum( bpsubc ) * ( frame_length - no_preambles )

    bm_update_trigger = [0] * frame_length
    for i in range( no_preambles + 1 ):
      bm_update_trigger[i] = 1

    bm_update_trigger = gr.vector_source_b( bm_update_trigger, True )

    demapper = ofdm.generic_demapper_vcb( vlen )
    bitmap_src = gr.vector_source_b( bpsubc, True, vlen )

    data_ref_src = gr.vector_source_b( bitdata_per_frame, True )

    compare = gr.xor_bb()
    bitstream_c2f = gr.char_to_float()
    acc_biterr = ofdm.accumulator_ff()

    window_length = bits_per_frame * no_frames
    self.N = window_length
    dst = limit_stream_get_last_item( acc_biterr, window_length )


    self.connect( self, demapper, compare, bitstream_c2f, acc_biterr, dst )
    self.connect( bitmap_src, ( demapper, 1 ) )
    self.connect( bm_update_trigger, ( demapper, 2 ) )
    self.connect( data_ref_src, ( compare, 1 ) )

    self.vector_sources = [ bm_update_trigger, bitmap_src ]
    self.acc = acc_biterr
    self.data_ref_src = data_ref_src
    self.compare = compare
    self.dst = dst


  def reset(self, bitdata_per_frame):
    for src in self.vector_sources:
      src.rewind()
    self.acc.reset()
    self.dst.reset()

    self.disconnect( self.data_ref_src, ( self.compare, 1 ) )
    self.data_ref_src = gr.vector_source_b( bitdata_per_frame, True )
    self.connect( self.data_ref_src, ( self.compare, 1 ) )

  def get_result( self ):
    data = self.dst.get_last_item() / float( self.N )
    return data



class perfect_ofdm_block_sampler ( gr.hier_block2 ):
  def __init__( self, vlen, cp_len ):
    gr.hier_block2.__init__( self,
          "perfect_ofdm_block_sampler",
          gr.io_signature( 1, 1, gr.sizeof_gr_complex ),
          gr.io_signature( 1, 1, gr.sizeof_gr_complex * vlen ) )

    sampler = ofdm.vector_sampler( gr.sizeof_gr_complex, vlen )
    perfect_trigger = perfect_block_trigger( vlen + cp_len )

    self.connect( self, sampler, self )
    self.connect( perfect_trigger, ( sampler, 1 ) )

    self.perfect_trigger = perfect_trigger

  def reset(self):
    self.perfect_trigger.reset()



class ber_simulator ( gr.hier_block2 ):
  def __init__( self, snr_db, LOS_power, no_taps, vlen, N, bits_per_subc,
                cp_len = None, startup = 0, have_LOS = True ):

    gr.hier_block2.__init__( self,
          "ber_simulator",
          gr.io_signature(0,0,0),
          gr.io_signature(0,0,0) )

    sigpow = float( vlen )

    no_frames = 1
    no_preambles = 1
    nblocks = 10
    self.vlen = vlen

    if not isinstance( bits_per_subc, ( list, tuple) ) or \
       ( len( bits_per_subc ) != vlen and len( bits_per_subc ) == 1 ):
      bits_per_subc = [ bits_per_subc ] * vlen
    else:
      assert( len( bits_per_subc ) == vlen )
      bits_per_subc = bits_per_subc

    framelength = self.calc_no_data_blocks( N, bits_per_subc, vlen ) \
                  + no_preambles

    if cp_len is None:
      cp_len = no_taps-1

    ## channel
    self.fading_channel = static_fading_channel( LOS_power, no_taps, vlen,
                                                 have_LOS )
    freq_resp = self.fading_channel.freq_resp
    assert( len( freq_resp ) == vlen )

    self.awgn_chan = awgn_channel( snr_db, sigpow )
    ## --


    ## equalizers
    self.uut = channel_estimator_002( vlen, framelength )
    block = self.uut.preamble_td
    assert( abs( sigpow - sum(numpy.abs(block)**2.0)/len(block) ) < 1e-5 ) # power

    self.optimal_equalizer = gr.multiply_const_vcc(
        [1.0 / freq_resp[i] for i in range( len( freq_resp ) ) ] )
    ## --

    self.ofdm_frame = ofdm_frame_src( vlen, nblocks, block, cp_len, framelength,
                                      bits_per_subc )

    self.perfect_block_sampler = perfect_ofdm_block_sampler( vlen, cp_len )
    self.fft = scaled_fft( vlen )

    bitdata_frame = self.ofdm_frame.get_bitdata()

    self.ber_lseq = ofdm_ber_estimator( vlen, framelength, no_frames,
                                        no_preambles, bits_per_subc,
                                        bitdata_frame )

    self.ber_opteq = ofdm_ber_estimator( vlen, framelength, no_frames,
                                         no_preambles, bits_per_subc,
                                         bitdata_frame )

    self.connect_blocks()


  def connect_blocks(self):
    self.connect( self.ofdm_frame, self.fading_channel, self.awgn_chan,
                  self.perfect_block_sampler, self.fft )

    self.connect( self.fft, self.uut, self.ber_lseq )
    self.connect( self.fft, self.optimal_equalizer, self.ber_opteq )

  def disconnect_blocks(self):
    self.disconnect( self.ofdm_frame, self.fading_channel, self.awgn_chan,
                     self.perfect_block_sampler, self.fft )

    self.disconnect( self.fft, self.uut, self.ber_lseq )
    self.disconnect( self.fft, self.optimal_equalizer, self.ber_opteq )


  def reset(self):
    #self.disconnect_blocks()

    self.ofdm_frame.reset()
    self.fading_channel.reset()
    self.perfect_block_sampler.reset()

    self.uut.reset()

    freq_resp = self.fading_channel.freq_resp
    assert( len( freq_resp ) == self.vlen )

    self.optimal_equalizer.set_k(
      [1.0 / freq_resp[i] for i in range( len( freq_resp ) ) ])

    bitdata_per_frame = self.ofdm_frame.get_bitdata()
    self.ber_lseq.reset(bitdata_per_frame)
    self.ber_opteq.reset(bitdata_per_frame)

    #self.connect_blocks()

  def get_results( self ):
    return self.ber_lseq.get_result(), self.ber_opteq.get_result()


  def calc_no_data_blocks( self, no_bits, bits_per_subc, vlen ):
    N = ceil( float( no_bits ) / sum( bits_per_subc ) )
    return int(N)



class parallel_mse_simulation_av_snr:
  def __init__( self, snr_db, LOS_power, no_taps, vlen, N,
                cp_len = None, startup = 0, parallel_sims = 1,
                have_LOS = True ):

    self.tb = gr.top_block( "test" )

    self.simulators = []
    for i in range( parallel_sims ):
      simulator = mse_simulator_av_snr(
          snr_db, LOS_power, no_taps, vlen, N, cp_len, startup, have_LOS )
      self.simulators.append( simulator )
      self.tb.connect( simulator )

    if cp_len is None:
      cp_len = no_taps-1

    self.snr_db = snr_db
    self.LOS_power = LOS_power
    self.no_taps = no_taps
    self.vlen = vlen
    self.N = N
    self.cp_len = cp_len
    self.startup = startup
    self.parallel_sims = parallel_sims
    self.have_LOS = have_LOS

  def reset(self):
    for simulator in self.simulators:
      simulator.reset()

  def run( self ):

    print "Start simulation"
    print "SNR: %f dB, no_taps = %d, vlen = %d, N = %d, cp_len = %d, startup = %d" \
      % ( self.snr_db, self.no_taps, self.vlen, int( self.N ), self.cp_len, self.startup )

    self.tb.run()

    print "End of simulation"

    results = []
    for simulator in self.simulators:
      mse = simulator.get_result()
      if verbose:
        print "Mean squared error: %f" % ( mse )
      results.append( mse )

    return results


class parallel_ber_simulation:
  def __init__ ( self,
      snr_db, LOS_power, no_taps, vlen, N, bits_per_subc,
      cp_len = None, startup = 0, parallel_sims = 1, have_LOS = True ):

    if cp_len is None:
      cp_len = no_taps-1

    self.tb = gr.top_block( "test" )
    self.simulators = []
    for i in range( parallel_sims ):
      simulator = ber_simulator( snr_db, LOS_power, no_taps, vlen, N,
                                 bits_per_subc, cp_len, startup, have_LOS )
      self.simulators.append( simulator )
      self.tb.connect( simulator )

    self.snr_db = snr_db
    self.no_taps = no_taps
    self.vlen = vlen
    self.N = N
    self.cp_len = cp_len
    self.startup = startup

  def reset(self):
    for simulator in self.simulators:
      simulator.reset()

  def run(self):
    print "Start simulation"
    print "SNR: %f dB, no_taps = %d, vlen = %d, N = %d, cp_len = %d, startup = %d" \
      % ( self.snr_db, self.no_taps, self.vlen, self.N, self.cp_len, self.startup )

    self.tb.run()

    print "End of simulation"

    uut_results = []
    opt_results = []
    for simulator in self.simulators:
      err = simulator.get_results()
      if verbose:
        print "BER unit under test:   %f" % ( err[0] )
        print "BER optimal equalizer: %f" % ( err[1] )
      uut_results.append( err[0] )
      opt_results.append( err[1] )

    return  uut_results, opt_results

class test_channel_estimator:
  def __init__ ( self ):
    pass
  def simulation_run_av_snr(self, snr_range, N_per_chan, N_per_snr, LOS_power,
                     no_taps, vlen, cp_len, startup, have_LOS=True ):

    mse_curve = []
    #var_curve = []

    parallel_sims =  10

    for snr_db in snr_range:
      results = []

      par_sim = parallel_mse_simulation_av_snr( snr_db, LOS_power, no_taps,
                                         vlen, N_per_chan, cp_len, startup,
                                         parallel_sims, have_LOS )

      for i in range( N_per_snr / parallel_sims ):
        ret = par_sim.run()
        results.extend( ret )
        par_sim.reset()

      if ( N_per_snr % parallel_sims ) > 0:
        par_sim = parallel_mse_simulation( snr_db, LOS_power, no_taps,
                                           vlen, N_per_chan, cp_len, startup,
                                           N_per_snr % parallel_sims, have_LOS )
        ret = par_sim.run()
        results.extend( ret )

      mse_curve.append( mean( results ) )
      #var_curve.append( var( results ) )

    return mse_curve#, var_curve

  def simulation_run(self, snr_range, N_per_chan, N_per_snr, LOS_power,
                     no_taps, vlen, cp_len, startup, have_LOS=True ):

    mse_curve = []
    var_curve = []

    parallel_sims =  10

    for snr_db in snr_range:
      results = []

      par_sim = parallel_mse_simulation( snr_db, LOS_power, no_taps,
                                         vlen, N_per_chan, cp_len, startup,
                                         parallel_sims, have_LOS )

      for i in range( N_per_snr / parallel_sims ):
        ret = par_sim.run()
        results.extend( ret )
        par_sim.reset()

      if ( N_per_snr % parallel_sims ) > 0:
        par_sim = parallel_mse_simulation( snr_db, LOS_power, no_taps,
                                           vlen, N_per_chan, cp_len, startup,
                                           N_per_snr % parallel_sims, have_LOS )
        ret = par_sim.run()
        results.extend( ret )

      mse_curve.append( mean( results ) )
      var_curve.append( var( results ) )

    return mse_curve, var_curve

  def simulation_run_ber(self,
        snr_range, N_per_chan, N_per_snr, LOS_power,
        no_taps, vlen, cp_len, startup, bits_per_subc, have_LOS = True ):

    opt_results = []
    uut_results = []

    parallel_sims = 5

    for snr_db in snr_range:
      ret_uut = []
      ret_opt = []

      par_sim = parallel_ber_simulation(
                  snr_db, LOS_power, no_taps, vlen, N_per_chan,
                  bits_per_subc, cp_len, startup,
                  parallel_sims, have_LOS )

      for i in range( N_per_snr / parallel_sims ):
        ret1,ret2 = par_sim.run()
        ret_uut.extend( ret1 )
        ret_opt.extend( ret2 )
        par_sim.reset()

      if ( N_per_snr % parallel_sims ) > 0:
        par_sim = parallel_ber_simulation(
                  snr_db, LOS_power, no_taps, vlen, N_per_chan,
                  bits_per_subc, cp_len, startup,
                  N_per_snr % parallel_sims, have_LOS )

        ret1,ret2 = par_sim.run()

        ret_uut.extend( ret1 )
        ret_opt.extend( ret2 )

      uut_results.append( mean( ret_uut ) )
      opt_results.append( mean( ret_opt ) )



    return uut_results, opt_results


  def print_matlab_matrix(self, mat, name):
    print "%s = [" % ( name ),
    for x in mat.keys():
      curve = mat[x]
      for y in curve:
        print "%7g," % (y),
      print ";"
    print "];"




  def start_nmse ( self ):
    N_per_chan = int( 5 )
    N_per_snr = int( 1e3 )

    cp_len = None
    startup = 0
    vlen = 256
    LOS_power = -50 # dB higher than first rayleigh path's power #10

    snr_range = range(0,25,5)

    #taps_range = [1,2,4,5,8,10,16]
    taps_range = [16]

    bits_per_subc = 2


    data = dict()
    var = dict()


    for x in taps_range:
      data[x],var[x] = self.simulation_run(snr_range, N_per_chan, N_per_snr,
                                           LOS_power, x, vlen, cp_len, startup)

    # SNR Range
    print "snr = [",
    for snr_db in snr_range:
      print "%.1f," % ( snr_db ),
    print "];"

    self.print_matlab_matrix( data, "data" )
    self.print_matlab_matrix( var, "var" )


    print "semilogy(snr,data,'x')"
    print "grid on"
    print "xlabel 'SNR (dB)'"
    print "ylabel 'MSE'"
    print "title 'Normalized MSE of channel estimator'"
    print "ylabel 'BER'"
    print "N_per_snr = %d; N_per_chan = %d;" % (N_per_snr,N_per_chan)

    print "taps_range = [",
    for x in taps_range:
      print "%d," % ( x )
    print "];"

#    print "vlen = %d; no_taps = %d; cp_len = %d; startup = %d;" \
#       % ( vlen, no_taps, cp_len or -1, startup )

  def start_nmse_av_snr ( self ):
    N_per_chan = int( 1 )
    N_per_snr = int( 1e3 )

    cp_len = None
    startup = 0
    vlen = 256
    LOS_power = -50 # dB higher than first rayleigh path's power #10

    snr_range = range(0,25,5)

    #taps_range = [1,2,4,5,8,10,16]
    taps_range = [4]

    bits_per_subc = 2


    data = dict()
    var = dict()


    for x in taps_range:
      data[x]= self.simulation_run_av_snr(snr_range, N_per_chan, N_per_snr,
                                           LOS_power, x, vlen, cp_len, startup)

    # SNR Range
    print "snr = [",
    for snr_db in snr_range:
      print "%.1f," % ( snr_db ),
    print "];"

    self.print_matlab_matrix( data, "data" )
    #self.print_matlab_matrix( var, "var" )


    print "semilogy(snr,data,'x')"
    print "grid on"
    print "xlabel 'SNR (dB)'"
    print "ylabel 'NMSE'"
    print "title 'Normalized MSE of average SNR estimator'"
    print "ylabel 'BER'"
    print "N_per_snr = %d; N_per_chan = %d;" % (N_per_snr,N_per_chan)

    print "taps_range = [",
    for x in taps_range:
      print "%d," % ( x )
    print "];"



  def start ( self ):
    N_per_chan = int( 1e8 )
    N_per_snr = int( 1e2 )

  def start_ber_sim ( self ):
    N_per_chan = int( 1e5 )
    N_per_snr = int( 1e1 )

    cp_len = None
    startup = 0
    vlen = 128
    LOS_power = 10 # dB higher than first rayleigh path's power
    have_LOS = False

    snr_range = range(0,25,5)

    taps_range = [1,2,4,5,8,10,16]

    bits_per_subc = 2

    uut_results = dict()
    opt_results = dict()


    for x in taps_range:
      uut_results[x], opt_results[x] = self.simulation_run_cmp(
          snr_range, N_per_chan, N_per_snr, LOS_power, x,
          vlen, cp_len, startup, bits_per_subc, have_LOS )

    # SNR Range
    print "snr = [",
    for snr_db in snr_range:
      print "%.1f," % ( snr_db ),
    print "];"


    self.print_matlab_matrix( uut_results, "uut_results" )
    self.print_matlab_matrix( opt_results, "opt_results" )

    print "figure"
    print "hold on"
    print "semilogy(snr,uut_results,'x')"
    print "semilogy(snr,opt_results,'o')"
    print "grid on"
    print "xlabel 'SNR (dB)'"
    print "ylabel 'BER'"
    print "N_per_snr = %d; N_per_chan = %d;" % (N_per_snr,N_per_chan)
    print "Have_LOS = ", ( "true" if have_LOS else "false")

    print "taps_range = [",
    for x in taps_range:
      print "%d, " % ( x ),
    print "];"


  def start_mse_sim ( self ):
    N_per_chan = int( 1e2 )
    N_per_snr = int( 1e2 )

    cp_len = 15
    startup = 0
    vlen = 128
    LOS_power = 10 # dB higher than first rayleigh path's power
    have_LOS = False

    snr_range = range(0,25,5)
    #snr_range=[25]

    #taps_range = [1,2,4,5,8,10,16]
    taps_range=[4]
    #taps_range=[1]

    bits_per_subc = 2

    data = dict()
    var = dict()

    for x in taps_range:
      data[x],var[x] = self.simulation_run(snr_range, N_per_chan, N_per_snr,
                                           LOS_power, x, vlen, cp_len, startup,
                                           have_LOS)

    # SNR Range
    print "snr = [",
    for snr_db in snr_range:
      print "%.1f," % ( snr_db ),
    print "];"

    self.print_matlab_matrix( data, "data" )
    self.print_matlab_matrix( var, "var" )


    print "semilogy(snr,data,'x')"
    print "grid on"
    print "xlabel 'SNR (dB)'"

    print "ylabel 'BER'"
    print "N_per_snr = %d; N_per_chan = %d;" % (N_per_snr,N_per_chan)

    print "taps_range = [",
    for x in taps_range:
      print "%d," % ( x )
    print "];"




if __name__ == '__main__':
  t = test_channel_estimator()
  #t.start_ber_sim()
  t.start_nmse_av_snr()


