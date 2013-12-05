#!/usr/bin/env python


from gnuradio import eng_notation
from gnuradio import gr, blocks
from gnuradio import fft as fft_blocks
from gnuradio import trellis
from gr_tools import log_to_file,unpack_array, terminate_stream
from numpy import concatenate
import ofdm as ofdm
from ofdm import generic_mapper_bcv  
from ofdm import puncture_bb, cyclic_prefixer, vector_padding, skip
from ofdm import sqrt_vff
from ofdm import stream_controlled_mux, reference_data_source_02_ib #reference_data_source_ib
from preambles import default_block_header
from preambles import pilot_subcarrier_inserter,pilot_block_inserter
from station_configuration import *
import common_options
import math, copy
import numpy

from ofdm import repetition_encoder_sb
from ofdm import stream_controlled_mux_b

from random import seed,randint, getrandbits

import zmqblocks


std_event_channel = "GNUradio_EventChannel" #TODO: flexible
fo=ofdm.fsm(1,2,[91,121])
print "\t\t\t\tfo=",fo

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
    config.tx_station_id       = options.station_id
    config.coding              = options.coding
    
    
    

    if config.tx_station_id is None:
      raise SystemError, "Station ID not set"

    config.frame_id_blocks     = 1 # FIXME

    # digital rms amplitude sent to USRP
    rms_amp                    = options.rms_amplitude
    self._options              = copy.copy(options)
    

    self.servants = [] # FIXME

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


    # ------------------------------------------------------------------------ #
    # Adaptive Transmitter Concept

    used_id_bits = config.used_id_bits = 10 #TODO: no constant in source code
    rep_id_bits = config.rep_id_bits = config.data_subcarriers/used_id_bits #BPSK
    if config.data_subcarriers % used_id_bits <> 0:
      raise SystemError,"Data subcarriers need to be multiple of %d" % (used_id_bits)


    ## Control Part
    if options.debug:
      self._control = ctrl = static_tx_control(options)
      print "Statix TX Control used"

    id_src = (ctrl,0)
    mux_src = (ctrl,1)
    map_src = self._map_src = (ctrl,2)
    pa_src = (ctrl,3)


    if options.log:
      id_src_f = gr.short_to_float()
      self.connect(id_src,id_src_f)
      log_to_file(self, id_src_f, "data/id_src_out.float")

      mux_src_f = gr.short_to_float()
      self.connect(mux_src,mux_src_f)
      log_to_file(self, mux_src_f, "data/mux_src_out.float")

      map_src_s = gr.vector_to_stream(gr.sizeof_char,config.data_subcarriers)
      map_src_f = gr.char_to_float()
      self.connect(map_src,map_src_s,map_src_f)
      log_to_file(self, map_src_f, "data/map_src.float")

      log_to_file(self, pa_src, "data/pa_src_out.float")

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

    ## Bitmap Update Trigger
    # TODO
    bmaptrig_stream = concatenate([[1, 1],[0]*(config.frame_data_part-2)])
    btrig = self._bitmap_trigger = blocks.vector_source_b(bmaptrig_stream.tolist(), True)
    
    if options.log:
      log_to_file(self, btrig, "data/bitmap_trig.char")
      
    ## Bitmap Update Trigger for puncturing
    # TODO
    if not options.nopunct:
        #bmaptrig_stream_puncturing = concatenate([[1],[0]*(config.frame_data_part-2)])
        bmaptrig_stream_puncturing = concatenate([[1],[0]*(config.frame_data_blocks/2-1)])
        
        btrig_puncturing = self._bitmap_trigger_puncturing = blocks.vector_source_b(bmaptrig_stream_puncturing.tolist(), True)
        bmapsrc_stream_puncturing = concatenate([[1]*dsubc,[2]*dsubc])
        bsrc_puncturing = self._bitmap_src_puncturing = blocks.vector_source_b(bmapsrc_stream_puncturing.tolist(), True, dsubc)
        
    if options.log and options.coding and not options.nopunct:
      log_to_file(self, btrig_puncturing, "data/bitmap_trig_puncturing.char")

    ## Frame Trigger
    # TODO
    ftrig_stream = concatenate([[1],[0]*(config.frame_data_part-1)])
    ftrig = self._frame_trigger = blocks.vector_source_b(ftrig_stream.tolist(),True)

    ## Data Multiplexer
    # Input 0: control stream
    # Input 1: encoded ID stream
    # Inputs 2..n: data streams
    dmux = self._data_multiplexer = stream_controlled_mux_b()
    self.connect(mux_src,(dmux,0))
    self.connect(id_enc,(dmux,1))
    self._data_multiplexer_nextport = 2

    if options.log:
      dmux_f = gr.char_to_float()
      self.connect(dmux,dmux_f)
      log_to_file(self, dmux_f, "data/dmux_out.float")
      
    ## Modulator
    mod = self._modulator = generic_mapper_bcv(config.data_subcarriers,options.coding)
    self.connect(dmux,(mod,0))
    self.connect(map_src,(mod,1))
    self.connect(btrig,(mod,2))
    mod_2 = (mod,1)

    if options.log:
      log_to_file(self, mod, "data/mod_out.compl")
      modi = gr.complex_to_imag(config.data_subcarriers)
      modr = gr.complex_to_real(config.data_subcarriers)
      self.connect(mod,modi)
      self.connect(mod,modr)
      log_to_file(self, modi, "data/mod_imag_out.float")
      log_to_file(self, modr, "data/mod_real_out.float")



    ## Power allocator
    if options.debug:

      ## static
      pa = self._power_allocator = power_allocator(config.data_subcarriers)
      self.connect(mod,(pa,0))
      self.connect(pa_src,(pa,1))


    if options.log:
      log_to_file(self, pa, "data/pa_out.compl")

