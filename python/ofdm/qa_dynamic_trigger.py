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

from numpy import concatenate


class qa_dynamic_trigger (gr_unittest.TestCase):
  def setUp (self):
    self.fg = gr.top_block ("test_block")

  def tearDown (self):
    self.fg = None

  def test_001 (self):
    l = [10,8,12,9,4,9,2,1,4,6,5]
    
    ref = []
    for x in l:
      ref.append(concatenate([[1],[0]*(x-1)]))
    ref = concatenate(ref)
    
    dst = gr.vector_sink_b()
    src = gr.vector_source_i(l)
    uut = ofdm.dynamic_trigger_ib(True)

    self.fg.connect(src, uut, dst)
    self.fg.run()

    d = dst.data()
    self.assertEqual(list(ref),list(d))


  def test_002 (self):
    l = [10,8,12,9,4,9,2,1,4,6,5]
    
    ref = []
    for x in l:
      ref.append(concatenate([[0]*(x-1),[1]]))
    ref = concatenate(ref)
    
    dst = gr.vector_sink_b()
    src = gr.vector_source_i(l)
    uut = ofdm.dynamic_trigger_ib(False)

    self.fg.connect(src, uut, dst)
    self.fg.run()

    d = dst.data()
    self.assertEqual(list(ref),list(d))

if __name__ == '__main__':
  gr_unittest.main()

