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

from gnuradio import eng_notation
from gnuradio import gr, blocks, analog, filter
from gnuradio import fft as fft_blocks
from gnuradio import trellis
from gr_tools import log_to_file,unpack_array, terminate_stream
import ofdm as ofdm
from ofdm import generic_mapper_bcv
from ofdm import puncture_bb, cyclic_prefixer, vector_padding, skip
from ofdm import stream_controlled_mux, reference_data_source_02_ib #reference_data_source_ib
from ofdm import multiply_frame_fc
from preambles import default_block_header
from preambles import pilot_subcarrier_inserter,pilot_block_inserter
import common_options
import math, copy
import numpy

from ofdm import repetition_encoder_sb
from ofdm import stream_controlled_mux_b
from ofdm import allocation_src
from station_configuration import *

from random import seed,randint, getrandbits

import zmqblocks

class transmit_path(gr.hier_block2):
  """
  output:
  - ofdm blocks, time domain (complex stream)
  """
  def __init__(self, options):
    gr.hier_block2.__init__(self, "transmit_path",
        gr.io_signature(0,0,0),
        gr.io_signature(1,1,gr.sizeof_gr_complex))

    common_options.defaults(options)

    config = self.config = station_configuration()

    config.data_subcarriers    = options.subcarriers
    config.cp_length           = options.cp_length
    config.frame_data_blocks   = options.data_blocks
    config._verbose            = options.verbose
    config.fft_length          = options.fft_length
    config.training_data       = default_block_header(config.data_subcarriers,
                                          config.fft_length,options)
    config.coding              = options.coding


    config.frame_id_blocks     = 1 # FIXME

    # digital rms amplitude sent to USRP
    rms_amp                    = options.rms_amplitude
    self._options              = copy.copy(options)


    config.block_length = config.fft_length + config.cp_length
    config.frame_data_part = config.frame_data_blocks + config.frame_id_blocks
    config.frame_length = config.frame_data_part + \
                          config.training_data.no_pilotsyms
    config.subcarriers = config.data_subcarriers + \
                         config.training_data.pilot_subcarriers
    config.virtual_subcarriers = config.fft_length - config.subcarriers

    # default values if parameters not set
    if rms_amp is None:
      rms_amp = math.sqrt(config.subcarriers)
    config.rms_amplitude = rms_amp

    # check some bounds
    if config.fft_length < config.subcarriers:
      raise SystemError, "Subcarrier number must be less than FFT length"
    if config.fft_length < config.cp_length:
      raise SystemError, "Cyclic prefix length must be less than FFT length"

    ## shortcuts
    blen = config.block_length
    flen = config.frame_length
    dsubc = config.data_subcarriers
    vsubc = config.virtual_subcarriers

    # Adaptive Transmitter Concept

    used_id_bits = config.used_id_bits = 8 #TODO: no constant in source code
    rep_id_bits = config.rep_id_bits = config.data_subcarriers/used_id_bits #BPSK
    if config.data_subcarriers % used_id_bits <> 0:
      raise SystemError,"Data subcarriers need to be multiple of %d" % (used_id_bits)

    ## Allocation Control
    self.allocation_src = allocation_src(config.data_subcarriers, config.frame_data_blocks, "tcp://*:3333")
    if options.static_allocation: #DEBUG
        # how many bits per subcarrier
        bitloading = 1
        # id's for frames
        id_vec = range(0,256)
        id_src = blocks.vector_source_s(id_vec,True,1)
        # bitloading for ID symbol and then once for data symbols
        #bitloading_vec = [1]*dsubc+[0]*(dsubc/2)+[2]*(dsubc/2)
        bitloading_vec = [1]*dsubc+[bitloading]*dsubc
        bitloading_src = blocks.vector_source_b(bitloading_vec,True,dsubc)
        # bitcount for frames
        bitcount_vec = [config.data_subcarriers*config.frame_data_blocks*bitloading]
        bitcount_src = blocks.vector_source_i(bitcount_vec,True,1)
        # power loading, here same for all symbols
        power_vec = [1]*config.data_subcarriers
        power_src = blocks.vector_source_c(power_vec,True,dsubc)
        # mux control stream to mux id and data bits
        mux_vec = [0]*dsubc+[1]*bitcount_vec[0]
        mux_ctrl = blocks.vector_source_b(mux_vec,True,1)
    else:
        id_src = (self.allocation_src,0)
        bitcount_src = (self.allocation_src,1)
        bitloading_src = (self.allocation_src,2)
        power_src = (self.allocation_src,3)
        mux_ctrl = ofdm.tx_mux_ctrl(dsubc)
        self.connect(bitcount_src,mux_ctrl)
        if options.benchmarking:
            self.allocation_src.set_allocation([4]*config.data_subcarriers,[1]*config.data_subcarriers)        


    if options.lab_special_case:
        self.allocation_src.set_allocation([0]*(config.data_subcarriers/4)+[2]*(config.data_subcarriers/2)+[0]*(config.data_subcarriers/4),[1]*config.data_subcarriers)

    if options.log:
        log_to_file(self, id_src, "data/id_src.short")
        log_to_file(self, bitcount_src, "data/bitcount_src.int")
        log_to_file(self, bitloading_src, "data/bitloading_src.char")
        log_to_file(self, power_src, "data/power_src.cmplx")

    ## GUI probe output
    zmq_probe_bitloading = zmqblocks.sink_pubsub(gr.sizeof_char*dsubc, "tcp://*:4445")
    # also skip ID symbol bitloading with keep_one_in_n (side effect)
    # factor 2 for bitloading because we have two vectors per frame, one for id symbol and one for all payload/data symbols
    # factor config.frame_data_part for power because there is one vector per ofdm symbol per frame
    self.connect(bitloading_src, blocks.keep_one_in_n(gr.sizeof_char*dsubc,2*40), zmq_probe_bitloading)
    zmq_probe_power = zmqblocks.sink_pubsub(gr.sizeof_float*dsubc, "tcp://*:4444")
    #self.connect(power_src, blocks.keep_one_in_n(gr.sizeof_gr_complex*dsubc,40), blocks.complex_to_real(dsubc), zmq_probe_power)
    self.connect(power_src, blocks.keep_one_in_n(gr.sizeof_float*dsubc,40), zmq_probe_power)

    ## Workaround to avoid periodic structure
    seed(1)
    whitener_pn = [randint(0,1) for i in range(used_id_bits*rep_id_bits)]

    ## ID Encoder
    id_enc = self._id_encoder = repetition_encoder_sb(used_id_bits,rep_id_bits,whitener_pn)
    self.connect(id_src,id_enc)

    if options.log:
      id_enc_f = gr.char_to_float()
      self.connect(id_enc,id_enc_f)
      log_to_file(self, id_enc_f, "data/id_enc_out.float")

    ## Reference Data Source
    ber_ref_src = ber_reference_source(self._options)
    self.connect(id_src,(ber_ref_src,0))
    self.connect(bitcount_src,(ber_ref_src,1))

    if options.log:
      log_to_file(self, ber_ref_src, "data/ber_rec_src_tx.char")

    ## Bitmap Update Trigger
    bmaptrig_stream = [1, 1]+[0]*(config.frame_data_part-2)
    btrig = self._bitmap_trigger = blocks.vector_source_b(bmaptrig_stream, True)

    if options.log:
      log_to_file(self, btrig, "data/bitmap_trig.char")

    ## Bitmap Update Trigger for puncturing
    if not options.nopunct:
        bmaptrig_stream_puncturing = [1]+[0]*(config.frame_data_blocks/2-1)

        btrig_puncturing = self._bitmap_trigger_puncturing = blocks.vector_source_b(bmaptrig_stream_puncturing, True)
        bmapsrc_stream_puncturing = [1]*dsubc + [2]*dsubc
        bsrc_puncturing = self._bitmap_src_puncturing = blocks.vector_source_b(bmapsrc_stream_puncturing, True, dsubc)

    if options.log and options.coding and not options.nopunct:
      log_to_file(self, btrig_puncturing, "data/bitmap_trig_puncturing.char")

    ## Frame Trigger
    ftrig_stream = [1]+[0]*(config.frame_data_part-1)
    ftrig = self._frame_trigger = blocks.vector_source_b(ftrig_stream,True)

    ## Data Multiplexer
    # Input 0: control stream
    # Input 1: encoded ID stream
    # Inputs 2..n: data streams
    dmux = self._data_multiplexer = stream_controlled_mux_b()
    self.connect(mux_ctrl,(dmux,0))
    self.connect(id_enc,(dmux,1))
    if options.benchmarking:
        self.connect(ber_ref_src,blocks.head(gr.sizeof_char, options.N),(dmux,2))
    else:
        self.connect(ber_ref_src,(dmux,2))
        

    if options.log:
      dmux_f = gr.char_to_float()
      self.connect(dmux,dmux_f)
      log_to_file(self, dmux_f, "data/dmux_out.float")

    ## Modulator
    mod = self._modulator = generic_mapper_bcv(config.data_subcarriers,options.coding)
    self.connect(dmux,(mod,0))
    self.connect(bitloading_src,(mod,1))
    self.connect(btrig,(mod,2))

    if options.log:
      log_to_file(self, mod, "data/mod_out.compl")
      modi = blocks.complex_to_imag(config.data_subcarriers)
      modr = blocks.complex_to_real(config.data_subcarriers)
      self.connect(mod,modi)
      self.connect(mod,modr)
      log_to_file(self, modi, "data/mod_imag_out.float")
      log_to_file(self, modr, "data/mod_real_out.float")

    ## Power allocator
    pa = self._power_allocator = multiply_frame_fc(config.frame_data_part, config.data_subcarriers)
    self.connect(mod,(pa,0))
    self.connect(power_src,(pa,1))

    if options.log:
      log_to_file(self, pa, "data/pa_out.compl")

    # Standard Transmitter Parts

    ## Pilot subcarriers
    psubc = self._pilot_subcarrier_inserter = pilot_subcarrier_inserter()
    self.connect(pa,psubc)

    if options.log:
      log_to_file(self, psubc, "data/psubc_out.compl")

    ## Add virtual subcarriers
    if config.fft_length > config.subcarriers:
      vsubc = self._virtual_subcarrier_extender = \
              vector_padding(config.subcarriers, config.fft_length)
      self.connect(psubc,vsubc)
    else:
      vsubc = self._virtual_subcarrier_extender = psubc

    if options.log:
      log_to_file(self, vsubc, "data/vsubc_out.compl")

    ## IFFT, no window, block shift
    ifft = self._ifft = fft_blocks.fft_vcc(config.fft_length,False,[],True)
    self.connect(vsubc,ifft)

    if options.log:
      log_to_file(self, ifft, "data/ifft_out.compl")

    ## Pilot blocks (preambles)
    pblocks = self._pilot_block_inserter = pilot_block_inserter(5,False)
    self.connect( ifft, pblocks )

    if options.log:
      log_to_file(self, pblocks, "data/pilot_block_ins_out.compl")

    ## Cyclic Prefix
    cp = self._cyclic_prefixer = cyclic_prefixer(config.fft_length,
                                                 config.block_length)
    self.connect( pblocks, cp )

    lastblock = cp

    if options.log:
      log_to_file(self, cp, "data/cp_out.compl")

    ## Digital Amplifier
    #amp = self._amplifier = gr.multiply_const_cc(1)
    amp = self._amplifier = ofdm.multiply_const_ccf( 1.0 )
    self.connect( lastblock, amp )
    self.set_rms_amplitude(rms_amp)

    if options.log:
      log_to_file(self, amp, "data/amp_tx_out.compl")



    ## Tx parameters
    bandwidth = options.bandwidth or 2e6
    bits = 8*config.data_subcarriers*config.frame_data_blocks # max. QAM256
    samples_per_frame = config.frame_length*config.block_length
    tb = samples_per_frame/bandwidth
    self.tx_parameters = {'carrier_frequency':options.tx_freq/1e9,'fft_size':config.fft_length, 'cp_size':config.cp_length \
                          , 'subcarrier_spacing':options.bandwidth/config.fft_length/1e3 \
                          ,'data_subcarriers':config.data_subcarriers, 'bandwidth':options.bandwidth/1e6 \
                          , 'frame_length':config.frame_length  \
                          , 'symbol_time':(config.cp_length + config.fft_length)/options.bandwidth*1e6, 'max_data_rate':(bits/tb)/1e6}

    ## Setup Output
    self.connect(amp,self)

    # Display some information about the setup
    if config._verbose:
      self._print_verbage()


  def get_tx_parameters(self):
    return self.tx_parameters


  def set_rms_amplitude(self, ampl):
    """
    Sets the rms amplitude sent to the USRP
    @param: ampl 0 <= ampl < 32768
    """
    # The standard output amplitude depends on the subcarrier number. E.g.
    # if non amplified, the amplitude is sqrt(subcarriers).

    self.rms = max(0.0, min(ampl, 1.0))
    scaled_ampl = ampl/math.sqrt(self.config.subcarriers)
    self._amplification = scaled_ampl
    self._amplifier.set_k(self._amplification)

  def change_txpower(self,val):
    self.set_rms_amplitude(val[0])

  def get_rms_amplitude(self):
    return self.rms

  def add_options(normal, expert):
    """
    Adds transmitter-specific options to the Options Parser
    """
    common_options.add_options(normal,expert)

    normal.add_option("-a", "--rms-amplitude",
                      type="eng_float", default=0.2, metavar="AMPL",
                      help="set transmitter digital rms amplitude: 0.0 "+
                           "<= AMPL < 1.0 [default=%default]")
    normal.add_option(
      "", "--img", type="string",
      default="ratatouille.bmp",
      help="The Bitmapfile which is tranferred[default=%default]")
    normal.add_option("", "--coding", action="store_true",
              default=False,
              help="Enable channel coding")
    normal.add_option("", "--nopunct", action="store_true",
              default=False,
              help="Disable puncturing/depuncturing")
    normal.add_option("", "--imgxfer", action="store_true", default=False,
      help="Enable IMG Transfer mode")
    expert.add_option("", "--freqoff", type="eng_float", default=None,
               help="Simulate frequency offset [default=%default]")
    expert.add_option('', '--lab-special-case', action='store_true', default=False,
                      help='For lab exercise, use only half of the subcarriers and multipath')
    expert.add_option('', '--benchmarking', action='store_true', default=False,
                      help='Modify transmitter for the benchmarking mode')


  # Make a static method to call before instantiation
  add_options = staticmethod(add_options)

  def _print_verbage(self):
    """
    Prints information about the transmit path
    """
    print "\nTransmit path:"
    print "RMS level:        %s"    % (self.rms)
    print "FFT length:       %3d"   % (self.config.fft_length)
    print "Subcarriers:      %3d"   % (self.config.subcarriers)
    print "CP length:        %3d"   % (self.config.cp_length)
    print "bits per symbol:  %3d"   % (self.src.bits_per_sym)
    print "OFDM frame_data_blocks: %3d"   % (self.config.frame_data_blocks)


