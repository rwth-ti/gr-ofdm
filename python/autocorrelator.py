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
import ofdm as ofdm

class autocorrelator ( gr.hier_block2 ):
  def __init__( self, lag, n_samples ):
    gr.hier_block2.__init__( self,
        "autocorrelator",
        gr.io_signature(
            1, 1,
            gr.sizeof_gr_complex ),
        gr.io_signature(
            1, 1,
            gr.sizeof_float ) )
    s1 = ofdm.autocorrelator_stage1( lag )
    s2 = ofdm.autocorrelator_stage2( n_samples )

    self.connect( self, s1, s2, self )
    self.connect( (s1,1), (s2,1) )

    self.s2 = s2
