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

from gnuradio import gr
import math
from numpy import concatenate

from gr_tools import log_to_file

from ofdm import skip, vector_sum_vff, static_mux_v, sinr_interpolator, sinr_estimator, sinr_estimator_02
from gnuradio.blocks import null_sink, divide_ff, add_const_vff, add_vff

from gnuradio import blocks, filter

from station_configuration import *



class milans_snr_estimator(gr.hier_block2):
  """
  Based on Milans idea (to be published)

  rho_hat = ((skip-1)*sum(|Y1_k|^2)/sum(|Y0_k|^2) -1)*(1/skip)
  where
   Y_1 is the received Morelli preamble signal in frequency domain (on used subcarriers)
   Y_0 is the received Morelli preamble signal in frequency domain (on non-used subcarriers)
   skip is the number of periodic parts in the Morelli preamble symbol (eg 2, 4, 8)
  """
  def __init__(self, subc, vlen, ss):
    gr.hier_block2.__init__(self, "new_snr_estimator",
        gr.io_signature(1,1,gr.sizeof_gr_complex*vlen),
        gr.io_signature(1,1,gr.sizeof_float))

    print "Created Milan's SNR estimator"

    trigger = [0]*vlen
    trigger[0] = 1


    u = range (vlen/ss*(ss-1))
    zeros_ind= map(lambda z: z+1+z/(ss-1),u)

    skip1 = skip(gr.sizeof_gr_complex,vlen)
    for x in zeros_ind:
      skip1.skip(x)

    #print "skipped zeros",zeros_ind

    v = range (vlen/ss)
    ones_ind= map(lambda z: z*ss,v)

    skip2 = skip(gr.sizeof_gr_complex,vlen)
    for x in ones_ind:
      skip2.skip(x)

    #print "skipped ones",ones_ind

    v2s = gr.vector_to_stream(gr.sizeof_gr_complex,vlen)
    s2v1 = gr.stream_to_vector(gr.sizeof_gr_complex,vlen/ss)
    trigger_src_1 = gr.vector_source_b(trigger,True)

    s2v2 = gr.stream_to_vector(gr.sizeof_gr_complex,vlen/ss*(ss-1))
    trigger_src_2 = gr.vector_source_b(trigger,True)

    mag_sq_ones = gr.complex_to_mag_squared(vlen/ss)
    mag_sq_zeros = gr.complex_to_mag_squared(vlen/ss*(ss-1))

    filt_ones = gr.single_pole_iir_filter_ff(0.1,vlen/ss)
    filt_zeros = gr.single_pole_iir_filter_ff(0.1,vlen/ss*(ss-1))

    sum_ones = vector_sum_vff(vlen/ss)
    sum_zeros = vector_sum_vff(vlen/ss*(ss-1))

    D = gr.divide_ff()
    P = gr.multiply_ff()
    mult1 = gr.multiply_const_ff(ss-1.0)
    add1 = gr.add_const_ff(-1.0)
    mult2 = gr.multiply_const_ff(1./ss)
    scsnrdb = gr.nlog10_ff(10,1,0)
    filt_end = gr.single_pole_iir_filter_ff(0.1)

    self.connect(self,v2s,skip1,s2v1,mag_sq_ones,filt_ones,sum_ones)
    self.connect(trigger_src_1,(skip1,1))

    self.connect(v2s,skip2,s2v2,mag_sq_zeros,filt_zeros,sum_zeros)
    self.connect(trigger_src_2,(skip2,1))

    self.connect(sum_ones,D)
    self.connect(sum_zeros,(D,1))
    self.connect(D,mult1,add1,mult2)

    self.connect(mult2,scsnrdb,filt_end,self)



################################################################################
################################################################################

