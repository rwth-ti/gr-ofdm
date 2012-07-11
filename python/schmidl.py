#!/usr/bin/env python

from numpy import concatenate, conjugate, arange
from delaylines import delayline_cc
from gnuradio import gr
from ofdm.ofdm_swig import peak_resync_bb #gate_ff
from ofdm.ofdm_swig import  vector_sum_vff
from ofdm.ofdm_swig import frequency_shift_vcc, cyclic_prefixer, schmidl_cfo_estimator
from ofdm.ofdm_swig import vector_sampler, complex_to_arg
from ofdm.ofdm_swig import sc_snr_estimator
from ofdm.ofdm_swig import vector_sum_vcc, limit_vff
import numpy, math
import ofdm.ofdm_swig as ofdm

from ofdm.ofdm_swig import accumulator_cc,accumulator_ff
from ofdm.ofdm_swig import schmidl_tm_rec_stage1,schmidl_tm_rec_stage2

from gnuradio.gr import delay

"""
schmidl's fine frequency offset estimator
resolving ambiguity in frequency offset of fractional part estimator

inputs:
- complex baseband
- sampled fract. freq. offset (one item per trigger)
- timing sync. trigger

output:
- frequency offset (float stream, one item per trigger)
- filtered timing sync. trigger
- frame trigger (marking ofdm block start)
"""
class integer_fo_estimator(gr.hier_block2):
  def __init__(self, fft_length, block_length, block_header, range, options):
    gr.hier_block2.__init__(self, "integer_fo_estimator",
      gr.io_signature3(3,3,gr.sizeof_gr_complex,gr.sizeof_float,gr.sizeof_char),
      gr.io_signature2(3,3,gr.sizeof_float,gr.sizeof_char))
    
    raise NotImplementedError,"Obsolete class"

    self._range = range

    # threshold after integer part frequency offset estimation
    # if peak value below threshold, assume false triggering
    self._thr_lo = 0.4 #0.19 # empirically found threshold. see ioe_metric.float
    self._thr_hi = 0.4 #0.2

    # stuff to be removed after bugfix for hierblock2s
    self.input = gr.kludge_copy(gr.sizeof_gr_complex)
    self.time_sync = gr.kludge_copy(gr.sizeof_char)
    self.epsilon = (self,1)
    self.connect((self,0),self.input)
    self.connect((self,2),self.time_sync)

    delay(gr.sizeof_char,
          block_header.schmidl_fine_sync[0]*block_length)

    # sample ofdm symbol (preamble 1 and 2)
    sampler_symbol1 = vector_sampler(gr.sizeof_gr_complex,fft_length)
    sampler_symbol2 = vector_sampler(gr.sizeof_gr_complex,fft_length)
    time_delay1 = delay(gr.sizeof_char,block_length*block_header.schmidl_fine_sync[1])
    self.connect(self.input, (sampler_symbol1,0))
    self.connect(self.input, (sampler_symbol2,0))
    if block_header.schmidl_fine_sync[0] > 0:
      time_delay0 = delay(gr.sizeof_char,block_length*block_header.schmidl_fine_sync[0])
      self.connect(self.time_sync, time_delay0, (sampler_symbol1,1))
    else:
      self.connect(self.time_sync, (sampler_symbol1,1))
    self.connect(self.time_sync, time_delay1, (sampler_symbol2,1))

    # negative fractional frequency offset estimate
    epsilon = gr.multiply_const_ff(-1.0)
    self.connect(self.epsilon, epsilon)

    # compensate for fractional frequency offset on per symbol base
    #  freq_shift: vector length, modulator sensitivity
    #  freq_shift third input: reset phase accumulator

    # symbol/preamble 1
    freq_shift_sym1 = frequency_shift_vcc(fft_length, 1.0/fft_length)
    self.connect(sampler_symbol1, (freq_shift_sym1,0))
    self.connect(epsilon, (freq_shift_sym1,1))
    self.connect(gr.vector_source_b([1], True), (freq_shift_sym1,2))

    # symbol/preamble 2
    freq_shift_sym2 = frequency_shift_vcc(fft_length, 1.0/fft_length)
    self.connect(sampler_symbol2, (freq_shift_sym2,0))
    self.connect(epsilon, (freq_shift_sym2,1))
    self.connect(gr.vector_source_b([1], True), (freq_shift_sym2,2))

    # fourier transfrom on both preambles
    fft_sym1 = gr.fft_vcc(fft_length, True, [], True) # Forward + Blockshift
    fft_sym2 = gr.fft_vcc(fft_length, True, [], True) # Forward + Blockshift

    # calculate schmidl's metric for estimation of freq. offset's integer part
    assert(hasattr(block_header, "schmidl_fine_sync"))
    pre1 = block_header.pilotsym_fd[block_header.schmidl_fine_sync[0]]
    pre2 = block_header.pilotsym_fd[block_header.schmidl_fine_sync[1]]
    diff_pn = concatenate([[conjugate(math.sqrt(2)*pre2[2*i]/pre1[2*i]),0.0j] for i in arange(len(pre1)/2)])
    cfo_estimator = schmidl_cfo_estimator(fft_length, len(pre1),
                                          self._range, diff_pn)
    self.connect(freq_shift_sym1, fft_sym1, (cfo_estimator,0))   # preamble 1
    self.connect(freq_shift_sym2, fft_sym2, (cfo_estimator,1))   # preamble 2

    # search for maximum and its argument in interval [-range .. +range]
    #arg_max = arg_max_vff(2*self._range + 1)
    arg_max_s = gr.argmax_fs(2*self._range+1)
    arg_max = gr.short_to_float()
    ifo_max = gr.max_ff(2*self._range + 1) # vlen
    ifo_estimate = gr.add_const_ff(-self._range)
    self.connect(cfo_estimator, arg_max_s, arg_max, ifo_estimate)
    self.connect(cfo_estimator, ifo_max)
    self.connect((arg_max_s,1),gr.null_sink(gr.sizeof_short))

    # threshold maximal value
    ifo_threshold = gr.threshold_ff(self._thr_lo, self._thr_hi, 0.0)
    ifo_thr_f2b = gr.float_to_char()
    self.connect(ifo_max, ifo_threshold, ifo_thr_f2b)

    # gating the streams ifo_estimate (integer part) and epsilon (frac. part)
    # if the metric's peak value was above the chosen threshold, assume to have
    # found a new burst. peak value below threshold results in blocking the
    # streams
    self.gate = gate_ff()
    self.connect(ifo_thr_f2b, (self.gate,0)) # threshold stream
    self.connect(ifo_estimate, (self.gate,1))
    self.connect(epsilon, (self.gate,2))


    # peak filtering
    # resynchronize and suppress peaks that didn't match a preamble
    filtered_time_sync = peak_resync_bb(True) # replace
    self.connect(self.time_sync, (filtered_time_sync,0))
    self.connect(ifo_thr_f2b, (filtered_time_sync,1))


    # find complete estimation for frequency offset
    # add together fractional and integer part
    freq_offset = gr.add_ff()
    self.connect((self.gate,1), gr.multiply_const_ff(-1.0), (freq_offset,0)) # integer offset
    self.connect((self.gate,2), (freq_offset,1)) # frac offset

    # output connections
    self.connect(freq_offset, (self,0))
    self.connect(filtered_time_sync, (self,1))
    self.connect((self.gate,0), (self,2)) # used for frame trigger


    #########################################
    # debugging
    if options.log:
      self.epsilon2_sink = gr.vector_sink_f()
      self.connect(epsilon, self.epsilon2_sink)

      self.connect(cfo_estimator, gr.file_sink(gr.sizeof_float*(self._range*2+1), "data/ioe_metric.float"))

      # output joint stream
      preamble_stream = gr.streams_to_vector(fft_length * gr.sizeof_gr_complex, 2)
      self.connect(fft_sym1, (preamble_stream,0))
      self.connect(fft_sym2, (preamble_stream,1))
      self.connect(preamble_stream, gr.file_sink(gr.sizeof_gr_complex * 2 * fft_length, "data/preambles.compl"))

      # output, preambles before and after correction, magnitude and complex spectrum
      self.connect(sampler_symbol1, gr.fft_vcc(fft_length, True, [], True), gr.file_sink(gr.sizeof_gr_complex * fft_length, "data/pre1_bef.compl"))
      self.connect(sampler_symbol1, gr.fft_vcc(fft_length, True, [], True), gr.complex_to_mag(fft_length), gr.file_sink(gr.sizeof_float * fft_length, "data/pre1_bef.float"))
      self.connect(sampler_symbol2, gr.fft_vcc(fft_length, True, [], True), gr.file_sink(gr.sizeof_gr_complex * fft_length, "data/pre2_bef.compl"))
      self.connect(sampler_symbol2, gr.fft_vcc(fft_length, True, [], True), gr.complex_to_mag(fft_length), gr.file_sink(gr.sizeof_float * fft_length, "data/pre2_bef.float"))
      self.connect(freq_shift_sym1, gr.fft_vcc(fft_length, True, [], True), gr.file_sink(gr.sizeof_gr_complex * fft_length,"data/pre1.compl"))
      self.connect(freq_shift_sym1, gr.fft_vcc(fft_length, True, [], True), gr.complex_to_mag(fft_length), gr.file_sink(gr.sizeof_float * fft_length,"data/pre1.float"))
      self.connect(freq_shift_sym2, gr.fft_vcc(fft_length, True, [], True), gr.file_sink(gr.sizeof_gr_complex * fft_length,"data/pre2.compl"))
      self.connect(freq_shift_sym2, gr.fft_vcc(fft_length, True, [], True), gr.complex_to_mag(fft_length), gr.file_sink(gr.sizeof_float * fft_length,"data/pre2.float"))

      # calculate epsilon from corrected source to check function
      test_cp = cyclic_prefixer(fft_length, block_length)
      test_eps = foe(fft_length)
      self.connect(freq_shift_sym1, test_cp, test_eps, gr.file_sink(gr.sizeof_float, "data/eps_after.float"))

    try:
        gr.hier_block.update_var_names(self, "ifo_estimator", vars())
        gr.hier_block.update_var_names(self, "ifo_estimator", vars(self))
    except:
        pass

  def _print_verbage(self):
    print "\nSchmidl IFO estimator:"
    print "CFO range:       %3d"   % (self._range)

