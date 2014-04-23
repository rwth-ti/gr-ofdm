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

from gnuradio import gr, gru

class vector_equalizer(gr.hier_block2):
  def __init__(self, vlen):
    gr.hier_block2.__init__(self, "vector_equalizer",
        gr.io_signature(1,1,gr.sizeof_gr_complex*vlen),
        gr.io_signature(1,1,gr.sizeof_gr_complex*vlen))

    self.input=gr.add_const_vcc([0.0]*vlen)
    self.connect(self, self.input)

    c2mag = gr.complex_to_mag(vlen)
    max_v = gr.max_ff(vlen)
    interpolator = gr.interp_fir_filter_fff(vlen,[1.0]*vlen)
    f2c = gr.float_to_complex()
    v2s = gr.vector_to_stream(gr.sizeof_gr_complex, vlen)
    normalizer = gr.divide_cc()
    s2v = gr.stream_to_vector(gr.sizeof_gr_complex, vlen)

    self.connect(self.input, v2s, (normalizer,0))
    self.connect(self.input, c2mag, max_v, interpolator, f2c, (normalizer,1))
    self.connect(normalizer, s2v)
    self.connect(s2v, self)