#class milans_sinr_sc_estimator(gr.hier_block2):
#  """
#  Based on Milans idea (to be published)
#
#  rho_hat = ((skip-1)*sum(|Y1_k|^2)/sum(|Y0_k|^2) -1)*(1/skip)
#  where
#   Y_1 is the received Morelli preamble signal in frequency domain (on used subcarriers)
#   Y_0 is the received Morelli preamble signal in frequency domain (on non-used subcarriers)
#   skip is the number of periodic parts in the Morelli preamble symbol (eg 2, 4, 8)
#  """
#  def __init__(self, subc, vlen, ss):
#    gr.hier_block2.__init__(self, "new_snr_estimator",
#        gr.io_signature(2,2,gr.sizeof_gr_complex*vlen),
#        #gr.io_signature2(2,2,gr.sizeof_float*vlen/ss*(ss-1),gr.sizeof_float*vlen/ss))
#        gr.io_signature(1,1,gr.sizeof_float*vlen))
#
#    print "Created Milan's SNR estimator"
#
#    trigger = [0]*vlen
#    trigger[0] = 1
#
#
#    u = range (vlen/ss*(ss-1))
#    zeros_ind= map(lambda z: z+1+z/(ss-1),u)
#
#    skip1_pr0 = skip(gr.sizeof_gr_complex,vlen)
#    skip1_pr1 = skip(gr.sizeof_gr_complex,vlen)
#    for x in zeros_ind:
#      skip1_pr0.skip(x)
#      skip1_pr1.skip(x)
#
#    #print "skipped zeros",zeros_ind
#
#    v = range (vlen/ss)
#    ones_ind= map(lambda z: z*ss,v)
#
#    skip2_pr0 = skip(gr.sizeof_gr_complex,vlen)
#    skip2_pr1 = skip(gr.sizeof_gr_complex,vlen)
#    for x in ones_ind:
#      skip2_pr0.skip(x)
#      skip2_pr1.skip(x)
#
#    #print "skipped ones",ones_ind
#
#    v2s_pr0 = gr.vector_to_stream(gr.sizeof_gr_complex,vlen)
#    v2s_pr1 = gr.vector_to_stream(gr.sizeof_gr_complex,vlen)
#
#    s2v1_pr0 = gr.stream_to_vector(gr.sizeof_gr_complex,vlen/ss)
#    trigger_src_1_pr0 = gr.vector_source_b(trigger,True)
#    s2v1_pr1 = gr.stream_to_vector(gr.sizeof_gr_complex,vlen/ss)
#    trigger_src_1_pr1 = gr.vector_source_b(trigger,True)
#
#
#    s2v2_pr0 = gr.stream_to_vector(gr.sizeof_gr_complex,vlen/ss*(ss-1))
#    trigger_src_2_pr0 = gr.vector_source_b(trigger,True)
#    s2v2_pr1 = gr.stream_to_vector(gr.sizeof_gr_complex,vlen/ss*(ss-1))
#    trigger_src_2_pr1 = gr.vector_source_b(trigger,True)
#
#    mag_sq_ones_pr0 = gr.complex_to_mag_squared(vlen/ss)
#    mag_sq_ones_pr1 = gr.complex_to_mag_squared(vlen/ss)
#
#    mag_sq_zeros_pr0 = gr.complex_to_mag_squared(vlen/ss*(ss-1))
#    mag_sq_zeros_pr1 = gr.complex_to_mag_squared(vlen/ss*(ss-1))
#
#    filt_ones_pr0 = gr.single_pole_iir_filter_ff(0.001,vlen/ss)
#    filt_ones_pr1 = gr.single_pole_iir_filter_ff(0.001,vlen/ss)
#
#    filt_zeros_pr0 = gr.single_pole_iir_filter_ff(0.001,vlen/ss*(ss-1))
#    filt_zeros_pr1 = gr.single_pole_iir_filter_ff(0.001,vlen/ss*(ss-1))
#
#    ##nomin_p = gr.add_vff(vlen/ss)
#    ##denomin_p = gr.add_vff(vlen/ss)
#
#   ## nomin_z = gr.add_vff(vlen/ss*(ss-1))
#   ## denomin_z = gr.add_vff(vlen/ss*(ss-1))
#
#    v1 = vlen/ss*(ss-1)
#    v2 = vlen/ss
#
#    vevc1 =[-1]*v1
#    vevc2 =[-1]*v2
#    vevc3 =[-ss]*v2
#    vevc4 =[1]*v2
#   ## v2 = [-ss]*vlen
#
#    neg_nomin_p = gr.multiply_const_vff(vevc2)
#    neg_denomin_p = gr.multiply_const_vff(vevc3)
#
#    neg_nomin_z = gr.multiply_const_vff(vevc1)
#
#    div_p=gr.divide_ff(vlen/ss)
#    div_pp=gr.divide_ff(vlen/ss)
#    div_z=gr.divide_ff(vlen/ss*(ss-1))
#
#    on_zeros = gr.add_const_vff(vevc1)
#    on_ones_upper = gr.add_const_vff(vevc2)
#    on_ones_lower = gr.add_const_vff(vevc4)
#    sum_ones = add_vff(vlen/ss)
#    sum_ones_d= add_vff(vlen/ss)
#    sum_zeros = add_vff(vlen/ss*(ss-1))
#
#    #D = gr.divide_ff()
#    #P = gr.multiply_ff()
#    #mult1 = gr.multiply_const_ff(ss-1.0)
#    #add1 = gr.add_const_ff(-1.0)
#    #mult2 = gr.multiply_const_ff(1./ss)
#    scsnr_z_db = gr.nlog10_ff(10,vlen/ss*(ss-1),0)
#    scsnr_p_db = gr.nlog10_ff(10,vlen/ss,0)
#    filt_end_z = gr.single_pole_iir_filter_ff(0.1,vlen/ss*(ss-1))
#    filt_end_p = gr.single_pole_iir_filter_ff(0.1,vlen/ss)
#    nusin_1 = gr.null_sink(gr.sizeof_float*vlen/ss)
#    nusin_2 = gr.null_sink(gr.sizeof_float*vlen/ss)
#
#
#    self.connect((self,0),v2s_pr0,skip1_pr0,s2v1_pr0,mag_sq_ones_pr0,filt_ones_pr0)
#    self.connect(trigger_src_1_pr0,(skip1_pr0,1))
#
#    self.connect(v2s_pr0,skip2_pr0,s2v2_pr0,mag_sq_zeros_pr0,filt_zeros_pr0)
#    self.connect(trigger_src_2_pr0,(skip2_pr0,1))
#
#    self.connect((self,1),v2s_pr1,skip1_pr1,s2v1_pr1,mag_sq_ones_pr1,filt_ones_pr1)
#    self.connect(trigger_src_1_pr1,(skip1_pr1,1))
#
#    self.connect(v2s_pr1,skip2_pr1,s2v2_pr1,mag_sq_zeros_pr1,filt_zeros_pr1)
#    self.connect(trigger_src_2_pr1,(skip2_pr1,1))
#
#    #self.connect(filt_ones_pr0,neg_nomin_p)
#
#    # On zeros
#    self.connect(filt_zeros_pr1,(sum_zeros,0))
#    self.connect(filt_zeros_pr0,neg_nomin_z,(sum_zeros,1))
#    self.connect(sum_zeros,div_z)
#    self.connect(filt_zeros_pr0,(div_z,1))
#
#    # On ones
#    self.connect(filt_ones_pr1,(sum_ones,0))
#    self.connect(filt_ones_pr0,neg_nomin_p,(sum_ones,1))
#    self.connect(sum_ones,div_p)
#
#    self.connect(filt_ones_pr1,neg_denomin_p,sum_ones_d)
#    self.connect(filt_ones_pr0,(sum_ones_d,1))
#
#    self.connect(sum_ones_d,(div_p,1))
#
#
#
#
#
#
#   #####
#
##    self.connect(filt_zeros_pr1,div_z)
##    self.connect(filt_zeros_pr0,(div_z,1))
##
##    self.connect(filt_ones_pr1,div_p)
##    self.connect(filt_ones_pr0,(div_p,1))
##
##    self.connect(div_p,on_ones_upper)
##    self.connect(div_p,neg_denomin_p,on_ones_lower)
##    self.connect(on_ones_upper,div_pp)
##    self.connect(on_ones_lower,(div_pp,1))
##
##
##
#
#    #self.connect(div_z,filt_end_z,scsnr_z_db,self)
#    #self.connect(div_p,filt_end_p,scsnr_p_db,(self,1))
#
######
#    v2s_p = gr.vector_to_stream(gr.sizeof_float,vlen/ss)
#    v2s_z = gr.vector_to_stream(gr.sizeof_float,vlen/ss*(ss-1))
#    s2v = gr.stream_to_vector(gr.sizeof_float,vlen)
#    scsnr_db = gr.nlog10_ff(10,vlen,0)
#    filt_end = gr.single_pole_iir_filter_ff(0.1,vlen)
#    #s2v_z = gr.stream_to_vector(gr.sizeof_float,vlen/ss*(ss-1))
#
#
#    # imux creation
#    imux = [1]
#    imux.extend([0]*(ss-1))
#
##    for i in range (vlen/ss):
##        imux.append(i+1)
##        for s in range (skip-1):
##                imux.append(0)
#    self.connect(div_z,v2s_z)
#    self.connect(div_p,v2s_p)
#
#
#
#    muxvec = static_mux_v(gr.sizeof_float, imux)
#    self.connect(v2s_z,(muxvec,0))
#    self.connect(v2s_p,(muxvec,1))
#
#    self.connect(muxvec,s2v,filt_end,scsnr_db,self)
#
#
#
#
#    #self.connect(div_z,on_zeros,scsnr_z_db,self)
#
#    #self.connect(sum_ones,D)
#    #self.connect(sum_zeros,(D,1))
#    #self.connect(D,mult1,add1,mult2)
#
#    #self.connect(mult2,scsnrdb,filt_end,self)