################################################################################
################################################################################

# Timing and frequency offset estimation by Schmidl & Cox
class timing_metric(gr.hier_block2):
  def __init__(self, fft_length):
    gr.hier_block2.__init__(self, "timing_metric",
        gr.io_signature(1,1,gr.sizeof_gr_complex),
        gr.io_signature(1,1,gr.sizeof_float))

    self.input = gr.kludge_copy(gr.sizeof_gr_complex)
    self.connect(self,self.input)

    # P(d)
    nominator = schmidl_nominator(fft_length)

    # R(d)
    denominator = schmidl_denominator(fft_length)

    # |P(d)| ** 2 / (R(d)) ** 2
    p_mag_sqrd = gr.complex_to_mag_squared()
    r_sqrd = gr.multiply_ff()
    self.timing_metric = gr.divide_ff()

    self.connect(self.input, nominator, p_mag_sqrd, (self.timing_metric,0))
    self.connect(self.input, denominator, (r_sqrd,0))
    self.connect(denominator, (r_sqrd,1))
    self.connect(r_sqrd, (self.timing_metric,1))
    self.connect(self.timing_metric, self)

    # calculate epsilon from P(d), epsilon is normalized fractional frequency offset
    #angle = gr.complex_to_arg()
    #self.epsilon = gr.multiply_const_ff(1.0/math.pi)
    #self.connect(nominator, angle, self.epsilon)

    try:
        gr.hier_block.update_var_names(self, "schmidl", vars())
        gr.hier_block.update_var_names(self, "schmidl", vars(self))
    except:
        pass