################################################################################

class ber_reference_source (gr.hier_block2):
  """
  Provide bit stream to measure BER at receiver.
  Input is the bitcount per frame. Outputs the exact number of bits for
  the each frame.
  """
  def __init__(self,options):
    gr.hier_block2.__init__(self, "ber_reference_source",
      gr.io_signature2(2,2,gr.sizeof_short,
                       gr.sizeof_int),
      gr.io_signature(1,1,gr.sizeof_char))

    ## ID Source
    id_src = (self,0)
    ## Bitcount Source
    bc_src = (self,1)

    ## Reference Data Source
#    rand_file = file('random.dat','rb')
#    rand_string = rand_file.read()
#    rand_file.close()
#    rand_data = [ord(rand_string[i]) for i in range(len(rand_string))]
    # We have to use a fix seed so that Tx and Rx have the same random sequence in order to calculate BER
    seed(30214345)
    # Maximum bitloading is 8 and maximum ID is 256
    print "Generating random bits..."
    rand_data = [chr(getrandbits(1)) for x in range(options.subcarriers*8*options.data_blocks*256)]

    ref_src = self._reference_data_source = reference_data_source_02_ib(rand_data)
    self.connect(id_src,(ref_src,0))
    self.connect(bc_src,(ref_src,1))

    ## Setup Output
    self.connect(ref_src,self)


################################################################################

class static_control ():
  def __init__(self, dsubc, frame_id_blocks, frame_data_blocks, options):
    self.static_id = range(0,256)
    self.static_idmod_map = [1] * dsubc
    self.static_idpow_map = [1.0] * dsubc
    self.static_ass_map = [1]*(dsubc)
    self.static_mod_map = [1]*(dsubc)
    self.static_pow_map = [1.0]*(dsubc)


    self.mux_stream = [0]*(frame_id_blocks*dsubc)
    for k in range(frame_data_blocks):
      for j in range(dsubc):
        if self.static_ass_map[j] != 0:
          self.mux_stream.extend([self.static_ass_map[j]]*self.static_mod_map[j])
    self.mux_stream = numpy.array(self.mux_stream)

    self.mod_stream = self.static_idmod_map*frame_id_blocks + self.static_mod_map*frame_data_blocks

    # reduced, demapper can handle reuse count
    self.rmod_stream = self.static_idmod_map + self.static_mod_map

    self.rc_stream = [frame_id_blocks,frame_data_blocks]

    self.pow_stream = self.static_idmod_map*frame_id_blocks + self.static_pow_map*frame_data_blocks