################################################################################
################################################################################

class milans_sinr_sc_estimator(gr.hier_block2):
  """
  Based on Milans idea (to be published)

  rho_hat = ((skip-1)*sum(|Y1_k|^2)/sum(|Y0_k|^2) -1)*(1/skip)
  where
   input_0 is the received Morelli preamble signal in frequency domain (on nulled subcarriers)
   input_1 is the received second preamble (used for ch. estimation) signal in frequency domain (on non-used subcarriers)
   
   output_0 is the SINR per subcarrier
   output_1 is the average SINR (is uniform Gussian noise over all subcarriers is assumed)
   skip is the number of periodic parts in the Morelli preamble symbol (eg 2, 4, 8)
  """
  def __init__(self, subc, vlen, ss):
    gr.hier_block2.__init__(self, "new_snr_estimator",
        gr.io_signature(2,2,gr.sizeof_gr_complex*vlen),
        #gr.io_signature2(2,2,gr.sizeof_float*vlen,gr.sizeof_float*vlen/ss*(ss-1)))
        gr.io_signature2(2,2,gr.sizeof_float*vlen,gr.sizeof_float))

    print "Created Milan's SINR estimator"

    trigger = [0]*vlen
    trigger[0] = 1

    v = range (vlen/ss)
    ones_ind= map(lambda z: z*ss,v)

    skip2_pr0 = skip(gr.sizeof_gr_complex,vlen)
    skip2_pr1 = skip(gr.sizeof_gr_complex,vlen)
    for x in ones_ind:
      skip2_pr0.skip(x)
      skip2_pr1.skip(x)

    #print "skipped ones",ones_ind

    v2s_pr0 = gr.vector_to_stream(gr.sizeof_gr_complex,vlen)
    v2s_pr1 = gr.vector_to_stream(gr.sizeof_gr_complex,vlen)

    s2v2_pr0 = gr.stream_to_vector(gr.sizeof_gr_complex,vlen/ss*(ss-1))
    trigger_src_2_pr0 = gr.vector_source_b(trigger,True)
    s2v2_pr1 = gr.stream_to_vector(gr.sizeof_gr_complex,vlen/ss*(ss-1))
    trigger_src_2_pr1 = gr.vector_source_b(trigger,True)

    mag_sq_zeros_pr0 = gr.complex_to_mag_squared(vlen/ss*(ss-1))
    mag_sq_zeros_pr1 = gr.complex_to_mag_squared(vlen/ss*(ss-1))


    filt_zeros_pr0 = gr.single_pole_iir_filter_ff(0.01,vlen/ss*(ss-1))
    filt_zeros_pr1 = gr.single_pole_iir_filter_ff(0.01,vlen/ss*(ss-1))
    v1 = vlen/ss*(ss-1)
    vevc1 =[-1]*v1
    neg_nomin_z = gr.multiply_const_vff(vevc1)
    div_z=gr.divide_ff(vlen/ss*(ss-1))
    on_zeros = gr.add_const_vff(vevc1)
    sum_zeros = add_vff(vlen/ss*(ss-1))
    
    # For average
    sum_all = vector_sum_vff(vlen)
    mult = gr.multiply_const_ff(1./vlen)
    scsnr_db_av = gr.nlog10_ff(10,1,0)
    filt_end_av = gr.single_pole_iir_filter_ff(0.1)


    self.connect((self,0),v2s_pr0,skip2_pr0,s2v2_pr0,mag_sq_zeros_pr0,filt_zeros_pr0)
    self.connect(trigger_src_2_pr0,(skip2_pr0,1))



    self.connect((self,1),v2s_pr1,skip2_pr1,s2v2_pr1,mag_sq_zeros_pr1,filt_zeros_pr1)
    self.connect(trigger_src_2_pr1,(skip2_pr1,1))


    # On zeros
    self.connect(filt_zeros_pr1,(sum_zeros,0))
    self.connect(filt_zeros_pr0,neg_nomin_z,(sum_zeros,1))
    self.connect(sum_zeros,div_z)
    self.connect(filt_zeros_pr0,(div_z,1))


    scsnr_db = gr.nlog10_ff(10,vlen,0)
    filt_end = gr.single_pole_iir_filter_ff(0.1,vlen)



    dd = []
    for i in range (vlen/ss):
        dd.extend([i*ss])
    #print dd
    interpolator = sinr_interpolator(vlen, ss,dd)

    self.connect(div_z,interpolator,filt_end,scsnr_db,self)
    self.connect(interpolator,sum_all,mult,scsnr_db_av,filt_end_av,(self,1))

