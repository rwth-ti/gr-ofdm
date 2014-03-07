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
from ofdm import moms_ff


################################################################################
################################################################################

class moms_block(gr.hier_block2):
  def __init__(self,delay_num,delay_denom):
    gr.hier_block2.__init__(self,"moms_block",
      gr.io_signature(1,1,gr.sizeof_gr_complex),
      gr.io_signature(1,1,gr.sizeof_gr_complex))

    cmplx_to_real  = gr.complex_to_real()
    cmplx_to_img   = gr.complex_to_imag()

    iirf_real = gr.iir_filter_ffd([1.5],[1, -0.5])
    self.moms_real = moms_ff()
    self.moms_real.set_init_ip_fraction(delay_num,delay_denom)

    iirf_imag = gr.iir_filter_ffd([1.5],[1, -0.5])
    self.moms_imag = moms_ff()
    self.moms_imag.set_init_ip_fraction(delay_num,delay_denom)

    float_to_cmplx = gr.float_to_complex()

    self.connect((self,0),            (cmplx_to_real,0))
    self.connect((self,0),            (cmplx_to_img,0))
    self.connect((cmplx_to_real,0),   (iirf_real,0))
    self.connect((cmplx_to_img,0),    (iirf_imag,0))
    self.connect((iirf_real,0),       (self.moms_real,0))
    self.connect((iirf_imag,0),       (self.moms_imag,0))
    self.connect((self.moms_real,0),  (float_to_cmplx,0))
    self.connect((self.moms_imag,0),  (float_to_cmplx,1))
    self.connect((float_to_cmplx,0),  (self,0))

  def set_ip_fraction(self,a,b):
    self.moms_real.set_ip_fraction(a,b)
    self.moms_imag.set_ip_fraction(a,b)
  def set_offset_num(self,a):
    self.moms_real.set_offset_num(a)
    self.moms_imag.set_offset_num(a)
