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

from gnuradio import gr, gr_unittest
from schmidl import coarse_frequency_offset_estimator
from numpy import concatenate,pi,exp,conjugate,arctan2
from random import randint,seed
from gr_tools import ifft

class qa_schmidl_coarse_frequency_offset_estimator (gr_unittest.TestCase):
  def setUp (self):
    self.fg = gr.top_block ("test_block")

  def tearDown (self):
    self.fg = None

  def test_001(self):
    N = 20
    N2 = 32
    blocks = 3

    seed()
    pn = [randint(0,3) for i in range(N/2*3)]

    mod = [1+1j, 1-1j, -1+1j, -1-1j]
    seq = concatenate([[mod[pn[x]],0.0] for x in range(len(pn))])

    signal = [ifft(seq[x*N:(x+1)*N], (N2-N)/2) for x in range(blocks)]
    signal = concatenate([concatenate(signal)]*blocks)

    f = [0.2, 0.1, -0.3]
    fo = [exp(1j*2*pi*f[x/N2]/N2*x) for x in range(N2*blocks)]

    signal = [signal[x]*fo[x] for x in range(len(fo))]

    #sum(0 to L-1, conj(delayed(r)) * r)

    ret = []
    for b in range(blocks):
      acc = 0.0j
      for x in range(N2/2):
        acc = acc + conjugate(signal[x+b*N2])*signal[x+N2/2+b*N2]
      ret.append( float(arctan2(acc.imag,acc.real)/pi) )


    trigger = [0]*N2
    trigger[N2-1] = 1
    trigger = trigger*blocks

    src = gr.vector_source_c(signal)
    src2 = gr.vector_source_b(trigger)
    dst = gr.vector_sink_f()

    uut = coarse_frequency_offset_estimator(N2)

    self.fg.connect(src,uut,dst)
    self.fg.connect(src2,(uut,1))

    self.fg.run()

    self.assertFloatTuplesAlmostEqual2(ret,dst.data(),rel_eps=1e-2)


if __name__ == '__main__':
  gr_unittest.main()