################################################################################
################################################################################

class milans_sinr_sc_estimator2(gr.hier_block2):
  """
  Based on Milans idea (to be published)

  rho_hat = ((skip-1)*sum(|Y1_k|^2)/sum(|Y0_k|^2) -1)*(1/skip)
  where
   input_0 is the received Morelli preamble signal in frequency domain (on nulled subcarriers)
   input_1 is the received second preamble (used for ch. estimation) signal in frequency domain (on non-used subcarriers)
   
   output_0 is the SINR per subcarrier
   output_1 is the average SINR (is uniform Gussian noise over all subcarriers is assumed)
   skip is the number of periodic parts in the Morelli preamble symbol (eg 2, 4, 8)
  """
  def __init__(self, subc, vlen, ss):
    gr.hier_block2.__init__(self, "new_snr_estimator",
        gr.io_signature(2,2,gr.sizeof_gr_complex*vlen),
        #gr.io_signature2(2,2,gr.sizeof_float*vlen,gr.sizeof_float*vlen/ss*(ss-1)))
        gr.io_signature2(2,2,gr.sizeof_float*vlen,gr.sizeof_float))

    print "Created Milan's SINR estimator 2"

    config = station_configuration()

#    trigger = [0]*vlen
#    trigger[0] = 1
#
#    v = range (vlen/ss)
#    ones_ind= map(lambda z: z*ss,v)
#
#    skip2_pr0 = skip(gr.sizeof_gr_complex,vlen)
#    skip2_pr1 = skip(gr.sizeof_gr_complex,vlen)
#    for x in ones_ind:
#      skip2_pr0.skip(x)
#      skip2_pr1.skip(x)
#
#    #print "skipped ones",ones_ind
#
#    v2s_pr0 = gr.vector_to_stream(gr.sizeof_gr_complex,vlen)
#    v2s_pr1 = gr.vector_to_stream(gr.sizeof_gr_complex,vlen)
#
#    s2v2_pr0 = gr.stream_to_vector(gr.sizeof_gr_complex,vlen/ss*(ss-1))
#    trigger_src_2_pr0 = gr.vector_source_b(trigger,True)
#    s2v2_pr1 = gr.stream_to_vector(gr.sizeof_gr_complex,vlen/ss*(ss-1))
#    trigger_src_2_pr1 = gr.vector_source_b(trigger,True)
#
#    mag_sq_zeros_pr0 = gr.complex_to_mag_squared(vlen/ss*(ss-1))
#    mag_sq_zeros_pr1 = gr.complex_to_mag_squared(vlen/ss*(ss-1))
#
#
#    filt_zeros_pr0 = gr.single_pole_iir_filter_ff(0.01,vlen/ss*(ss-1))
#    filt_zeros_pr1 = gr.single_pole_iir_filter_ff(0.01,vlen/ss*(ss-1))
#    v1 = vlen/ss*(ss-1)
#    vevc1 =[-1]*v1
#    neg_nomin_z = gr.multiply_const_vff(vevc1)
#    div_z=gr.divide_ff(vlen/ss*(ss-1))
#    on_zeros = gr.add_const_vff(vevc1)
#    sum_zeros = add_vff(vlen/ss*(ss-1))
#    
    # For average
    sum_all = vector_sum_vff(vlen)
    mult = blocks.multiply_const_ff(1./vlen)
    scsnr_db_av = blocks.nlog10_ff(10,1,0)
    filt_end_av = filter.single_pole_iir_filter_ff(0.1)