#    self.connect(pa,gr.null_sink(gr.sizeof_gr_complex*dsubc))
#
#    self.connect(blocks.vector_source_c([1],True),self)
#
#    return



    # ------------------------------------------------------------------------ #
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


    if options.cheat:
      ## Artificial Channel
      # kept to compare with previous system
      achan_ir = concatenate([[1.0],[0.0]*(config.cp_length-1)])
      achan = self._artificial_channel = gr.fir_filter_ccc(1,achan_ir)
      self.connect( lastblock, achan )
      lastblock = achan


    ## Digital Amplifier
    #amp = self._amplifier = gr.multiply_const_cc(1)
    amp = self._amplifier = ofdm.multiply_const_ccf( 1.0 )
    self.connect( lastblock, amp )
    self.set_rms_amplitude(rms_amp)
    
    if options.log:
      log_to_file(self, amp, "data/amp_tx_out.compl")

    ## Setup Output
    self.connect(amp,self)

    # ------------------------------------------------------------------------ #

    # Display some information about the setup
    if config._verbose:
      self._print_verbage()
      
    #self.rpc_manager = zmqblocks.rpc_manager()
    #self.rpc_manager.set_reply_socket("tcp://*:6666")

    #self.rpc_manager.start_watcher()


  def set_rms_amplitude(self, ampl):
    """
    Sets the rms amplitude sent to the USRP
    @param: ampl 0 <= ampl < 32768
    """
    # The standard output amplitude depends on the subcarrier number. E.g.
    # if non amplified, the amplitude is sqrt(subcarriers).

    self.rms = max(0.0, min(ampl, 32767.0))
    scaled_ampl = ampl/math.sqrt(self.config.subcarriers)
    self._amplification = scaled_ampl
    self._amplifier.set_k(self._amplification)


  def add_mobile_station(self,station_id):
    """
    Adds new receiver mobile station. Station ID must be unique. Initializes
    BER reference source.
    """

    # Initialize
    id_src = self._control._id_source
    dmux = self._data_multiplexer
    port = self._data_multiplexer_nextport
    self._data_multiplexer_nextport += 1

    # Setup
    ctrl_port = self._control.add_mobile_station(station_id)
    options = self._options
    if options.imgxfer:
      ref_src = ofdm.imgtransfer_src( options.img )
    else:
      ref_src = ber_reference_source(self._options)
    
    if(options.coding):
        ## Encoder
        encoder = self._encoder = ofdm.encoder_bb(fo,0)
        unpack = self._unpack = blocks.unpack_k_bits_bb(2)
        
        ## Puncturing
        if not options.nopunct:
            puncturing = self._puncturing = puncture_bb(options.subcarriers)
            #sah = gr.sample_and_hold_bb()
            #sah_trigger = blocks.vector_source_b([1,0],True)
            #decim_sah=gr.keep_one_in_n(gr.sizeof_char,2)
            self.connect(self._bitmap_trigger_puncturing,(puncturing,2))
            frametrigger_bitmap_filter = blocks.vector_source_b([1,0],True)
            bitmap_filter = self._puncturing_bitmap_src_filter = skip(gr.sizeof_char*options.subcarriers,2)# skip_known_symbols(frame_length,subcarriers)
            bitmap_filter.skip_call(0)
            #self.connect(self._bitmap_src_puncturing,bitmap_filter,(puncturing,1))
            self.connect(self._map_src,bitmap_filter,(puncturing,1))
            self.connect(frametrigger_bitmap_filter,(bitmap_filter,1))
            #bmt = gr.char_to_float()
            #self.connect(bitmap_filter,gr.vector_to_stream(gr.sizeof_char,options.subcarriers), bmt)
            #log_to_file(self, bmt, "data/bitmap_filter_tx.float")
            
        self.connect((self._control,ctrl_port),ref_src,encoder,unpack)
        self.connect((self._control,ctrl_port+1),(ref_src,1))
        if not options.nopunct:
            self.connect(unpack,puncturing,(dmux,port))
            #self.connect(sah_trigger, (sah,1))
        else:
            self.connect(unpack,(dmux,port))
    else:
        self.connect((self._control,ctrl_port),ref_src,(dmux,port))
        #self.connect((self._control,ctrl_port),(ref_src,0))
        self.connect((self._control,ctrl_port+1),(ref_src,1))
        #self.connect(ref_src,(dmux,port))
    
    if options.log and options.coding:
        log_to_file(self, encoder, "data/encoder_out.char")
        log_to_file(self, ref_src, "data/reference_data_src.char")
        log_to_file(self, unpack, "data/encoder_unpacked_out.char")
        if not options.nopunct:
            log_to_file(self, puncturing, "data/puncturing_out.char")

