#!/usr/bin/env python

from numpy import concatenate
from gnuradio import gr
from gnuradio.eng_option import eng_option
from ofdm import frequency_shift_vcc
from ofdm import vector_sampler, peak_detector2_fb
from ofdm import vector_mask
from gnuradio.gr import delay
from optparse import OptionParser
import schmidl
from gr_tools import log_to_file,terminate_stream
from morelli import morelli_foe

import ofdm


class ofdm_receiver(gr.hier_block2):
  """
  input: complex baseband
  output: extracted frequency-offset corrected ofdm symbols
          second stream, bytes, 1 if ofdm sym is first preamble, 0 else
          consume second stream at same rate as first stream!
  """
  def __init__(self, fft_length, block_length, frame_data_part, block_header,
               options):
    gr.hier_block2.__init__(self, "ofdm_receiver",
        gr.io_signature (1,1,gr.sizeof_gr_complex),
        gr.io_signature2(2,2,gr.sizeof_gr_complex*fft_length,
                             gr.sizeof_char))

    
    frame_length = frame_data_part + block_header.no_pilotsyms
    cp_length = block_length-fft_length
    
    

    self.input=gr.kludge_copy(gr.sizeof_gr_complex)
    self.connect(self, self.input)
    
    self.blocks_out = (self,0)
    self.frame_trigger_out = (self,1)
    self.snr_out = (self,2)


    if options.log:
      log_to_file(self, self.input, "data/receiver_input.compl")



    # peak detector: thresholds low, high
    #self._pd_thres_lo = 0.09
    #self._pd_thres_hi = 0.1
    self._pd_thres = 0.2
    self._pd_lookahead = fft_length / 2 # empirically chosen
    
    

    #########################
    # coarse timing offset estimator