#
#
#    self.connect((self,0),v2s_pr0,skip2_pr0,s2v2_pr0,mag_sq_zeros_pr0,filt_zeros_pr0)
#    self.connect(trigger_src_2_pr0,(skip2_pr0,1))
#
#
#
#    self.connect((self,1),v2s_pr1,skip2_pr1,s2v2_pr1,mag_sq_zeros_pr1,filt_zeros_pr1)
#    self.connect(trigger_src_2_pr1,(skip2_pr1,1))
#
#
#    # On zeros
#    self.connect(filt_zeros_pr1,(sum_zeros,0))
#    self.connect(filt_zeros_pr0,neg_nomin_z,(sum_zeros,1))
#    self.connect(sum_zeros,div_z)
#    self.connect(filt_zeros_pr0,(div_z,1))
    

    estimator = sinr_estimator(vlen, ss, config.dc_null)

    scsnr_db = blocks.nlog10_ff(10,vlen,0)
    filt_end = filter.single_pole_iir_filter_ff(0.1,vlen)



    dd = []
    #for i in range (vlen/ss):
    #    dd.extend([i*ss])
    for i in range (vlen/ss):
        if i < (vlen/ss)/2:
            dd.extend([i*ss + 4 + config.dc_null/2])
        else:
            dd.extend([i*ss + 4 - config.dc_null/2])

    #print dd
    interpolator = sinr_interpolator(vlen, ss,dd)
    
    self.connect((self,0),(estimator,0))
    self.connect((self,1),(estimator,1))
    self.connect(estimator,interpolator,filt_end,scsnr_db,self)
    self.connect(interpolator,sum_all,mult,scsnr_db_av,filt_end_av,(self,1))
    #log_to_file(self,estimator , "data/estimator.float")
    #log_to_file(self,interpolator, "data/interpolator.float")