# ---------------------------------------------------------------------------- #
## Relikte der alten Zeit


  def change_txpower(self,val):
    self.set_rms_amplitude(val[0])



  def get_rms_amplitude(self):
    return self.rms



# ---------------------------------------------------------------------------- #

  def add_options(normal, expert):
    """
    Adds transmitter-specific options to the Options Parser
    """
    common_options.add(normal,expert)

    normal.add_option("-a", "--rms-amplitude",
                      type="eng_float", default=1000, metavar="AMPL",
                      help="set transmitter digital rms amplitude: 0"+
                           " <= AMPL < 32768 [default=%default]")
    expert.add_option("", "--cheat", action="store_true",
              default=False,
              help="Enable channel cheating")
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
    normal.add_option(
      "", "--imgxfer",
      action="store_true", default=False,
      help="Enable IMG Transfer mode")

  # Make a static method to call before instantiation
  add_options = staticmethod(add_options)

  # TODO: update
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

    '''
################################################################################
################################################################################

class ber_reference_source (gr.hier_block2):
  """
  Provide bit stream to measure BER at receiver station.
  Input is the bitcount per frame. Outputs the exact number of bits for
  the each frame.
  """
  def __init__(self,options):
    gr.hier_block2.__init__(self, "ber_reference_source",
      gr.io_signature(1,1,gr.sizeof_int),
      gr.io_signature(1,1,gr.sizeof_char))

    ## Bitcount Source
    bc_src = (self,0)

    ## Reference Data Source
    rand_file = file('random.dat','rb')
    rand_string = rand_file.read()
    rand_file.close()
    data = [ord(rand_string[i]) for i in range(len(rand_string))]
    ref_src = self._reference_data_source = reference_data_source_ib(list(data))
    self.connect(bc_src,ref_src)

    ## Setup Output
    self.connect(ref_src,self)'''
    
    ################################################################################
################################################################################

