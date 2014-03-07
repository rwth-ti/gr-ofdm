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
from random import randint

class qa_modulation(gr_unittest.TestCase):
  def setUp (self):
    self.tb = gr.top_block()
    
  def tearDown(self):
    self.tb = None
  
  def stdtest_01(self,bps):
    # no reuse, bps bits per symbol
    vsyms = 10
    vlen = 10
    bits = vsyms*vlen*bps
    
    refdata = [randint(0,1) for i in range(bits)]
    cmap = [bps]*(vsyms*vlen)
    
    src = gr.vector_source_b(refdata)
    dst = gr.vector_sink_b()
    
    src_map = gr.vector_source_b(cmap)
    s2v = gr.stream_to_vector(gr.sizeof_char, vlen)
    self.tb.connect(src_map,s2v)
    
    dut1 = ofdm.generic_mapper_bcv(vlen)
    dut2 = ofdm.generic_demapper_vcb(vlen)
    
    self.tb.connect(src,dut1,dut2,dst)
    self.tb.connect(s2v,(dut1,1))
    self.tb.connect(s2v,(dut2,1))
    
    self.tb.run()
    
    self.assertEqual(list(dst.data()),refdata)
    
if __name__ == '__main__':
  gr_unittest.main()