################################################################################
################################################################################
class milans_sinr_sc_estimator3(gr.hier_block2):
  """
  Based on Milans idea (to be published)

  rho_hat = ((skip-1)*sum(|Y1_k|^2)/sum(|Y0_k|^2) -1)*(1/skip)
  where
   input_0 is the received Morelli preamble signal in frequency domain (on nulled subcarriers)
   input_1 is the received second preamble (used for ch. estimation) signal in frequency domain (on non-used subcarriers)
   
   output_0 is the SINR per subcarrier
   output_1 is the average SINR (is uniform Gussian noise over all subcarriers is assumed)
   skip is the number of periodic parts in the Morelli preamble symbol (eg 2, 4, 8)
  """
  def __init__(self, subc, vlen, ss):
    gr.hier_block2.__init__(self, "new_snr_estimator",
        gr.io_signature(2,2,gr.sizeof_gr_complex*vlen),
        #gr.io_signature2(2,2,gr.sizeof_float*vlen,gr.sizeof_float*vlen/ss*(ss-1)))
        gr.io_signature2(2,2,gr.sizeof_float*vlen,gr.sizeof_float))

    print "Created Milan's SINR estimator 3"

#    trigger = [0]*vlen
#    trigger[0] = 1
#
#    v = range (vlen/ss)
#    ones_ind= map(lambda z: z*ss,v)
#
#    skip2_pr0 = skip(gr.sizeof_gr_complex,vlen)
#    skip2_pr1 = skip(gr.sizeof_gr_complex,vlen)
#    for x in ones_ind:
#      skip2_pr0.skip(x)
#      skip2_pr1.skip(x)
#
#    #print "skipped ones",ones_ind
#
#    v2s_pr0 = gr.vector_to_stream(gr.sizeof_gr_complex,vlen)
#    v2s_pr1 = gr.vector_to_stream(gr.sizeof_gr_complex,vlen)
#
#    s2v2_pr0 = gr.stream_to_vector(gr.sizeof_gr_complex,vlen/ss*(ss-1))
#    trigger_src_2_pr0 = gr.vector_source_b(trigger,True)
#    s2v2_pr1 = gr.stream_to_vector(gr.sizeof_gr_complex,vlen/ss*(ss-1))
#    trigger_src_2_pr1 = gr.vector_source_b(trigger,True)
#
#    mag_sq_zeros_pr0 = gr.complex_to_mag_squared(vlen/ss*(ss-1))
#    mag_sq_zeros_pr1 = gr.complex_to_mag_squared(vlen/ss*(ss-1))
#
#
#    filt_zeros_pr0 = gr.single_pole_iir_filter_ff(0.01,vlen/ss*(ss-1))
#    filt_zeros_pr1 = gr.single_pole_iir_filter_ff(0.01,vlen/ss*(ss-1))
#    v1 = vlen/ss*(ss-1)
#    vevc1 =[-1]*v1
#    neg_nomin_z = gr.multiply_const_vff(vevc1)
#    div_z=gr.divide_ff(vlen/ss*(ss-1))
#    on_zeros = gr.add_const_vff(vevc1)
#    sum_zeros = add_vff(vlen/ss*(ss-1))
#    
    # For average
    #sum_all = vector_sum_vff(vlen)
    #mult = gr.multiply_const_ff(1./vlen)
    scsnr_db_av = gr.nlog10_ff(10,1,0)
    filt_end_av = gr.single_pole_iir_filter_ff(0.1)