################################################################################
################################################################################

class recursive_timing_metric( gr.hier_block2 ):
  def __init__ ( self, fft_length ):
    gr.hier_block2.__init__(self, "recursive_timing_metric",
        gr.io_signature(1,1,gr.sizeof_gr_complex),
        gr.io_signature(1,1,gr.sizeof_float))
    
    input = (self,0)
    output = (self,0)
    
    st1 = schmidl_tm_rec_stage1(fft_length)
    st2 = schmidl_tm_rec_stage2(fft_length/2)
    
    self.connect(input,st1,st2,output)
    self.connect((st1,1),(st2,1))
    

class recursive_timing_metric_simple( gr.hier_block2 ):
  def __init__ ( self, fft_length ):
    gr.hier_block2.__init__(self, "recursive_timing_metric",
        gr.io_signature(1,1,gr.sizeof_gr_complex),
        gr.io_signature(1,1,gr.sizeof_float))
    
    self.input = gr.kludge_copy(gr.sizeof_gr_complex)
    self.connect(self, self.input)
    
    # P(d) = sum(0 to L-1, conj(delayed(r)) * r)
    conj = gr.conjugate_cc()
    mixer = gr.multiply_cc()
    mix_delay = delay(gr.sizeof_gr_complex,fft_length/2+1)
    mix_diff = gr.sub_cc()
    nominator = accumulator_cc()
    inpdelay = delay(gr.sizeof_gr_complex,fft_length/2)
    
    self.connect(self.input, inpdelay, 
                 conj, (mixer,0))
    self.connect(self.input, (mixer,1))
    self.connect(mixer,(mix_diff,0))
    self.connect(mixer, mix_delay, (mix_diff,1))
    self.connect(mix_diff,nominator)
    
    rmagsqrd = gr.complex_to_mag_squared()
    rm_delay = delay(gr.sizeof_float,fft_length+1)
    rm_diff = gr.sub_ff()
    denom = accumulator_ff()
    self.connect(self.input,rmagsqrd,rm_diff,gr.multiply_const_ff(0.5),denom)
    self.connect(rmagsqrd,rm_delay,(rm_diff,1))
    
    
    ps = gr.complex_to_mag_squared()
    rs = gr.multiply_ff()
    self.connect(nominator,ps)
    self.connect(denom,rs)
    self.connect(denom,(rs,1))
    
    div = gr.divide_ff()
    self.connect(ps,div)
    self.connect(rs,(div,1))
    
    self.connect(div,self)
    