class ber_reference_source (gr.hier_block2):
  """
  Provide bit stream to measure BER at receiver station.
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
    seed(30214345)
    rand_data = [chr(getrandbits(1)) for x in range(options.subcarriers*options.data_blocks*256)]
            
    ref_src = self._reference_data_source = reference_data_source_02_ib(rand_data)
    self.connect(id_src,(ref_src,0))
    self.connect(bc_src,(ref_src,1))

    ## Setup Output
    self.connect(ref_src,self)
    
    #log_to_file(self, ref_src, "data/ref_src.char")


################################################################################
################################################################################

class common_power_allocator (gr.hier_block2):
  """
  internal use
  """
  def __init__(self,subcarriers,operational_block):
    gr.hier_block2.__init__(self, "common_power_allocator",
      gr.io_signature2(2,2,gr.sizeof_gr_complex*subcarriers,
                           gr.sizeof_float*subcarriers),
      gr.io_signature (1,1,gr.sizeof_gr_complex*subcarriers))

    data = (self,0)
    power = (self,1)

    to_ampl = sqrt_vff(subcarriers)
    f2c = blocks.float_to_complex(subcarriers)
    adjust = operational_block

    self.connect(data,(adjust,0))
    self.connect(power,to_ampl,f2c,(adjust,1))
    self.connect(adjust, self)

################################################################################

class power_allocator (common_power_allocator):
  """
  Allocates power to subcarriers.

  It combines the complex data subcarrier stream with the real valued power
  allocation stream. Power allocation vectors are counted in energy units. The
  power is converted to the real amplitude (square root). The data is multiplied
  with the real power amplitude.

  Input 0: Data subcarriers
  Input 1: Power allocation
  Output: Power adjusted data subcarriers
  """
  def __init__(self, subcarriers):
    common_power_allocator.__init__(self, subcarriers,
                                    blocks.multiply_vcc(subcarriers))

################################################################################

class power_deallocator (common_power_allocator):
  """
  Deallocates power to subcarriers, i.e. reverts power allocation.

  Simply divides the data with the real valued power amplitude. See
  power_allocator block for detailed description of power amplitude and power
  units.

  Input 0: Data subcarriers
  Input 1: Power allocation
  Output: Power adjusted data subcarriers
  """
  def __init__(self, subcarriers):
    common_power_allocator.__init__(self,subcarriers,
                                    blocks.divide_cc(subcarriers))


################################################################################
################################################################################

class static_control ():
  def __init__(self, dsubc, frame_id_blocks, frame_data_blocks, options):
    self.static_id = range(0,256)
    self.static_idmod_map = [1] * dsubc
    self.static_idpow_map = [1.] * dsubc
    self.static_ass_map = concatenate([[1]*(dsubc/2),[0]*(dsubc/2)])
    self.static_mod_map = concatenate([[2]*(dsubc/2),[0]*(dsubc/2)])
    self.static_pow_map = concatenate([[1.]*(dsubc/2),[0.]*(dsubc/2)])


    self.mux_stream = [0]*(frame_id_blocks*dsubc)
    for k in range(frame_data_blocks):
      for j in range(dsubc):
        if self.static_ass_map[j] != 0:
          self.mux_stream.extend([self.static_ass_map[j]]*self.static_mod_map[j])    
    self.mux_stream = numpy.array(self.mux_stream)

    self.mod_stream = concatenate([[self.static_idmod_map]*frame_id_blocks,
                                   [self.static_mod_map]*frame_data_blocks])
    self.mod_stream = concatenate(self.mod_stream)

    # reduced, demapper can handle reuse count
    self.rmod_stream = concatenate([self.static_idmod_map,
                                    self.static_mod_map])

    self.rc_stream = [frame_id_blocks,frame_data_blocks]

    self.pow_stream = concatenate([[self.static_idmod_map]*frame_id_blocks,
                                    [self.static_pow_map]*frame_data_blocks])
    self.pow_stream = list( concatenate(self.pow_stream) )


class static_tx_control (gr.hier_block2):
  def __init__(self, options):
    config = station_configuration()
    dsubc = config.data_subcarriers

    gr.hier_block2.__init__(self, "static_tx_control",
      gr.io_signature (0,0,0),
      gr.io_signaturev(4,-1,[gr.sizeof_short,         # ID
                             gr.sizeof_short,         # Multiplex control stream
                             gr.sizeof_char*dsubc,    # Bit Map
                             gr.sizeof_float*dsubc,   # Power Map
                             gr.sizeof_short,
                             gr.sizeof_int ]))        # Bit count per frame

    self.control = ctrl = static_control(dsubc,config.frame_id_blocks,
                                  config.frame_data_blocks,options)

    id_out = (self,0)
    mux_out = (self,1)
    bitmap_out = (self,2)
    powmap_out = (self,3)

    bitcount_id_out = (self,4)
    self.cur_port = 4


    ## ID Source (root)
    id_src = self._id_source = blocks.vector_source_s(ctrl.static_id,True)
    self.connect(id_src,id_out)

    ## Multiplex Source
    mux_src = self._multiplex_source = blocks.vector_source_s(ctrl.mux_stream.tolist(),True)
    self.connect(mux_src,mux_out)

    ## Map Source
    map_src = blocks.vector_source_b(ctrl.rmod_stream.tolist(), True, dsubc)
    self.connect(map_src,bitmap_out)
    
    self.zmq_probe_map = zmqblocks.sink_pubsub(gr.sizeof_char*dsubc, "tcp://*:4445")
    self.connect(map_src, self.zmq_probe_map)


    ## Power Allocation Source
    pa_src = blocks.vector_source_f(ctrl.pow_stream,True,dsubc)
    self.connect(pa_src,powmap_out)
    
    self.zmq_probe_power = zmqblocks.sink_pubsub(gr.sizeof_float*dsubc, "tcp://*:4444")
    self.connect(pa_src, sqrt_vff(dsubc), self.zmq_probe_power)

#    ## Map Source
#    map_src = blocks.vector_source_b(ctrl.mod_stream,True,dsubc)
#    self.connect(map_src,(self,2))


  def add_mobile_station(self,uid):
    """
    Register mobile station with unique id \param uid
    Provides a new bitcount stream for this id. The next free port of
    the control block is used. Returns assigned output port.
    """

    config = station_configuration()
    port = self.cur_port
    self.cur_port += 2 #1

    smm = numpy.array(self.control.static_mod_map)
    sam = numpy.array(self.control.static_ass_map)

    bitcount = sum(smm[sam == uid])*config.frame_data_blocks
    
    bitcount_array = numpy.array(bitcount)

    bc_src = blocks.vector_source_i([bitcount_array.tolist()],True)
    self.connect(self._id_source,(self,port))
    self.connect(bc_src,(self,port+1))
    
    

    return port
