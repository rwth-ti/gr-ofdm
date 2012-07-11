#!/usr/bin/env python

from gnuradio import gr
from gnuradio.eng_option import eng_option

from optparse import OptionParser
from gr_tools import log_to_file,terminate_stream

import ofdm.ofdm_swig as ofdm
import numpy
import os

from station_configuration import station_configuration


class ofdm_inner_receiver( gr.hier_block2 ):
  def __init__( self, options, log = False, log_freq_off = False ):

    ## Read configuration
    config = station_configuration()
    
    fft_length    = config.fft_length
    cp_length     = config.cp_length
    block_header  = config.training_data
    data_subc     = config.data_subcarriers
    virtual_subc  = config.virtual_subcarriers
    total_subc    = config.subcarriers
    block_length  = config.block_length
    frame_length  = config.frame_length
    
    L             = block_header.mm_periodic_parts
    
    
    ## Set Input/Output signature
    gr.hier_block2.__init__( self, 
        "ofdm_inner_receiver",
        gr.io_signature(
            1, 1,
            gr.sizeof_gr_complex ),
        gr.io_signature3(
            3, 3,
            gr.sizeof_gr_complex * total_subc,    # OFDM blocks
            gr.sizeof_char,                       # Frame start
            gr.sizeof_float * total_subc ) )      # Normalized |CTF|^2 
    
    
    ## Input and output ports
    self.input = rx_input = self
    
    out_ofdm_blocks = ( self, 0 )
    out_frame_start = ( self, 1 )
    out_disp_ctf    = ( self, 2 )
    
    
    ## pre-FFT processing
    
    
    ## Compute autocorrelations for S&C preamble
    ## and cyclic prefix
    sc_metric = ofdm.autocorrelator( fft_length/2, fft_length/2 )
    gi_metric = ofdm.autocorrelator( fft_length, cp_length )
    
    self.connect( rx_input, sc_metric )
    self.connect( rx_input, gi_metric )
    
    ## Sync. Output contains OFDM blocks
    sync = ofdm.dominiks_sync_01( fft_length, cp_length )
    self.connect( rx_input, ( sync, 0 ) )
    self.connect( sc_metric, ( sync, 1 ) )
    self.connect( gi_metric, ( sync, 2 ) )
    ofdm_blocks = ( sync, 0 )
    frame_start = ( sync, 1 )
    
    if options.disable_time_sync:
      terminate_stream(self, ofdm_blocks)
      terminate_stream(self, frame_start)
      
      serial_to_parallel = gr.stream_to_vector(gr.sizeof_gr_complex,block_length)
      discard_cp = ofdm.vector_mask(block_length,cp_length,fft_length,[])
      ofdm_blocks = discard_cp
      self.connect( rx_input, serial_to_parallel, discard_cp )
      
      frame_start = [0]*frame_length
      frame_start[0] = 1
      frame_start = gr.vector_source_b(frame_start,True)
      
      print "Disabled time synchronization stage"
    

    
    
    ## Extract preamble, feed to Morelli & Mengali frequency offset estimator
    assert( block_header.mm_preamble_pos == 0 )
    morelli_foe = ofdm.mm_frequency_estimator( fft_length, L )
    sampler_preamble = ofdm.vector_sampler( gr.sizeof_gr_complex * fft_length,
                                            1 )
    self.connect( ofdm_blocks, ( sampler_preamble, 0 ) )
    self.connect( frame_start, ( sampler_preamble, 1 ) )
    self.connect( sampler_preamble, morelli_foe )
    freq_offset = morelli_foe
    
    ## Adaptive LMS FIR filtering of frequency offset
    lms_fir = ofdm.lms_fir_ff( 20, 1e-3 ) # TODO: verify parameter choice
    self.connect( freq_offset, lms_fir )
    freq_offset = self.freq_offset = lms_fir
    
    if options.disable_freq_sync:
      terminate_stream(self, freq_offset)
      freq_offset = gr.vector_source_f([0.0],True)
      print "Disabled frequency synchronization stage"
    
    ## Correct frequency shift, feed-forward structure
    frequency_shift = ofdm.frequency_shift_vcc( fft_length, -1.0/fft_length,
                                                cp_length )
    self.connect( ofdm_blocks, ( frequency_shift, 0 ) )
    self.connect( freq_offset, ( frequency_shift, 1 ) )
    self.connect( frame_start, ( frequency_shift, 2 ) )
    ofdm_blocks = frequency_shift
    
    
    
    
    ## FFT
    fft = gr.fft_vcc( fft_length, True, [], True )
    self.connect( ofdm_blocks, fft )
    ofdm_blocks = fft
    
    
    
    ## Remove virtual subcarriers
    if fft_length > data_subc:
      subcarrier_mask = ofdm.vector_mask( fft_length, virtual_subc/2,
                                           total_subc, [] )
      self.connect( ofdm_blocks, subcarrier_mask )
      ofdm_blocks = subcarrier_mask



    ## post-FFT processing
      
    
    
    ## extract channel estimation preamble from frame
    chest_pre_trigger = gr.delay( gr.sizeof_char, 
                                  1 )
    sampled_chest_preamble = \
      ofdm.vector_sampler( gr.sizeof_gr_complex * total_subc, 1 )
    self.connect( frame_start,       chest_pre_trigger )
    self.connect( chest_pre_trigger, ( sampled_chest_preamble, 1 ) )
    self.connect( ofdm_blocks,       ( sampled_chest_preamble, 0 ) )
    

    
    ## Least Squares estimator for channel transfer function (CTF)
    inv_preamble_fd = numpy.array( block_header.pilotsym_fd[ 
        block_header.channel_estimation_pilot[0] ] )
    inv_preamble_fd = 1. / inv_preamble_fd
    
    LS_channel_estimator = ofdm.multiply_const_vcc( list( inv_preamble_fd ) )
    self.connect( sampled_chest_preamble, LS_channel_estimator )
    estimated_CTF = LS_channel_estimator



    if not options.disable_ctf_enhancer:
      ## MSE enhancer
      ctf_mse_enhancer = ofdm.CTF_MSE_enhancer( total_subc, cp_length + cp_length)
      self.connect( estimated_CTF, ctf_mse_enhancer )
      
      #ifft3 = gr.fft_vcc(total_subc,False,[],True)
      #null_noise = ofdm.noise_nulling(total_subc, cp_length + cp_length)
      #ctf_mse_enhancer = gr.fft_vcc(total_subc,True,[],True)
      #ctf_mse_enhancer = ofdm.vector_mask( fft_length, virtual_subc/2,
                                          # total_subc, [] )
      #self.connect( estimated_CTF, ifft3,null_noise,ctf_mse_enhancer )
        
      estimated_CTF = ctf_mse_enhancer 
      print "Disabled CTF MSE enhancer"



    ## Postprocess the CTF estimate
    ## CTF -> inverse CTF (for equalizer)
    ## CTF -> norm |.|^2 (for CTF display)
    ctf_postprocess = ofdm.postprocess_CTF_estimate( total_subc )
    self.connect( estimated_CTF, ctf_postprocess )
    inv_estimated_CTF = ( ctf_postprocess, 0 )
    disp_CTF = ( ctf_postprocess, 1 )
    
    if options.disable_equalization:
      terminate_stream(self, inv_estimated_CTF)
      inv_estimated_CTF = gr.vector_source_f([1.]*total_subc,True,total_subc)
      print "Disabled equalization stage"


    ## Channel Equalizer
    equalizer = ofdm.channel_equalizer( total_subc )
    self.connect( ofdm_blocks,       ( equalizer, 0 ) )
    self.connect( inv_estimated_CTF, ( equalizer, 1 ) )
    self.connect( frame_start,       ( equalizer, 2 ) )
    ofdm_blocks = equalizer
    
    
    ## LMS Phase tracking
    ## Track residual frequency offset and sampling clock frequency offset

    nondata_blocks = []
    for i in range(config.frame_length):
      if i in config.training_data.pilotsym_pos:
        nondata_blocks.append(i)
        
    pilot_subc = block_header.pilot_tones
    pilot_subcarriers = block_header.pilot_subc_sym
    print "PILOT SUBCARRIERS: ", pilot_subcarriers
        
    phase_tracking = ofdm.LMS_phase_tracking3( total_subc, pilot_subc,
                                               nondata_blocks, pilot_subcarriers )
    self.connect( ofdm_blocks, ( phase_tracking, 0 ) )
    self.connect( frame_start, ( phase_tracking, 1 ) )
    
    if options.scatter_plot_before_phase_tracking:
      self.before_phase_tracking = equalizer
      
    
    if options.disable_phase_tracking:
      terminate_stream(self, phase_tracking)
      print "Disabled phase tracking stage"
    else:
      ofdm_blocks = phase_tracking
      

    
     


    ## Output connections

    self.connect( ofdm_blocks, out_ofdm_blocks )
    self.connect( frame_start, out_frame_start )
    self.connect( disp_CTF, out_disp_ctf )



    if options.log_freq_off:
      print "LOG_FREQ_OFF"
      #log_to_file( self, morelli_foe, "data/morelli_foe.float" )
      omnilogdir = os.path.expanduser('~/omnilog/')
      filee2 = omnilogdir+"freqoff.float"
      log_to_file( self, lms_fir, filee2)

    if log:
      log_to_file( self, sc_metric, "data/sc_metric.float" )
      log_to_file( self, gi_metric, "data/gi_metric.float" )
      log_to_file( self, morelli_foe, "data/morelli_foe.float" )
      log_to_file( self, lms_fir, "data/lms_fir.float" )
      log_to_file( self, sampler_preamble, "data/preamble.compl" )
      log_to_file( self, sync, "data/sync.compl" )
      log_to_file( self, frequency_shift, "data/frequency_shift.compl" )
      log_to_file( self, fft, "data/fft.compl")
      log_to_file( self, fft, "data/fft.float", mag=True )
      
      if vars().has_key( 'subcarrier_mask' ):
        log_to_file( self, subcarrier_mask, "data/subcarrier_mask.compl" )
      
      log_to_file( self, ofdm_blocks, "data/ofdm_blocks_out.compl" )
      log_to_file( self, frame_start, "data/frame_start.float", 
                   char_to_float=True )
      
      log_to_file( self, sampled_chest_preamble, 
                   "data/sampled_chest_preamble.compl" )
      log_to_file( self, LS_channel_estimator, 
                   "data/ls_channel_estimator.compl" )
      log_to_file( self, LS_channel_estimator, 
                   "data/ls_channel_estimator.float", mag=True )
      
      if "ctf_mse_enhancer" in locals(): 
        log_to_file( self, ctf_mse_enhancer, "data/ctf_mse_enhancer.compl" )
        log_to_file( self, ctf_mse_enhancer, "data/ctf_mse_enhancer.float", 
                     mag=True )
      
      log_to_file( self, (ctf_postprocess,0), "data/inc_estimated_ctf.compl" )
      log_to_file( self, (ctf_postprocess,1), "data/disp_ctf.float" )
      
      log_to_file( self, equalizer, "data/equalizer.compl" )
      log_to_file( self, equalizer, "data/equalizer.float", mag=True )
      
      log_to_file( self, phase_tracking, "data/phase_tracking.compl" )
      
    
      
    
  def add_options( normal, expert ):
    
    normal.add_option( "", "--disable-ctf-enhancer",
                       action="store_true",
                       default=True,
                       help="Disable Enhancing the MSE of CTF")
    
    expert.add_option( "", "--disable-freq-sync",
                       action="store_true",
                       default=False,
                       help="Disabling frequency synchronization stage")
    
    expert.add_option( "", "--disable-equalization",
                       action="store_true",
                       default=False,
                       help="Disabling equalization stage")
    
    expert.add_option( "", "--disable-phase-tracking",
                       action="store_true",
                       default=False,
                       help="Disabling phase tracking stage")
    
    expert.add_option( "", "--disable-time-sync",
                       action="store_true",
                       default=False,
                       help="Disabling time synchronization stage")
    expert.add_option( "", "--log-freq-off",
                       action="store_true",
                       default=False,
                       help="Log frequency offset")

  add_options = staticmethod(add_options)