class modified_timing_metric(gr.hier_block2):
  def __init__(self, fft_length, pn_weights):
    gr.hier_block2.__init__(self, "modified_timing_metric",
        gr.io_signature(1,1,gr.sizeof_gr_complex),
        gr.io_signature(1,1,gr.sizeof_float))

    assert(len(pn_weights) == fft_length)
    p = [pn_weights[fft_length-i-1]*pn_weights[fft_length/2-i-1]
         for i in range(fft_length/2)]
    tm1 = ofdm.schmidl_tm_s1(fft_length)
    tm2 = ofdm.schmidl_tm_s2(fft_length,p)

    self.connect(self,tm1,tm2,self)
    self.connect((tm1,1),(tm2,1))


class modified_timing_metric_old(gr.hier_block2):
  def __init__(self, fft_length, pn_weights):
    gr.hier_block2.__init__(self, "modified_timing_metric",
        gr.io_signature(1,1,gr.sizeof_gr_complex),
        gr.io_signature(1,1,gr.sizeof_float))

    assert(len(pn_weights) == fft_length)

    self.input = gr.kludge_copy(gr.sizeof_gr_complex)
    self.connect(self,self.input)

    # P(d) = sum(0 to L-1, conj(delayed(r)) * r)
    conj = gr.conjugate_cc()
    mixer = gr.multiply_cc()
    nominator = gr.fir_filter_ccf(1,[pn_weights[fft_length-i-1]*pn_weights[fft_length/2-i-1] for i in range(fft_length/2)])

    self.connect(self.input, delay(gr.sizeof_gr_complex,fft_length/2), conj, (mixer,0))
    self.connect(self.input, (mixer,1))
    self.connect(mixer, nominator)
    # moving_avg = P(d)

    # R(d)
    denominator = schmidl_denominator(fft_length)

    # |P(d)| ** 2 / (R(d)) ** 2
    p_mag_sqrd = gr.complex_to_mag_squared()
    r_sqrd = gr.multiply_ff()
    self.timing_metric = gr.divide_ff()

    self.connect(nominator, p_mag_sqrd, (self.timing_metric,0))
    self.connect(self.input, denominator, (r_sqrd,0))
    self.connect(denominator, (r_sqrd,1))
    self.connect(r_sqrd, (self.timing_metric,1))
    self.connect(self.timing_metric, self)

    # calculate epsilon from P(d), epsilon is normalized fractional frequency offset
    #angle = gr.complex_to_arg()
    #self.epsilon = gr.multiply_const_ff(1.0/math.pi)
    #self.connect(nominator, angle, self.epsilon)