#
#
#    self.connect((self,0),v2s_pr0,skip2_pr0,s2v2_pr0,mag_sq_zeros_pr0,filt_zeros_pr0)
#    self.connect(trigger_src_2_pr0,(skip2_pr0,1))
#
#
#
#    self.connect((self,1),v2s_pr1,skip2_pr1,s2v2_pr1,mag_sq_zeros_pr1,filt_zeros_pr1)
#    self.connect(trigger_src_2_pr1,(skip2_pr1,1))
#
#
#    # On zeros
#    self.connect(filt_zeros_pr1,(sum_zeros,0))
#    self.connect(filt_zeros_pr0,neg_nomin_z,(sum_zeros,1))
#    self.connect(sum_zeros,div_z)
#    self.connect(filt_zeros_pr0,(div_z,1))

    estimator = sinr_estimator2(vlen, ss)

    scsnr_db = gr.nlog10_ff(10,vlen,0)
    filt_end = gr.single_pole_iir_filter_ff(0.1,vlen)



    dd = []
    for i in range (vlen/ss):
        dd.extend([i*ss])
    #print dd
    #interpolator = sinr_interpolator(vlen, ss,dd)
    
    self.connect((self,0),(estimator,0))
    self.connect((self,1),(estimator,1))
    self.connect(estimator,filt_end,scsnr_db,self)
    self.connect((estimator,1),scsnr_db_av,filt_end_av,(self,1))