#    self.tm = schmidl.modified_timing_metric(fft_length,[1]*(fft_length))
    self.tm = schmidl.recursive_timing_metric(fft_length)
    self.connect(self.input,self.tm)
    assert(hasattr(block_header, 'sc_preamble_pos'))
    assert(block_header.sc_preamble_pos == 0) # TODO: relax this restriction
    
    if options.filter_timingmetric:
      timingmetric_shift = -2 #int(-cp_length * 0.8)
      tmfilter = gr.fir_filter_fff(1, [1./cp_length]*cp_length)
      self.connect( self.tm, tmfilter )
      self.timing_metric = tmfilter
      print "Filtering timing metric, experimental"
    else:
      self.timing_metric = self.tm
      timingmetric_shift = int(-cp_length/4)
    
    if options.log:
      log_to_file(self, self.timing_metric, "data/tm.float")
        


    # peak detection
    #threshold = gr.threshold_ff(self._pd_thres_lo,self._pd_thres_hi,0)
    #muted_tm = gr.multiply_ff()
    peak_detector = peak_detector2_fb(self._pd_lookahead, self._pd_thres)
    #self.connect(self.timing_metric, threshold, (muted_tm,0))
    #self.connect(self.timing_metric, (muted_tm,1))
    #self.connect(muted_tm, peak_detector)
    self.connect(self.timing_metric, peak_detector)

    if options.log:
      pd_float = gr.char_to_float()
      self.connect(peak_detector,pd_float)
      log_to_file(self, pd_float, "data/peakdetector.float")
      
    if options.no_timesync:
      terminate_stream( self, peak_detector )
      trigger = [0]*(frame_length*block_length)
      trigger[ block_length-1 ] = 1
      peak_detector = gr.vector_source_b( trigger, True )
      print "Bypassing timing synchronisation"
    
    
    # TODO: refine detected peaks with 90% average method as proposed
    # from Schmidl & Cox:
    # Starting from peak, find first points to the left and right whose
    # value is less than or equal 90% of the peak value. New trigger point
    # is average of both
    
    
    
    
    
    # Frequency Offset Estimation
    # Used: Algorithm as proposed from Morelli & Mengali
    # Idea: Use periodic preamble, correlate identical parts, determine
    # phase offset. This phase offset is a function of the frequency offset.
    
    assert(hasattr(block_header, 'mm_preamble_pos'))

    foe = morelli_foe(fft_length,block_header.mm_periodic_parts)
    self.connect(self.input,(foe,0))
    
    if block_header.mm_preamble_pos > 0:
      delayed_trigger = gr.delay(gr.sizeof_char,
                                 block_header.mm_preamble_pos*block_length)
      self.connect(peak_detector,delayed_trigger,(foe,1))
    else:
      self.connect(peak_detector,(foe,1))
    
    self.freq_offset = foe

    if options.log:
      log_to_file(self, self.freq_offset, "data/freqoff_out.float")
      
      
    if options.average_freqoff:
      #avg_foe = gr.single_pole_iir_filter_ff( 0.1 )
      avg_foe = ofdm.lms_fir_ff( 20, 1e-3 )
      self.connect( self.freq_offset, avg_foe )
      self.freq_offset = avg_foe
      #log_to_file( self, avg_foe, "data/freqoff_out_avg.float" )
      print "EXPERIMENTAL!!! Filtering frequency offset estimate"
      
    
    if options.no_freqsync:
      terminate_stream( self, self.freq_offset )
      self.freq_offset = gr.vector_source_f( [0.0], True )
      print "Bypassing frequency offset estimator, offset=0.0"
      
    
    # TODO: dynamic solution
    frametrig_seq = concatenate([[1],[0]*(frame_length-1)])
    self.time_sync = peak_detector
    self.frame_trigger = gr.vector_source_b(frametrig_seq,True)
    self.connect(self.frame_trigger, self.frame_trigger_out)
    




    ##########################
    # symbol extraction and processing
    #  First, we extract the whole ofdm block, then we divide this block into
    #  several ofdm symbols. This asserts that all symbols belonging to the
    #  same ofdm block will be a consecutive order.
    #  extract ofdm symbols
    #  compensate frequency offset

    # TODO: use PLL and update/reset signals
    delayed_timesync = gr.delay(gr.sizeof_char,
                                (frame_length-1)*block_length+timingmetric_shift)
    self.connect( self.time_sync, delayed_timesync )
    
    self.block_sampler = vector_sampler(gr.sizeof_gr_complex,block_length*frame_length)
    self.discard_cp = vector_mask(block_length,cp_length,fft_length,[])

    
    if options.use_dpll:
      dpll = gr.dpll_bb( frame_length * block_length , .01 )
      self.connect( delayed_timesync, dpll )
      
      if options.log:
        dpll_f = gr.char_to_float()
        delayed_timesync_f = gr.char_to_float()
        self.connect( dpll, dpll_f )
        self.connect( delayed_timesync, delayed_timesync_f )
        log_to_file( self, dpll_f, "data/dpll.float" )
        log_to_file( self, delayed_timesync_f, "data/dpll_in.float" )
        
      delayed_timesync = dpll
      print "Using DPLL, EXPERIMENTAL!!!!!"

    self.connect(self.input,self.block_sampler)
    self.connect(delayed_timesync,(self.block_sampler,1))
    
    if options.log:
      log_to_file(self, self.block_sampler, "data/block_sampler_out.compl")



    # TODO: dynamic solution
    self.ofdm_symbols = gr.vector_to_stream(gr.sizeof_gr_complex*block_length,
                                            frame_length)
    self.connect(self.block_sampler,self.ofdm_symbols,self.discard_cp)

    if options.log:
      log_to_file(self, self.discard_cp, "data/discard_cp_out.compl")
      dcp_fft = gr.fft_vcc(fft_length, True, [], True)
      self.connect(self.discard_cp,dcp_fft)
      log_to_file(self, dcp_fft, "data/discard_cp_fft.compl")


    # reset phase accumulator inside freq_shift on every block start
    # setup output connection


    freq_shift = frequency_shift_vcc(fft_length, -1.0/fft_length, cp_length)

    self.connect(self.discard_cp,(freq_shift,0))
    self.connect(self.freq_offset,(freq_shift,1))
    self.connect(self.frame_trigger,(freq_shift,2))
    self.connect(freq_shift, self.blocks_out)
    
    if options.log:
      log_to_file(self, freq_shift, "data/freqshift_out.compl")
      
    if options.no_freqshift:
      terminate_stream( self, freq_shift )
      freq_shift = self.discard_cp
      print "Bypassing frequency shift block"
      


  def _print_verbage(self):
    print "\nOFDM Receiver:"

  def add_options(normal, expert):
    expert.add_option("", "--no-timesync", action="store_true",
                      default=False,
                      help = "Debug time synchronisation, replace estimator"+
                             " with static fixed spaced trigger")
    
    expert.add_option("", "--no-freqsync", action="store_true",
                      default=False,
                      help = "Debug frequency synchronisation, replace estimator"+
                             " with fixed offset 0.0")
    
    expert.add_option("", "--no-freqshift", action="store_true",
                      default=False,
                      help="Debug frequency shift block, bypass")
    
    expert.add_option("", "--use-dpll", action="store_true",
                      default=False,
                      help="Enable digital PLL")
    
    expert.add_option("", "--average-freqoff", action="store_true",
                      default=False,
                      help="Experimental filtering/averaging of frequency "+
                           "offset estimate")
    
    expert.add_option("", "--filter-timingmetric", action="store_true",
                      default=False,
                      help="Enable filtering of timing metric")
    
  add_options = staticmethod(add_options)