################################################################################
################################################################################


class coarse_frequency_offset_estimator(gr.hier_block2):
  """
  Coarse Frequency Offset Estimator by Schmidl & Cox

  It calculates an estimate for the fractional, i.e. the coarse, frequency
  offset. The method described in the S&C paper is applied.

  Input 0: Complex baseband
  Input 1: Trigger signal

  Output: Estimate of fractional frequency offset, one value per trigger
  """
  def __init__(self, vlen):
    gr.hier_block2.__init__(self, "coarse_frequency_offset_estimation",
        gr.io_signature2(2,2,gr.sizeof_gr_complex,gr.sizeof_char),
        gr.io_signature (1,1,gr.sizeof_float))

    ## Preamble Extraction
    sampler = vector_sampler(gr.sizeof_gr_complex,vlen)
    self.connect(self,sampler)
    self.connect((self,1),(sampler,1))

    ## Split block into two parts
    splitter = gr.vector_to_streams(gr.sizeof_gr_complex*vlen/2,2)
    self.connect(sampler,splitter)

    ## Conjugate first half block
    conj = gr.conjugate_cc(vlen/2)
    self.connect(splitter,conj)

    ## Vector multiplication of both half blocks
    vmult = gr.multiply_vcc(vlen/2)
    self.connect(conj,vmult)
    self.connect((splitter,1),(vmult,1))

    ## Sum of Products
    psum = vector_sum_vcc(vlen/2)
    self.connect(vmult,psum)

    ## Complex to Angle
    angle = complex_to_arg()
    self.connect(psum,angle)

    ## Normalize
    norm = gr.multiply_const_ff(1.0/math.pi)
    self.connect(angle,norm)

    ## Setup Output Connections
    self.connect(norm,self)


class snr_estimator(gr.hier_block2):
  """
  SNR Estimator by Schmidl & Cox

  The method described in the S&C paper is applied.

  Input 0: Complex baseband
  Input 1: Trigger signal

  Output: Estimate of SNR, one value per trigger
  """
  def __init__(self, vlen):
    gr.hier_block2.__init__(self, "snr_estimator",
        gr.io_signature2(2,2,gr.sizeof_gr_complex,gr.sizeof_char),
        gr.io_signature (1,1,gr.sizeof_float))
    
    data_in = (self,0)
    trig_in = (self,1)
    snr_out = (self,0)

    ## Preamble Extraction
    sampler = vector_sampler(gr.sizeof_gr_complex,vlen)
    self.connect(data_in,sampler)
    self.connect(trig_in,(sampler,1))
    
    ## Algorithm implementation
    estim = sc_snr_estimator(vlen)
    self.connect(sampler,estim)
    self.connect(estim,snr_out)
    
    return 
  
  
  

    ## Split block into two parts
    splitter = gr.vector_to_streams(gr.sizeof_gr_complex*vlen/2,2)
    self.connect(sampler,splitter)

    ## Conjugate first half block
    conj = gr.conjugate_cc(vlen/2)
    self.connect(splitter,conj)

    ## Vector multiplication of both half blocks
    vmult = gr.multiply_vcc(vlen/2)
    self.connect(conj,vmult)
    self.connect((splitter,1),(vmult,1))

    ## Sum of Products
    psum = vector_sum_vcc(vlen/2)
    self.connect(vmult,psum)

    ## Magnitude of P(d)
    p_mag = gr.complex_to_mag()
    self.connect(psum,p_mag)

    ## Squared Magnitude of block
    r_magsqrd = gr.complex_to_mag_squared(vlen)
    self.connect(sampler,r_magsqrd)

    ## Sum of squared second half block
    r_sum = vector_sum_vff(vlen)
    self.connect(r_magsqrd,r_sum)

    ## Square Root of Metric
    m_sqrt = gr.divide_ff()
    self.connect(p_mag,(m_sqrt,0))
    self.connect(r_sum,gr.multiply_const_ff(0.5),(m_sqrt,1))

    ## Denominator of SNR estimate
    denom = gr.add_const_ff(1)
    neg_m_sqrt = gr.multiply_const_ff(-1.0)
    self.connect(m_sqrt,limit_vff(1,1-2e-5,-1000),neg_m_sqrt,denom)

    ## SNR estimate
    snr_est = gr.divide_ff()
    self.connect(m_sqrt,(snr_est,0))
    self.connect(denom,(snr_est,1))

    ## Setup Output Connections
    self.connect(snr_est,self)


