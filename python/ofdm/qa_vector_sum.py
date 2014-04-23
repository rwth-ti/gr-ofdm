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
import ofdm as ofdm

class qa_vector_sum (gr_unittest.TestCase):
  def setUp (self):
    self.fg = gr.top_block ("test_block")

  def tearDown (self):
    self.fg = None

  def test_vcc_001(self):
    N = 10

    data = [1.0+2.0j]*N

    src = gr.vector_source_c(data)
    s2v = gr.stream_to_vector(gr.sizeof_gr_complex,N)
    dst = gr.vector_sink_c()

    uut = ofdm.vector_sum_vcc(N)

    self.fg.connect(src,s2v,uut,dst)

    self.fg.run()

    self.assertEqual([sum(data)],list(dst.data()))

  def test_vcc_002(self):
    N = 10

    data = [1.0+2.0j]*(N*2)

    src = gr.vector_source_c(data)
    s2v = gr.stream_to_vector(gr.sizeof_gr_complex,N)
    dst = gr.vector_sink_c()

    uut = ofdm.vector_sum_vcc(N)

    self.fg.connect(src,s2v,uut,dst)

    self.fg.run()

    self.assertEqual([sum(data[0:N]),sum(data[N:2*N])],list(dst.data()))

  def test_vff_001(self):
    N = 10

    data = [2.0]*N

    src = gr.vector_source_c(data)
    s2v = gr.stream_to_vector(gr.sizeof_gr_complex,N)
    dst = gr.vector_sink_c()

    uut = ofdm.vector_sum_vcc(N)

    self.fg.connect(src,s2v,uut,dst)

    self.fg.run()

    self.assertEqual([sum(data)],list(dst.data()))

  def test_vff_002(self):
    N = 10

    data = [2.0]*(N*2)

    src = gr.vector_source_c(data)
    s2v = gr.stream_to_vector(gr.sizeof_gr_complex,N)
    dst = gr.vector_sink_c()

    uut = ofdm.vector_sum_vcc(N)

    self.fg.connect(src,s2v,uut,dst)

    self.fg.run()

    self.assertEqual([sum(data[0:N]),sum(data[N:2*N])],list(dst.data()))

if __name__ == '__main__':
  gr_unittest.main()