class effective_snr_estimator(gr.hier_block2):
  """
  Based on the paper "Effective SNR Estimation in OFDM System Simulation"
  from Shousheng He and Mats Torkelson

  rho_hat = |< S_k Z_k* >|^2 / ( < |Z_k|^2 > < |S_k|^2 > - |< S_k Z_k* >|^2 )
  where
   S_k is the reference signal in frequency domain and
   Z_k is the received signal in frequency domain
   (.)* denotes the complex conjugation
   <.> is the empirical mean, 1/N sum i = 0 .. N-1 (.)

  Abbreviations:
   R_innerproduct = S_k Z_k*
   R_sum = < R_innerproduct >
   R = | R_sum | ^2
   received_magsqrd = |Z_k|^2
   reference_magsqrd = |Z_k|^2
   received_sum = < received_magsqrd >
   reference_sum = < reference_magsqrd >
   P = received_sum * reference_sum
   denominator = P - R
  """
  def __init__(self,vlen):
    gr.hier_block2.__init__(self,"snr_estimator",
      gr.io_signature(2,2,gr.sizeof_gr_complex*vlen),
      gr.io_signature(1,1,gr.sizeof_float))

    reference = gr.kludge_copy(gr.sizeof_gr_complex*vlen)
    received = gr.kludge_copy(gr.sizeof_gr_complex*vlen)
    self.connect((self,0),reference)
    self.connect((self,1),received)

    received_conjugated = gr.conjugate_cc(vlen)
    self.connect(received,received_conjugated)

    R_innerproduct = gr.multiply_vcc(vlen)
    self.connect(reference,R_innerproduct)
    self.connect(received_conjugated,(R_innerproduct,1))

    R_sum = vector_sum_vcc(vlen)
    self.connect(R_innerproduct,R_sum)

    R = gr.complex_to_mag_squared()
    self.connect(R_sum,R)

    received_magsqrd = gr.complex_to_mag_squared(vlen)
    reference_magsqrd = gr.complex_to_mag_squared(vlen)
    self.connect(received,received_magsqrd)
    self.connect(reference,reference_magsqrd)

    received_sum = vector_sum_vff(vlen)
    reference_sum = vector_sum_vff(vlen)
    self.connect(received_magsqrd,received_sum)
    self.connect(reference_magsqrd,reference_sum)

    P = gr.multiply_ff()
    self.connect(received_sum,(P,0))
    self.connect(reference_sum,(P,1))

    denominator = gr.sub_ff()
    self.connect(P,denominator)
    self.connect(R,(denominator,1))

    rho_hat = gr.divide_ff()
    self.connect(R,rho_hat)
    self.connect(denominator,(rho_hat,1))
    self.connect(rho_hat,self)