class foe(gr.hier_block2):
  def __init__(self, fft_length):
    gr.hier_block2.__init__(self, "foe",
        gr.io_signature2(2,2,gr.sizeof_gr_complex,gr.sizeof_char),
        gr.io_signature(1,1,gr.sizeof_float))

    self.input = (self,0)
    self.time_sync = (self,1)

    # P(d)
    self.nominator = schmidl_nominator(fft_length)

    # sample nominator
    sampler = vector_sampler(gr.sizeof_gr_complex,1)
    self.connect(self.input, self.nominator, (sampler,0))
    self.connect(self.time_sync, (sampler,1))

    # calculate epsilon from P(d), epsilon is normalized fractional frequency offset
    angle = complex_to_arg()
    self.epsilon = gr.multiply_const_ff(1.0/math.pi)

    self.connect(sampler, angle, self.epsilon, self)

    try:
        gr.hier_block.update_var_names(self, "foe", vars())
        gr.hier_block.update_var_names(self, "foe", vars(self))
    except:
        pass

################################################################################
################################################################################

class schmidl_nominator(gr.hier_block2):
  def __init__(self, fft_length):
    gr.hier_block2.__init__(self, "schmidl_nominator",
        gr.io_signature(1,1,gr.sizeof_gr_complex),
        gr.io_signature(1,1,gr.sizeof_gr_complex))

    self.input=gr.kludge_copy(gr.sizeof_gr_complex)

    # P(d) = sum(0 to L-1, conj(delayed(r)) * r)
    conj = gr.conjugate_cc()
    mixer = gr.multiply_cc()
    moving_avg = gr.fir_filter_ccf(1,[1.0 for i in range(fft_length/2)])

    self.connect(self, self.input, delay(gr.sizeof_gr_complex,fft_length/2), conj, (mixer,0))
    self.connect(self.input, (mixer,1))
    self.connect(mixer, moving_avg, self)
    # moving_avg = P(d)
    try:
        gr.hier_block.update_var_names(self, "schmidl_nom", vars())
        gr.hier_block.update_var_names(self, "schmidl_nom", vars(self))
    except:
        pass

################################################################################
################################################################################

class schmidl_denominator(gr.hier_block2):
  def __init__(self, fft_length):
    gr.hier_block2.__init__(self, "schmidl_denominator",
        gr.io_signature(1,1,gr.sizeof_gr_complex),
        gr.io_signature(1,1,gr.sizeof_float))

    # R(d) = sum(0 to L-1, |r_d|**2)
    r_mag_sqrd = gr.complex_to_mag_squared()
    r_mov_avg = gr.fir_filter_fff(1,[0.5 for i in range(fft_length)])
    #r_mov_avg_half = gr.multiply_const_ff(0.5)
    #r_mov_avg = moving_sum_cc(fft_length)

    self.connect(self, r_mag_sqrd, r_mov_avg, self)
    # r_mov_avg = R(d)

    try:
        gr.hier_block.update_var_names(self, "schmidl_denom", vars())
        gr.hier_block.update_var_names(self, "schmidl_denom", vars(self))
    except:
        pass
