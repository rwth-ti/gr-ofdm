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

from math import sqrt, pi
from numpy import concatenate,conjugate,array
from gr_tools import fft,ifft
from gnuradio import gr, blocks
from cmath import exp
from numpy import abs,concatenate
import numpy
import ofdm as ofdm
from station_configuration import *
from ofdm import stream_controlled_mux,skip
from numpy import *

from ofdm import static_mux_c, static_mux_v

class default_block_header (object):
  def __init__(self,data_subcarriers,fft_length, fbmc, est_preamble, options):
    self.fbmc = fbmc
    if self.fbmc:
        self.no_preambles = est_preamble
    else:
        self.no_preambles = est_preamble + 1
    self.no_pilotsyms = self.no_preambles
    self.pilotsym_td = []
    self.pilotsym_fd = []
    self.pilotsym_fd_1 = []
    self.pilotsym_fd_2 = []
    self.pilotsym_td_1 = []
    self.pilotsym_td_2 = []
    self.pilotsym_pos = []
    self.pilot_tones = []
    self.pilot_tone_map = []
    
    self._prepare_pilot_subcarriers(data_subcarriers, fft_length)
    
    #FBMC preambles
    self.fbmc_pilotsym_fd = []
    
    vlen = data_subcarriers # padding AFTER oqam processing
    #vlen = fft_length # padding BEFORE oqam processing
    
    norm_fact = 3
    fbmc_fd_1 = numpy.array([0 + 0j]*vlen)
    fbmc_fd_2_list = [1, -1j, -1, 1j]* (int)(vlen/4)
    fbmc_fd_2_l_list = [1j, -1, -1j, 1]* (int)(vlen/4)
    fbmc_fd_2_r_list = [-1j, 1, 1j, -1]* (int)(vlen/4)
    fbmc_fd_2_list_norm = [1.0/math.sqrt(norm_fact), -1.0j/math.sqrt(norm_fact), -1.0/math.sqrt(norm_fact), 1.0j/math.sqrt(norm_fact)]* (int)(vlen/4)
    fbmc_fd_2_l_list_norm = [1.0j/math.sqrt(norm_fact), -1.0/math.sqrt(norm_fact), -1.0j/math.sqrt(norm_fact), 1.0/math.sqrt(norm_fact)]* (int)(vlen/4)
    fbmc_fd_2_r_list_norm = [-1.0j/math.sqrt(norm_fact), 1.0/math.sqrt(norm_fact), 1.0j/math.sqrt(norm_fact), -1.0/math.sqrt(norm_fact)]* (int)(vlen/4)

    if norm_fact !=1:
        #norm_fact=norm_fact+2
        norm_fact = 2.128
        #norm_fact=2.37 # channel estimation factor
    
    fbmc_fd_2_list = [1, -1, 1, -1]* (int)(vlen/4)
    
    
    # New idea, random quazi-random-preamble
    hh1 = fixed_real_pn1[0:vlen/4]
    fbmc_fd_2_list = [0]*vlen
    fbmc_fd_2_list[0:len(fbmc_fd_2_list)/2:2] = hh1
    fbmc_fd_2_list[len(fbmc_fd_2_list)/2:len(fbmc_fd_2_list):2] = hh1
    fbmc_fd_2 = numpy.array(fbmc_fd_2_list)#*sqrt(2)
    fbmc_fd_3 = 1j*numpy.roll(fbmc_fd_2,1+vlen/2)
    #fbmc_fd_3 = numpy.roll(fbmc_fd_2,1)


    
    
    
    #fbmc_fd_2 = numpy.array(fbmc_fd_2_list)
    fbmc_fd_2_l = numpy.array(fbmc_fd_2_l_list)
    fbmc_fd_2_r = numpy.array(fbmc_fd_2_r_list)
    fbmc_fd_2_norm = numpy.array(fbmc_fd_2_list_norm)
    fbmc_fd_2_l_norm = numpy.array(fbmc_fd_2_l_list_norm)
    fbmc_fd_2_r_norm = numpy.array(fbmc_fd_2_r_list_norm)
    
    self.fbmc_pilotsym_pos = []
    #fbmc_fd_2_norm = fbmc_fd_1
    
    
    self.fbmc_pilotsym_fd.append(fbmc_fd_1)
    self.fbmc_pilotsym_pos.append(0)
    self.fbmc_pilotsym_fd.append(fbmc_fd_1)
    self.fbmc_pilotsym_pos.append(1)
    self.fbmc_pilotsym_fd.append(fbmc_fd_2)
    self.fbmc_pilotsym_pos.append(2)
    self.fbmc_pilotsym_fd.append(fbmc_fd_2)
    self.fbmc_pilotsym_pos.append(3)
    self.fbmc_pilotsym_fd.append(fbmc_fd_2)
    self.fbmc_pilotsym_pos.append(4)
    self.fbmc_pilotsym_fd.append(fbmc_fd_1)
    self.fbmc_pilotsym_pos.append(5)
    self.fbmc_pilotsym_fd.append(fbmc_fd_1)
    self.fbmc_pilotsym_pos.append(6)
    self.fbmc_pilotsym_fd.append(fbmc_fd_1)
    self.fbmc_pilotsym_pos.append(7)
    #self.fbmc_pilotsym_fd.append(fbmc_fd_1)
    #self.fbmc_pilotsym_pos.append(8)
    #self.fbmc_pilotsym_fd.append(fbmc_fd_1)
    #self.fbmc_pilotsym_pos.append(9)
    #self.fbmc_pilotsym_fd.append(fbmc_fd_1)
    #self.fbmc_pilotsym_pos.append(10)
    #self.fbmc_pilotsym_fd.append(fbmc_fd_1)
    #self.fbmc_pilotsym_pos.append(11)
    #self.fbmc_pilotsym_fd.append(fbmc_fd_1)
    #self.fbmc_pilotsym_pos.append(9)
    
    self.fbmc_no_preambles = len(array(self.fbmc_pilotsym_fd).tolist()[0:]) #fixed for now
    self.fbmc_no_pilotsyms = self.fbmc_no_preambles
    
    print "Number of channel estimation preambles", self.fbmc_no_pilotsyms
    
    x = norm_fact*array(self.fbmc_pilotsym_fd)
    #x = 2.128*array(self.fbmc_pilotsym_fd)
    fbmc_pilotsym_fd_list = (x).tolist()[0:]
    self.fbmc_pilotsym_fd_list =  [item for sublist in fbmc_pilotsym_fd_list for item in sublist]
    
    self.fbmc_pilotsym_fd_list = [1./x if x!=0 else x for x in self.fbmc_pilotsym_fd_list]
    
    
    #print "self.fbmc_pilotsym_fd_list", self.fbmc_pilotsym_fd_list
    
    self.fbmc_no_preambles_td = 2*self.no_pilotsyms #fixed for now # 4 for includin channel estimation
    self.fbmc_no_pilotsyms_td = self.fbmc_no_preambles_td
    self.fbmc_pilotsym_td = []
    self.fbmc_pilotsym_pos_td = []
    
    self.fbmc_pilotsym_fd_timing = []
    self.fbmc_pilotsym_pos_fd_timing = []
    
    #self.fbmc_pilotsym_fd.append(fbmc_fd_1)
    #self.fbmc_pilotsym_pos.append(0)
    #self.fbmc_pilotsym_fd.append(fbmc_fd_2)
    #self.fbmc_pilotsym_pos.append(1)
    #self.fbmc_pilotsym_fd.append(fbmc_fd_1)
    #self.fbmc_pilotsym_pos.append(2)
    
    
    
    

    # symbol position inside ofdm block!
    self.mm_preamble_pos = self.sc_preamble_pos = 0 # restricted to 0!
    self.channel_estimation_pilot = [1] # TODO: remove when interpolating channel estimator available
    

    # Morelli & Mengali + Schmidl & Cox Preamble
    self.mm_periodic_parts = L = 8
    td,fd = morellimengali_designer.create(self.subcarriers, fft_length, L)
    #td = numpy.array([0 + 0j]*fft_length)
    
    

    assert(len(td) == fft_length)
    assert(len(fd) == self.subcarriers)

    self.pilotsym_td.append(td)
    self.pilotsym_fd.append(fd)
    
    self.pilotsym_td_1.append(td)
    self.pilotsym_td_2.append(td)
    
    self.pilotsym_fd_1.append(fd)
    self.pilotsym_fd_2.append(fd)
    self.pilotsym_pos.append(0)
    
    self.fbmc_pilotsym_td.append(td[0:len(td)/2])
    self.fbmc_pilotsym_pos_td.append(0)
    self.fbmc_pilotsym_td.append(td[len(td)/2:len(td)])
    self.fbmc_pilotsym_pos_td.append(1)
    
    self.fbmc_pilotsym_fd_timing.append(fd)
    self.fbmc_pilotsym_pos_fd_timing.append(0)
    
    self.fbmc_no_timing_preambles = len(array(self.fbmc_pilotsym_fd_timing).tolist()[0:]) #fixed for now
    self.fbmc_no_timing_pilotsyms = self.fbmc_no_timing_preambles
    
    


    # Known pilot block to ease estimation of CTF
    td,fd,td_1,fd_1,td_2,fd_2 = schmidl_ifo_designer.create(self.subcarriers, fft_length)
    #td = numpy.array([0 + 0j]*fft_length)
                     
                     
    assert(len(td) == fft_length)
    assert(len(fd) == self.subcarriers)
    assert(len(td_1) == fft_length)
    assert(len(fd_1) == self.subcarriers)
    assert(len(td_2) == fft_length)
    assert(len(fd_2) == self.subcarriers)
    
    if self.fbmc is not True:
        self.fbmc_pilotsym_td.append(td[0:len(td)/2])
        self.fbmc_pilotsym_pos_td.append(2)
        self.fbmc_pilotsym_td.append(td[len(td)/2:len(td)])
        self.fbmc_pilotsym_pos_td.append(3)

    

    self.pilotsym_td.append(td)
    self.pilotsym_fd.append(fd)
    
    if self.no_pilotsyms == 3:
        x_f=[0]*self.subcarriers
        x=[0]*fft_length
        self.pilotsym_fd_1.append(fd)
        self.pilotsym_fd_2.append(x_f)
        self.pilotsym_td_1.append(td)
        self.pilotsym_td_2.append(x)
        self.pilotsym_pos.append(1)
        
        self.pilotsym_fd_1.append(x_f)
        self.pilotsym_fd_2.append(fd)
        self.pilotsym_td_1.append(x)
        self.pilotsym_td_2.append(td)
        self.pilotsym_pos.append(2)
    else:
        self.pilotsym_fd_1.append(fd_1)
        self.pilotsym_fd_2.append(fd_2)
        self.pilotsym_td_1.append(td_1)
        self.pilotsym_td_2.append(td_2)
        self.pilotsym_pos.append(1)


    #assert(self.no_pilotsyms == len(self.pilotsym_fd))
    #assert(self.no_pilotsyms == len(self.pilotsym_fd_1))
    #assert(self.no_pilotsyms == len(self.pilotsym_fd_2))
    #assert(self.no_pilotsyms == len(self.pilotsym_td))
    #assert(self.no_pilotsyms == len(self.pilotsym_pos))


  def _prepare_pilot_subcarriers(self,data_subcarriers,fft_length):
    # FIXME make this parameterisable
    # FIXME pilot subcarriers fixed to 1.0
    
    if self.fbmc:
        self.pilot_subcarriers = 0
    else:
        self.pilot_subcarriers = 8
    self.subcarriers = subc = self.pilot_subcarriers+data_subcarriers
    self.pilot_subc_sym = [2.0]*(self.pilot_subcarriers)

    # compute pilot subcarriers
    pilot_dist = subc/2/(self.pilot_subcarriers/2+1)
    for i in range(1,self.pilot_subcarriers/2+1):
      pos = pilot_dist*i
      self.pilot_tones.append(pos)
      self.pilot_tones.append(-pos)
    self.pilot_tones.sort()
    
    subc_dc = subc/2
    
    tmp = [0.0]*subc
    tmp[subc_dc] = 1.0
    assert(numpy.array(ifft(tmp)).all() == 1.0)

    print "pilot tones",self.pilot_tones
    self.shifted_pilot_tones = shifted_pilot_tones = \
        map(lambda x: x+subc_dc, self.pilot_tones)
    print "shifted pilot tones",self.shifted_pilot_tones

    self.pilot_tone_map = [0.0]*subc
    for i in range(len(self.pilot_tones)):
      self.pilot_tone_map[shifted_pilot_tones[i]] = self.pilot_subc_sym[i]
    
    t = numpy.array( ifft( self.pilot_tone_map ) )
    assert( ( numpy.abs( t.imag ) < 1e-6 ).all() )
    

    # compute partition map
    last_pilot = 0
    partition = []
    for x in range(len(shifted_pilot_tones)):
      dist = shifted_pilot_tones[x]-last_pilot
      partition.append(dist) # data subcarrier
      partition.append(1)    # pilot subcarrier
      last_pilot = shifted_pilot_tones[x]+1
    partition.append(subc - last_pilot)
    print "Data/Pilot subcarrier partition: ", partition
    self.partition = partition
    print "sum partition",sum(partition)


  def add_options(normal, expert):
    expert.add_option("", "--est-preamble", type="int", default=1,
                      help="the number of channel estimation preambles (1 or 2)")

  # Make a static method to call before instantiation
  add_options = staticmethod(add_options)

################################################################################

# time domain
class ofdm_pilot_block_inserter(gr.hier_block2):
  """
  Multiplex pilot blocks to time domain signal.
  """
  def __init__ (self, frame_length, fft_length, cp_length, training_data, ant, add_cyclic_prefix = False):
    
    vlen = fft_length# + cp_length

    gr.hier_block2.__init__(self, "ofdm_pilot_block_inserter_grc",
        gr.io_signature(1,1,gr.sizeof_gr_complex*vlen),
        gr.io_signature(1,1,gr.sizeof_gr_complex*vlen))

    mux = ofdm.frame_mux( vlen, frame_length)
    
    if ant==1:
        for x in range( training_data.no_pilotsyms ):
          mux.add_preamble( training_data.pilotsym_td_1[ x ] )
    elif ant==2:
        for x in range( training_data.no_pilotsyms ):
          mux.add_preamble( training_data.pilotsym_td_2[ x ] )
    else:
       
        for x in range( training_data.no_pilotsyms ):
          ####print "fd", config.training_data.pilotsym_fd[ x ]
          ####print "td", config.training_data.pilotsym_td[ x ]
          print "TTTTtraining_data.no_pilotsyms: ", training_data.no_pilotsyms 
          mux.add_preamble( training_data.pilotsym_td[ x ] ) 

    self.connect( self, mux, self )
    return

################################################################################

################################################################################

# time domain
class pilot_block_inserter2(gr.hier_block2):
  """
  Multiplex pilot blocks to time domain signal.
  """
  def __init__ (self, ant, add_cyclic_prefix = False):

    config = station_configuration()
    fft_length = config.fft_length
    block_length = config.block_length
    cp_length = config.cp_length
    fbmc = config.fbmc
    
    if add_cyclic_prefix:
      vlen = block_length
    else:
      vlen = fft_length

    gr.hier_block2.__init__(self, "pilot_block_inserter2",
        gr.io_signature(1,1,gr.sizeof_gr_complex*vlen/2),
        gr.io_signature(1,1,gr.sizeof_gr_complex*vlen/2))


    mux = ofdm.frame_mux( vlen/2, 2*config.frame_length + config.training_data.fbmc_no_preambles)
    
    if ant==1:
        for x in range( config.training_data.no_pilotsyms ):
          mux.add_preamble( config.training_data.pilotsym_td_1[ x ] )
    elif ant==2:
        for x in range( config.training_data.no_pilotsyms ):
          mux.add_preamble( config.training_data.pilotsym_td_2[ x ] )
    else:
       
        for x in range( config.training_data.fbmc_no_pilotsyms_td ):
          ####print "fd", config.training_data.pilotsym_fd[ x ]
          ####print "td", config.training_data.pilotsym_td[ x ]
          mux.add_preamble( config.training_data.fbmc_pilotsym_td[ x ] ) 

    self.connect( self, mux, self )
    return

################################################################################

# FBMC frequency domain
class fbmc_pilot_block_inserter(gr.hier_block2):
  """
  Multiplex pilot blocks to time domain signal.
  """
  def __init__ (self, subcarriers, frame_data_part, training_data, ant, add_cyclic_prefix = False):

    #config = station_configuration()
    #fft_length = config.fft_length
    #block_length = config.block_length
    #cp_length = config.cp_length
    #fbmc = config.fbmc
      
    vlen = subcarriers #config.subcarriers # padding AFTER oqam processing
    #vlen = fft_length # padding BEFORE oqam processing

    gr.hier_block2.__init__(self, "fbmc_pilot_block_inserter",
        gr.io_signature(1,1,gr.sizeof_gr_complex*vlen),
        gr.io_signature(1,1,gr.sizeof_gr_complex*vlen))


    mux = ofdm.frame_mux( vlen, 2*frame_data_part+training_data.fbmc_no_preambles)
    
    if ant==1:
        for x in range( training_data.no_pilotsyms ):
          mux.add_preamble( training_data.pilotsym_td_1[ x ] )
    elif ant==2:
        for x in range( training_data.no_pilotsyms ):
          mux.add_preamble( training_data.pilotsym_td_2[ x ] )
    else:
       
        for x in range( training_data.fbmc_no_pilotsyms ):
          ####print "fd", config.training_data.pilotsym_fd[ x ]
          print "fbmc_fd", training_data.fbmc_pilotsym_fd[ x ]
          mux.add_preamble( training_data.fbmc_pilotsym_fd[ x ] ) 

    self.connect( self, mux, self )
    return

class fbmc_timing_pilot_block_inserter(gr.hier_block2):
  """
  Multiplex pilot blocks to time domain signal.
  """
  def __init__ (self, ant, add_cyclic_prefix = False):

    config = station_configuration()
    fft_length = config.fft_length
    block_length = config.block_length
    cp_length = config.cp_length
    fbmc = config.fbmc
    
    if add_cyclic_prefix:
      vlen = block_length
    else:
      vlen = fft_length
      
    vlen = config.subcarriers # padding AFTER oqam processing
    #vlen = fft_length # padding BEFORE oqam processing

    gr.hier_block2.__init__(self, "fbmc_timing_pilot_block_inserter",
        gr.io_signature(1,1,gr.sizeof_gr_complex*vlen),
        gr.io_signature(1,1,gr.sizeof_gr_complex*vlen))


    mux = ofdm.frame_mux( vlen,2*config.frame_data_part+config.training_data.fbmc_no_preambles+1)
    
    if ant==1:
        for x in range( config.training_data.no_pilotsyms ):
          mux.add_preamble( config.training_data.pilotsym_td_1[ x ] )
    elif ant==2:
        for x in range( config.training_data.no_pilotsyms ):
          mux.add_preamble( config.training_data.pilotsym_td_2[ x ] )
    else:
       
        for x in range( config.training_data.fbmc_no_timing_pilotsyms ):
          ####print "fd", config.training_data.pilotsym_fd[ x ]
          print "fbmc_fd", config.training_data.fbmc_pilotsym_fd_timing[ x ]
          mux.add_preamble( config.training_data.fbmc_pilotsym_fd_timing[ x ] ) 

    self.connect( self, mux, self )
    return

class pilot_block_filter(gr.hier_block2):
  """
  Remove pilot blocks from ofdm block stream. Frequency domain operation.

  Input 0: ofdm frames
  Input 1: frame trigger
  Output 0: data blocks
  Output 1: frame trigger for data blocks
  """
  def __init__ (self,subcarriers,frame_length,training_data):

    #config = station_configuration()
    
    subcarriers = subcarriers
    frame_length = frame_length

    gr.hier_block2.__init__(self, "pilot_block_filter",
        gr.io_signature2(2,2,gr.sizeof_gr_complex*subcarriers,gr.sizeof_char),
        gr.io_signature2(2,2,gr.sizeof_gr_complex*subcarriers,gr.sizeof_char))

    filt = skip(gr.sizeof_gr_complex*subcarriers,frame_length)# skip_known_symbols(frame_length,subcarriers)
    for x in training_data.pilotsym_pos:
      filt.skip_call(x)

    self.connect(self,filt)
    self.connect(filt,self)
    self.connect((self,1),(filt,1),(self,1))


################################################################################

class fbmc_inner_pilot_block_filter(gr.hier_block2):
  """
  Remove pilot blocks from ofdm block stream. Frequency domain operation.

  Input 0: ofdm frames
  Input 1: frame trigger
  Output 0: data blocks
  Output 1: frame trigger for data blocks
  """
  def __init__ (self):

    config = station_configuration()
    
    vlen = config.fft_length/2
    frame_length = config.frame_length

    gr.hier_block2.__init__(self, "fbmc_inner_pilot_block_filter",
        gr.io_signature2(2,2,gr.sizeof_gr_complex*vlen,gr.sizeof_char),
        gr.io_signature2(2,2,gr.sizeof_gr_complex*vlen,gr.sizeof_char))

    filt = skip(gr.sizeof_gr_complex*vlen,frame_length)# skip_known_symbols(frame_length,subcarriers)
    for x in config.training_data.fbmc_pilotsym_pos_td:
      filt.skip_call(x)

    self.connect(self,filt)
    self.connect(filt,self)
    self.connect((self,1),(filt,1),(self,1))


################################################################################

class fbmc_pilot_block_filter(gr.hier_block2):
  """
  Remove pilot blocks from ofdm block stream. Frequency domain operation.

  Input 0: ofdm frames
  Input 1: frame trigger
  Output 0: data blocks
  Output 1: frame trigger for data blocks
  """
  def __init__ (self,subcarriers,frame_length,frame_data_part,training_data):

    #config = station_configuration()
    
    subcarriers = subcarriers
    frame_length = frame_length
    frame_data_part = frame_data_part
    

    gr.hier_block2.__init__(self, "fbmc_pilot_block_filter",
        gr.io_signature2(2,2,gr.sizeof_gr_complex*subcarriers,gr.sizeof_char),
        gr.io_signature2(2,2,gr.sizeof_gr_complex*subcarriers,gr.sizeof_char))

    filt = skip(gr.sizeof_gr_complex*subcarriers,frame_length/2)# skip_known_symbols(frame_length,subcarriers)
    for x in training_data.fbmc_pilotsym_pos[:len(training_data.fbmc_pilotsym_pos)/2]:
      filt.skip_call(x)

    self.connect(self,filt)
    self.connect(filt,self)
    self.connect((self,1),(filt,1),(self,1))

################################################################################
class fbmc_snr_filter(gr.hier_block2):
  """
  Remove pilot blocks from ofdm block stream. Frequency domain operation.

  Input 0: ofdm frames
  Input 1: frame trigger
  Output 0: data blocks
  Output 1: frame trigger for data blocks
  """
  def __init__ (self,subcarriers,frame_length,training_data):

    #config = station_configuration()
    

    gr.hier_block2.__init__(self, "fbmc_snr_filter",
        gr.io_signature2(2,2,gr.sizeof_gr_complex*subcarriers,gr.sizeof_char),
        gr.io_signature(1,1,gr.sizeof_gr_complex*subcarriers))

    
    skipping_symbols = [0] + range(training_data.fbmc_no_preambles/2,frame_length/2)
    snr_est_filt = skip(gr.sizeof_gr_complex*subcarriers,frame_length/2)# skip_known_symbols(frame_length,subcarriers)
    
    for x in skipping_symbols:
      snr_est_filt.skip_call(x)

    self.connect(self,snr_est_filt)
    self.connect(snr_est_filt,self)
    self.connect((self,1),(snr_est_filt,1))
 


################################################################################
class ofdm_snr_filter(gr.hier_block2):
  """
  Remove pilot blocks from ofdm block stream. Frequency domain operation.

  Input 0: ofdm frames
  Input 1: frame trigger
  Output 0: data blocks
  Output 1: frame trigger for data blocks
  """
  def __init__ (self,subcarriers,frame_length):

    #config = station_configuration()
    

    gr.hier_block2.__init__(self, "ofdm_snr_filter",
        gr.io_signature2(2,2,gr.sizeof_gr_complex*subcarriers,gr.sizeof_char),
        gr.io_signature(1,1,gr.sizeof_gr_complex*subcarriers))

    
    #skipping_symbols = [0] + range(training_data.fbmc_no_preambles/2,frame_length/2)
    snr_est_filt = skip(gr.sizeof_gr_complex*subcarriers,frame_length)# skip_known_symbols(frame_length,subcarriers)
    
    for x in range(1,frame_length):
      snr_est_filt.skip_call(x)

    self.connect(self,snr_est_filt)
    self.connect(snr_est_filt,self)
    self.connect((self,1),(snr_est_filt,1))
 


################################################################################

class scatterplot_subcarrier_filter(gr.hier_block2):
  """
  Remove pilot blocks from ofdm block stream. Frequency domain operation.

  Input 0: ofdm frames
  Input 1: frame trigger
  Output 0: data blocks
  Output 1: frame trigger for data blocks
  """
  def __init__ (self,subcarriers,data_blocks):

    gr.hier_block2.__init__(self, "fbmc_pilot_block_filter",
        gr.io_signature2(2,2,gr.sizeof_gr_complex*subcarriers,gr.sizeof_char),
        gr.io_signature(1,1,gr.sizeof_gr_complex*subcarriers))

    
    scatter_id_filt = skip(gr.sizeof_gr_complex*subcarriers,data_blocks)
    scatter_id_filt.skip_call(0)

    self.connect(self,scatter_id_filt)
    self.connect(scatter_id_filt,self)
    self.connect((self,1),(scatter_id_filt,1))
 


################################################################################

class pilot_subcarrier_inserter (gr.hier_block2):
  """
  Inserts the pilot symbols at the pilot subcarriers. Input are the data
  subcarriers (as vector), the output vector contains data subcarriers
  muxed with pilot subcarriers. Extends vector size.
  """
  def __init__(self,data_subcarriers,pilots,data_blocks,training_data):

    #config = station_configuration()
    subc = data_subcarriers
    #pilots = training_data.pilot_subcarriers
    total_subc = subc + pilots

    gr.hier_block2.__init__(self,"pilot_subcarrier_inserter",
        gr.io_signature(1,1,gr.sizeof_gr_complex*subc),
        gr.io_signature(1,1,gr.sizeof_gr_complex*total_subc))
    
    ins = ofdm.pilot_subcarrier_inserter( subc,
        config.training_data.pilot_subc_sym,
        config.training_data.pilot_tones )

    self.connect( self, ins, self )
    return 
  

################################################################################

class pilot_subcarrier_inserter_zeroes (gr.hier_block2):
  """
  Inserts the pilot symbols at the pilot subcarriers. Input are the data
  subcarriers (as vector), the output vector contains data subcarriers
  muxed with pilot subcarriers. Extends vector size.
  """
  def __init__(self):

    config = station_configuration()
    subc = config.data_subcarriers
    pilots = config.training_data.pilot_subcarriers
    total_subc = config.subcarriers

    pilot_subc_sym = [0.0] * pilots

    gr.hier_block2.__init__(self,"pilot_subcarrier_inserter_zeroes",
        gr.io_signature(1,1,gr.sizeof_gr_complex*subc),
        gr.io_signature(1,1,gr.sizeof_gr_complex*total_subc))

    ins = ofdm.pilot_subcarrier_inserter( subc,
        pilot_subc_sym,
        config.training_data.pilot_tones )

    self.connect( self, ins, self )
    return


    # decompress partition map
    partition = config.training_data.partition
    mux_stream = []
    next_port = 0
    for x in partition:
      if x > 0:
        mux_stream.extend([next_port]*x)
      next_port = (next_port+1) % 2

    assert(len(mux_stream) == total_subc)
    assert(sum(mux_stream) == pilots)

    imux = []
    for x in mux_stream:
      imux.append(int(x))



    v2s = blocks.vector_to_stream(gr.sizeof_gr_complex,subc)
    pilot_src = blocks.vector_source_c(pilot_subc_sym,True)

    mux = static_mux_c(imux)
    s2v = blocks.stream_to_vector(gr.sizeof_gr_complex,total_subc)

    # vector to stream, mux with pilot subcarrier symbols,
    # reconvert to vector

    self.connect(self,v2s,(mux,0))
    self.connect(pilot_src,(mux,1))
    self.connect(mux,s2v,self)

################################################################################

class pilot_subcarrier_filter (gr.hier_block2):
  """
  Remove pilot subcarriers from subcarriers. Input are the received
  subcarriers (as vector), the output vector only contains data subcarriers.
  Decreases vector size.

  """
  def __init__(self, data_subcarriers, subcarriers, training_data, complex_value=True):

    #config = station_configuration()
    data_subc = data_subcarriers
    subc = subcarriers

    if complex_value:
      itemsize = gr.sizeof_gr_complex
    else:
      itemsize = gr.sizeof_float

    gr.hier_block2.__init__(self,"pilot_subcarrier_filter",
        gr.io_signature(1,1,itemsize*subc),
        gr.io_signature(1,1,itemsize*data_subc))

    # FIXME inefficient

    skipcarrier = skip(itemsize,subc)
    for x in training_data.shifted_pilot_tones:
      skipcarrier.skip_call(x)

    trigger = [0]*subc
    trigger[0] = 1
    trigger_src = blocks.vector_source_b(trigger,True) # FIXME static

    v2s = blocks.vector_to_stream(itemsize,subc)
    s2v = blocks.stream_to_vector(itemsize,data_subc)

    self.connect(self,v2s,skipcarrier,s2v,self)
    self.connect(trigger_src,(skipcarrier,1))

################################################################################

"""
Creates a preamble based on a modified version of park's design.
Can be used for Schmidl's algorithm.
"""
class mod_park_designer:
  def create(subcarriers,fft_length):
    assert(subcarriers%4==0)
    assert((fft_length-subcarriers)%2==0)

    # using park preamble design
    #  A | B* | A | B*
    # with B is symmetric to A

    # select subsequence from fixed pn sequence
    seq1 = fixed_real_pn1[0:subcarriers/2]

    # create periodicity. we use higher amplitude to have same energy in
    # both preambles.
    seq1 = concatenate([[seq1[i]*sqrt(2.0), 0.0] for i in range(subcarriers/2)])

    # transform to time domain
    td = ifft(seq1, (fft_length-subcarriers)/2)
    fd = seq1

    return (td,fd)

  create = staticmethod(create)

  def transform_td(seq):
    # A -> A | B* | A | B*
    # with B symmetric to A
    x = conjugate(seq[1:len(seq)])
    td = concatenate([seq,[seq[0]],x[::-1]]*2)
    assert(len(td)==4*len(seq))
    fd = array(fft(td)) / len(td)
    return (td,fd)

  transform_td = staticmethod(transform_td)

  def transform_fd(seq):
    return mod_park_designer.transform_td(ifft(seq,0))

  transform_fd = staticmethod(transform_fd)

################################################################################

"""
Creates a preamble that is used by the Schmidl's integer frequency offset
estimator.
"""
class schmidl_ifo_designer:
  def create(subcarriers,fft_length):
    assert(subcarriers%2==0)
    assert((fft_length-subcarriers)%2==0)

    # fully loaded ofdm symbol as preamble.
    mod = [1,1j,-1,-1j] # subset of QPSK, |x| = 1.0

    seq1 = [(fixed_real_pn1[2*i]+1)/2+(fixed_real_pn1[2*i+1]+1) for i in range(subcarriers)]
    seq1 = [mod[seq1[i]] for i in range(subcarriers)]
    
    #seq1 = [fixed_real_pn1[i] + ((1j)**(2*i+1))*fixed_real_pn1[i] for i in range(208)]/numpy.sqrt(2)
    
    mimo_mask_1 = zeros(subcarriers,int)
    mimo_mask_2 = zeros(subcarriers,int)
    mimo_mask_1[0::2]=sqrt(2.0)
    mimo_mask_2[1::2]=sqrt(2.0)
    fd_1 = seq1*mimo_mask_1
    fd_2 = seq1*mimo_mask_2
 
    td_1 = ifft(fd_1, (fft_length-subcarriers)/2)
    td_2 = ifft(fd_2, (fft_length-subcarriers)/2)
    # transform to time domain
    td = ifft(seq1, (fft_length-subcarriers)/2)
    fd = seq1

    return (td,fd,td_1,fd_1,td_2,fd_2)

  create = staticmethod(create)

################################################################################

"""
Creates a preamble that is used by the Schmidl's fractional frequency offset
estimator.
"""
class schmidl_ffo_designer:
  def create(subcarriers,fft_length):
    assert(subcarriers%4==0)
    assert((fft_length-subcarriers)%2==0)

    # every second subcarrier loaded. results in a periodicity in time
    # A | A
    mod = [1+1j,1-1j,-1-1j,-1-1j] # subset of QPSK |x|=sqrt(2.0)

    seq1 = [(fixed_real_pn1[2*i]+1)/2+(fixed_real_pn1[2*i+1]+1) for i in range(subcarriers/2)]
    seq1 = concatenate([[mod[seq1[i]],0.0] for i in range(subcarriers/2)])

    # transform to time domain
    td = ifft(seq1, (fft_length-subcarriers)/2)
    fd = seq1

    return (td,fd)

  create = staticmethod(create)

  def transform_td(seq):
    # A -> A | A
    td = concatenate([seq]*2)
    fd = array(fft(td)) / len(td)
    return (td,fd)

  transform_td = staticmethod(transform_td)

  def transform_fd(seq):
    # every second subcarrier to zero
    fd = concatenate([[seq[i],0.0] for i in range(len(seq))])
    td = ifft(fd,0)

    return (td,fd)

  transform_fd = staticmethod(transform_fd)

################################################################################

class morellimengali_designer:
  def create(subcarriers,fft_length,L):
    assert(subcarriers%(2*L)==0)
#    assert((fft_length-subcarriers)%2==0)

    # every subcarrier loaded. results in a periodicity in time
    # A | A
    mod = [1+1j,1-1j,-1-1j,-1-1j] # subset of QPSK |x|=sqrt(2.0)
    mod = numpy.array(mod) * sqrt(L/2.0)

    seq1 = [(fixed_real_pn1[2*i]+1)/2+(fixed_real_pn1[2*i+1]+1) for i in range(subcarriers/L)]
    seq2 = []
    for i in range(subcarriers/L):
      seq2.append([mod[seq1[i]]])
      seq2.append([0.0]*(L-1))
    seq1 = concatenate(seq2)

    # transform to time domain
    td = ifft(seq1, (fft_length-subcarriers)/2)
    fd = seq1

    return (td,fd)

  create = staticmethod(create)

################################################################################

class mod_schmidl_ffo_designer:
  def create(subcarriers,fft_length):
    assert(subcarriers%4 == 0)
    assert((fft_length-subcarriers)%2==0)

    td,fd = cazac_designer.create(subcarriers/2, fft_length/2)
    td,fd = array(schmidl_ffo_designer.transform_td(td))*sqrt(2.0)

    td = [td[i]*float(fixed_real_pn1[i]) for i in range(len(td))]
    fd = array(fft(td,(fft_length-subcarriers)/2)) / len(td)
   #print fd
   # print sum([abs(fd[i])**2 for i in range(len(fd))])

    return (td,fd)

  create = staticmethod(create)


################################################################################

def gcd(a,b):
  """Return greatest common divisor using Euclid's Algorithm."""
  while b:
    a, b = b, a % b
  return a

"""
Create constant amplitude zero autocorrelation preamble.
As by theory, the ifft result of a cazac sequence is a cazac sequence.
The fft window needs to be fully used, i.e. fft_length=subcarriers.
This algorithm should work with any subcarrier number.
"""
class cazac_designer:
  def create(subcarriers,fft_length):
    assert((fft_length-subcarriers)%2==0)
    #assert(subcarriers == fft_length)

    N = subcarriers
    M = 0

    # find number that is relatively prime to subcarrier number
    for i in range(2,N):
      if gcd(i,N) == 1:
        M = i
        break
    assert(gcd(M,N)==1)

    if subcarriers % 2 == 0: #even
      index = lambda k: k**2 +2*k
    else: # odd
      index = lambda k: k*(k+1) +2*k

    fd = [exp(1j*M*pi*index(k)/N) for k in range(N)]
    if fft_length > subcarriers:
      vs = (fft_length-subcarriers)/2
      fd = concatenate([[0.0]*vs,fd,[0.0]*vs])
    td = ifft(fd,0)

    return (td,fd)

  create = staticmethod(create)

################################################################################

fixed_real_pn1 = \
  [ 1, -1, -1, -1, -1, -1,  1,  1,  1, -1,  1, -1,  1,  1,  1, -1,  1, -1,  1,
    1, -1, -1, -1, -1,  1, -1, -1, -1,  1, -1, -1, -1,  1,  1,  1, -1, -1,  1,
   -1, -1, -1,  1,  1,  1,  1, -1, -1, -1,  1, -1, -1, -1, -1,  1, -1,  1, -1,
   -1,  1,  1,  1, -1,  1, -1, -1,  1, -1, -1,  1,  1, -1,  1,  1,  1, -1,  1,
   -1, -1, -1,  1, -1, -1,  1,  1, -1, -1, -1,  1,  1,  1, -1,  1,  1, -1, -1,
   -1, -1,  1, -1, -1, -1, -1, -1, -1,  1,  1,  1, -1,  1, -1,  1, -1, -1, -1,
   -1, -1,  1,  1, -1,  1,  1,  1,  1, -1, -1, -1,  1, -1,  1,  1, -1, -1, -1,
    1, -1,  1, -1,  1, -1,  1,  1, -1, -1, -1,  1,  1, -1, -1,  1,  1, -1,  1,
   -1,  1, -1,  1, -1,  1,  1,  1,  1, -1, -1, -1,  1,  1,  1,  1, -1, -1, -1,
   -1, -1,  1,  1, -1, -1,  1, -1,  1, -1,  1,  1,  1, -1, -1, -1, -1,  1,  1,
   -1,  1, -1, -1,  1, -1,  1, -1,  1, -1, -1, -1, -1, -1,  1, -1,  1, -1, -1,
   -1, -1,  1,  1,  1,  1, -1,  1,  1,  1,  1,  1, -1, -1, -1, -1, -1,  1,  1,
   -1,  1, -1, -1,  1, -1,  1, -1, -1, -1,  1, -1,  1, -1, -1, -1,  1,  1, -1,
   -1, -1, -1, -1, -1,  1,  1,  1,  1, -1, -1, -1,  1, -1,  1, -1, -1, -1, -1,
    1, -1, -1,  1,  1, -1,  1, -1,  1, -1, -1, -1, -1,  1, -1,  1, -1, -1, -1,
   -1,  1, -1,  1, -1, -1,  1,  1, -1,  1,  1, -1, -1, -1,  1,  1,  1,  1,  1,
   -1, -1,  1, -1,  1,  1, -1, -1, -1,  1, -1,  1, -1, -1,  1,  1, -1,  1, -1,
   -1, -1,  1, -1, -1,  1, -1, -1, -1,  1, -1,  1,  1, -1,  1, -1,  1, -1,  1,
    1, -1, -1, -1,  1,  1, -1,  1, -1, -1,  1, -1, -1, -1, -1, -1,  1, -1, -1,
   -1, -1, -1,  1,  1, -1, -1, -1, -1, -1,  1, -1, -1,  1,  1, -1,  1,  1,  1,
   -1, -1,  1,  1,  1,  1,  1,  1,  1,  1,  1, -1, -1,  1,  1, -1,  1, -1,  1,
    1, -1,  1, -1, -1,  1, -1, -1,  1, -1,  1,  1,  1, -1,  1,  1, -1,  1,  1,
   -1, -1,  1, -1, -1,  1, -1, -1,  1, -1,  1,  1, -1, -1, -1,  1,  1,  1,  1,
    1, -1,  1,  1, -1, -1,  1, -1,  1,  1, -1, -1, -1,  1,  1, -1, -1,  1,  1,
    1, -1,  1,  1, -1, -1,  1, -1, -1, -1, -1,  1, -1, -1, -1, -1,  1, -1,  1,
   -1, -1, -1, -1,  1, -1, -1,  1,  1, -1,  1,  1, -1,  1, -1,  1,  1,  1, -1,
    1,  1, -1,  1, -1, -1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1, -1,
   -1, -1,  1, -1, -1, -1,  1,  1, -1,  1, -1,  1,  1,  1, -1, -1,  1,  1,  1,
    1, -1, -1, -1,  1,  1,  1, -1, -1, -1,  1, -1,  1, -1,  1,  1, -1, -1, -1,
   -1,  1, -1, -1, -1,  1,  1, -1, -1,  1,  1,  1,  1, -1,  1,  1,  1,  1,  1,
   -1, -1,  1, -1, -1, -1, -1,  1, -1, -1, -1, -1,  1, -1, -1, -1,  1, -1, -1,
   -1, -1, -1, -1,  1,  1,  1,  1,  1, -1, -1, -1, -1,  1, -1, -1, -1, -1, -1,
    1,  1, -1,  1, -1, -1, -1, -1,  1,  1, -1,  1,  1,  1, -1, -1, -1, -1,  1,
    1,  1,  1, -1, -1, -1, -1, -1,  1,  1,  1,  1, -1,  1,  1,  1, -1, -1, -1,
    1,  1, -1, -1,  1,  1, -1, -1, -1,  1, -1, -1, -1,  1,  1,  1, -1,  1, -1,
   -1, -1,  1,  1,  1,  1,  1,  1,  1, -1,  1,  1,  1, -1,  1,  1,  1,  1, -1,
    1, -1, -1,  1, -1, -1,  1,  1, -1,  1,  1, -1,  1,  1, -1,  1, -1, -1,  1,
    1, -1,  1,  1, -1,  1, -1, -1, -1,  1, -1,  1,  1, -1,  1,  1, -1,  1,  1,
   -1,  1,  1,  1,  1,  1,  1,  1,  1,  1, -1, -1,  1, -1,  1,  1, -1, -1,  1,
    1,  1, -1, -1,  1, -1, -1, -1,  1, -1,  1,  1, -1,  1,  1, -1, -1, -1,  1,
   -1,  1,  1,  1, -1, -1,  1,  1, -1, -1,  1, -1, -1, -1,  1, -1,  1,  1,  1,
   -1,  1, -1, -1,  1, -1,  1,  1,  1,  1, -1, -1,  1,  1,  1,  1, -1,  1,  1,
    1, -1, -1, -1,  1, -1,  1, -1,  1, -1,  1, -1,  1,  1,  1,  1,  1, -1, -1,
   -1, -1,  1, -1, -1, -1,  1,  1,  1, -1, -1,  1, -1,  1, -1,  1,  1, -1, -1,
    1, -1,  1,  1, -1, -1, -1,  1, -1,  1, -1, -1, -1,  1,  1, -1, -1,  1, -1,
    1,  1, -1, -1, -1, -1, -1,  1,  1,  1,  1, -1, -1,  1,  1, -1, -1,  1,  1,
    1,  1, -1, -1, -1, -1,  1, -1,  1, -1,  1, -1, -1, -1, -1,  1,  1, -1,  1,
   -1,  1, -1, -1,  1, -1,  1, -1,  1,  1, -1, -1, -1,  1, -1,  1, -1,  1,  1,
    1,  1, -1, -1, -1, -1, -1, -1,  1, -1,  1,  1, -1, -1, -1, -1,  1,  1,  1,
   -1, -1,  1,  1,  1,  1, -1,  1, -1,  1,  1,  1, -1, -1, -1, -1, -1, -1,  1,
   -1,  1, -1, -1,  1,  1,  1,  1,  1,  1, -1,  1, -1, -1, -1,  1,  1, -1,  1,
   -1,  1, -1, -1,  1, -1,  1, -1,  1, -1,  1,  1, -1, -1,  1,  1,  1,  1, -1,
   -1,  1,  1, -1, -1, -1,  1, -1, -1,  1,  1, -1,  1,  1, -1, -1, -1,  1, -1,
   -1, -1,  1, -1, -1,  1, -1, -1, -1,  1, -1, -1, -1,  1,  1,  1, -1,  1,  1,
    1, -1, -1, -1, -1,  1, -1,  1, -1, -1, -1, -1,  1, -1,  1, -1, -1,  1, -1,
   -1,  1,  1, -1, -1,  1, -1, -1,  1, -1, -1,  1, -1, -1, -1, -1,  1, -1,  1,
    1,  1,  1, -1, -1,  1, -1,  1,  1,  1, -1, -1,  1,  1, -1,  1, -1,  1, -1,
   -1, -1, -1, -1,  1,  1, -1, -1,  1,  1,  1, -1,  1, -1, -1,  1,  1, -1, -1,
    1, -1, -1, -1, -1,  1,  1, -1, -1,  1, -1,  1,  1,  1,  1, -1, -1, -1, -1,
   -1,  1, -1,  1, -1, -1,  1,  1,  1, -1,  1, -1,  1,  1,  1,  1,  1, -1, -1,
    1,  1, -1,  1,  1, -1,  1,  1,  1, -1, -1, -1,  1,  1,  1, -1,  1, -1,  1,
   -1,  1,  1, -1, -1,  1,  1,  1, -1, -1, -1, -1,  1,  1, -1,  1, -1,  1, -1,
    1, -1,  1, -1,  1, -1,  1,  1, -1,  1, -1,  1, -1,  1,  1,  1, -1, -1,  1,
   -1, -1,  1,  1,  1, -1, -1,  1,  1, -1,  1, -1,  1,  1,  1,  1, -1,  1,  1,
   -1, -1, -1, -1, -1, -1,  1,  1,  1,  1, -1,  1,  1,  1,  1,  1, -1, -1,  1,
    1,  1,  1, -1, -1,  1, -1,  1,  1, -1, -1,  1, -1, -1, -1,  1, -1, -1,  1,
   -1, -1,  1, -1,  1,  1, -1,  1, -1, -1, -1, -1, -1, -1,  1,  1, -1,  1, -1,
   -1, -1,  1, -1,  1,  1, -1,  1, -1, -1,  1, -1,  1,  1,  1, -1,  1,  1,  1,
   -1, -1,  1, -1, -1, -1, -1, -1, -1,  1, -1, -1,  1, -1, -1, -1,  1,  1,  1,
   -1, -1, -1, -1, -1, -1, -1,  1,  1,  1, -1,  1, -1, -1,  1,  1, -1, -1, -1,
   -1, -1,  1,  1,  1,  1, -1,  1,  1, -1, -1, -1,  1,  1,  1, -1,  1,  1,  1,
   -1, -1, -1, -1,  1, -1, -1, -1, -1, -1,  1,  1, -1,  1, -1,  1,  1, -1, -1,
    1,  1,  1, -1, -1,  1, -1,  1,  1,  1,  1,  1, -1, -1, -1, -1, -1,  1,  1,
    1,  1,  1, -1, -1, -1, -1, -1,  1,  1, -1,  1, -1,  1, -1, -1, -1, -1,  1,
    1, -1,  1,  1, -1, -1,  1,  1,  1, -1, -1, -1,  1,  1, -1, -1, -1, -1,  1,
    1, -1,  1,  1, -1, -1, -1, -1, -1, -1,  1,  1, -1, -1, -1,  1,  1,  1, -1,
    1, -1,  1, -1, -1, -1,  1,  1, -1, -1, -1, -1,  1,  1, -1,  1,  1, -1,  1,
    1,  1, -1,  1,  1, -1, -1,  1, -1, -1, -1,  1,  1, -1,  1, -1,  1,  1, -1,
    1, -1, -1, -1, -1, -1, -1,  1, -1, -1,  1,  1, -1,  1, -1,  1, -1,  1, -1,
    1, -1, -1,  1,  1, -1, -1, -1,  1,  1,  1,  1,  1,  1, -1, -1,  1,  1,  1,
   -1, -1,  1,  1,  1,  1,  1, -1,  1,  1, -1,  1,  1,  1,  1, -1,  1, -1,  1,
   -1,  1, -1,  1,  1,  1,  1,  1, -1, -1,  1, -1,  1, -1, -1, -1,  1, -1,  1,
    1, -1,  1,  1, -1,  1,  1,  1,  1, -1, -1,  1,  1, -1, -1,  1, -1, -1,  1,
    1, -1, -1, -1, -1,  1, -1,  1, -1, -1,  1,  1,  1,  1,  1,  1, -1, -1, -1,
   -1,  1, -1,  1,  1,  1,  1,  1,  1, -1,  1,  1, -1,  1,  1, -1,  1, -1, -1,
   -1,  1,  1,  1,  1,  1, -1, -1,  1, -1, -1,  1,  1,  1,  1,  1,  1,  1,  1,
    1, -1,  1, -1, -1, -1, -1, -1, -1, -1, -1,  1, -1,  1,  1, -1,  1, -1, -1,
   -1,  1,  1, -1,  1,  1, -1,  1,  1,  1, -1,  1,  1, -1,  1,  1,  1,  1,  1,
    1, -1, -1,  1,  1, -1,  1, -1, -1, -1,  1, -1, -1,  1,  1, -1,  1, -1,  1,
   -1, -1,  1, -1, -1,  1,  1,  1,  1,  1,  1,  1, -1,  1,  1, -1, -1,  1, -1,
   -1, -1,  1,  1,  1, -1,  1,  1, -1,  1, -1, -1, -1, -1, -1,  1,  1, -1, -1,
    1,  1,  1, -1, -1, -1, -1, -1,  1,  1, -1, -1, -1, -1, -1,  1, -1,  1, -1,
    1,  1,  1,  1, -1, -1,  1,  1, -1, -1,  1,  1, -1,  1, -1, -1,  1, -1,  1,
   -1, -1,  1, -1,  1, -1,  1, -1,  1,  1, -1,  1,  1, -1,  1,  1, -1, -1, -1,
   -1,  1, -1,  1, -1,  1, -1,  1, -1, -1, -1,  1,  1, -1,  1,  1, -1, -1, -1,
    1,  1, -1,  1,  1,  1, -1, -1, -1,  1,  1,  1,  1, -1, -1,  1,  1, -1,  1,
    1, -1,  1,  1,  1,  1, -1, -1, -1,  1, -1, -1,  1,  1, -1, -1, -1, -1,  1,
   -1, -1,  1,  1,  1,  1,  1,  1,  1, -1,  1, -1, -1, -1,  1, -1, -1, -1,  1,
    1,  1,  1, -1,  1, -1, -1,  1, -1,  1,  1,  1,  1,  1, -1, -1,  1,  1,  1,
    1,  1, -1, -1, -1, -1,  1,  1,  1,  1,  1, -1,  1,  1, -1,  1, -1,  1, -1,
    1,  1,  1, -1,  1,  1,  1, -1,  1, -1,  1,  1,  1,  1, -1, -1,  1, -1, -1,
    1, -1, -1,  1,  1,  1,  1, -1, -1, -1, -1, -1,  1, -1, -1, -1,  1, -1,  1,
   -1, -1, -1,  1,  1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  1,  1,  1, -1, -1,
   -1, -1, -1,  1,  1, -1, -1,  1, -1,  1, -1,  1, -1, -1,  1, -1, -1,  1,  1,
   -1, -1, -1,  1,  1, -1,  1,  1,  1,  1,  1,  1,  1,  1, -1,  1, -1, -1, -1,
   -1, -1,  1,  1, -1, -1, -1, -1,  1,  1,  1,  1, -1, -1,  1, -1, -1,  1,  1,
   -1,  1, -1,  1, -1, -1, -1,  1,  1, -1, -1, -1,  1,  1,  1, -1, -1,  1, -1,
    1,  1,  1, -1, -1,  1,  1, -1, -1, -1, -1, -1,  1, -1, -1, -1, -1, -1,  1,
    1, -1, -1, -1, -1,  1,  1,  1, -1, -1,  1, -1,  1,  1, -1, -1, -1, -1,  1,
    1, -1,  1, -1, -1,  1,  1,  1, -1,  1,  1, -1,  1,  1,  1, -1, -1, -1,  1,
   -1, -1,  1,  1,  1,  1,  1,  1,  1,  1, -1, -1,  1, -1, -1, -1,  1, -1,  1,
   -1, -1,  1,  1, -1, -1,  1,  1,  1,  1, -1, -1,  1,  1,  1, -1,  1, -1, -1,
   -1, -1, -1,  1, -1,  1,  1,  1,  1, -1, -1, -1,  1,  1, -1, -1, -1,  1, -1,
   -1, -1, -1,  1,  1,  1,  1,  1, -1, -1,  1,  1, -1,  1,  1,  1,  1,  1, -1,
    1, -1, -1, -1, -1,  1,  1, -1,  1, -1,  1,  1, -1, -1, -1,  1, -1,  1,  1,
   -1,  1,  1,  1,  1,  1,  1,  1,  1,  1, -1,  1,  1, -1, -1,  1, -1, -1, -1,
    1, -1, -1, -1, -1,  1,  1, -1, -1, -1, -1,  1,  1, -1,  1, -1,  1,  1,  1,
   -1, -1, -1,  1, -1, -1, -1,  1, -1, -1,  1,  1,  1,  1, -1, -1, -1,  1,  1,
    1, -1,  1,  1,  1,  1, -1,  1, -1, -1, -1,  1, -1, -1, -1,  1, -1,  1, -1,
    1, -1,  1, -1,  1, -1,  1, -1,  1, -1, -1,  1, -1,  1, -1,  1,  1,  1, -1,
    1,  1, -1,  1, -1, -1,  1,  1, -1,  1,  1, -1,  1, -1, -1, -1,  1, -1,  1,
   -1,  1,  1,  1, -1,  1, -1,  1,  1, -1,  1,  1,  1, -1, -1, -1,  1, -1,  1,
   -1, -1, -1, -1, -1, -1,  1, -1,  1, -1,  1,  1, -1, -1, -1,  1, -1,  1, -1,
    1, -1, -1, -1, -1,  1, -1, -1,  1,  1,  1,  1,  1,  1, -1, -1,  1, -1,  1,
    1, -1,  1,  1,  1,  1, -1,  1, -1,  1, -1,  1,  1, -1,  1, -1,  1, -1,  1,
   -1,  1, -1,  1,  1, -1,  1, -1, -1, -1, -1, -1,  1, -1,  1, -1, -1,  1,  1,
   -1,  1,  1, -1,  1,  1,  1,  1,  1,  1, -1,  1, -1,  1,  1,  1,  1, -1, -1,
    1,  1, -1,  1, -1,  1, -1,  1,  1,  1, -1, -1,  1,  1,  1,  1,  1,  1,  1,
    1, -1,  1, -1, -1, -1,  1, -1,  1,  1,  1,  1,  1, -1, -1,  1, -1,  1,  1,
   -1, -1, -1,  1,  1,  1, -1,  1, -1, -1,  1, -1, -1, -1, -1, -1,  1,  1, -1,
    1, -1, -1, -1, -1, -1,  1,  1,  1,  1,  1,  1,  1,  1,  1, -1,  1,  1,  1,
   -1, -1,  1, -1, -1,  1, -1,  1,  1, -1, -1,  1, -1,  1,  1, -1, -1,  1, -1,
   -1, -1,  1,  1, -1, -1, -1,  1,  1,  1, -1, -1, -1,  1, -1, -1, -1,  1,  1,
    1,  1, -1,  1, -1, -1,  1, -1,  1,  1,  1,  1, -1,  1, -1, -1, -1, -1, -1,
    1, -1, -1,  1,  1, -1, -1, -1,  1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  1,
   -1,  1, -1,  1,  1,  1, -1, -1, -1, -1, -1,  1, -1, -1,  1, -1, -1,  1, -1,
   -1, -1, -1, -1,  1,  1,  1, -1,  1,  1,  1,  1, -1, -1,  1,  1, -1,  1, -1,
   -1, -1,  1,  1,  1,  1,  1,  1,  1, -1,  1, -1, -1,  1,  1, -1, -1, -1, -1,
   -1, -1, -1,  1, -1, -1,  1,  1, -1, -1,  1,  1,  1,  1,  1,  1, -1, -1,  1,
   -1,  1, -1,  1,  1,  1,  1, -1, -1, -1,  1,  1, -1, -1,  1,  1, -1, -1, -1,
   -1, -1,  1, -1, -1,  1,  1, -1,  1, -1, -1,  1,  1, -1, -1,  1,  1,  1,  1,
   -1,  1, -1,  1,  1,  1,  1, -1,  1, -1, -1, -1, -1, -1,  1, -1,  1, -1, -1,
    1, -1,  1,  1, -1,  1,  1, -1,  1, -1,  1,  1,  1,  1,  1,  1, -1,  1, -1,
    1, -1,  1,  1,  1,  1, -1, -1, -1, -1,  1, -1,  1, -1, -1,  1, -1,  1, -1,
   -1, -1, -1, -1, -1,  1, -1,  1,  1, -1, -1, -1, -1, -1,  1,  1,  1,  1,  1,
   -1,  1,  1,  1,  1, -1,  1,  1, -1,  1,  1, -1, -1, -1, -1, -1, -1,  1,  1,
    1, -1,  1,  1, -1, -1,  1, -1,  1, -1,  1, -1,  1,  1, -1,  1,  1,  1, -1,
    1,  1,  1, -1,  1, -1,  1,  1,  1, -1,  1, -1,  1,  1, -1, -1,  1, -1,  1,
   -1, -1, -1,  1,  1, -1,  1, -1, -1,  1,  1, -1, -1, -1, -1,  1,  1,  1, -1,
   -1, -1,  1,  1, -1,  1,  1,  1, -1, -1, -1,  1, -1,  1, -1, -1,  1,  1,  1,
    1,  1,  1,  1, -1, -1, -1,  1, -1,  1,  1, -1, -1,  1, -1,  1,  1, -1,  1,
    1, -1,  1, -1, -1, -1, -1,  1,  1,  1, -1, -1, -1, -1, -1,  1,  1,  1,  1,
   -1, -1, -1,  1,  1,  1,  1,  1, -1, -1, -1,  1, -1, -1,  1, -1,  1,  1, -1,
   -1, -1, -1,  1, -1,  1,  1,  1,  1,  1, -1, -1,  1, -1, -1,  1, -1, -1,  1,
    1, -1, -1,  1,  1, -1, -1, -1, -1, -1,  1,  1, -1,  1,  1,  1,  1,  1, -1,
    1,  1,  1, -1,  1,  1,  1,  1, -1,  1,  1,  1,  1, -1, -1, -1,  1, -1,  1,
   -1, -1, -1, -1,  1,  1, -1,  1,  1, -1,  1,  1,  1,  1, -1,  1, -1,  1, -1,
    1, -1, -1, -1, -1,  1,  1, -1, -1, -1, -1, -1,  1,  1, -1, -1,  1, -1,  1,
    1,  1, -1, -1, -1,  1, -1, -1, -1,  1, -1, -1,  1,  1,  1, -1, -1, -1, -1,
   -1,  1,  1,  1,  1,  1,  1, -1,  1, -1, -1,  1, -1,  1, -1,  1, -1, -1,  1,
    1, -1, -1,  1,  1, -1,  1,  1,  1, -1,  1,  1,  1,  1, -1, -1, -1, -1,  1,
   -1,  1, -1, -1, -1,  1, -1, -1,  1, -1,  1,  1, -1,  1, -1,  1, -1, -1,  1,
    1, -1,  1, -1, -1, -1, -1, -1, -1,  1,  1, -1, -1, -1,  1,  1, -1, -1, -1,
    1,  1, -1, -1, -1, -1, -1, -1,  1,  1, -1, -1,  1,  1, -1, -1, -1, -1, -1,
   -1, -1, -1,  1,  1, -1,  1, -1,  1, -1, -1,  1, -1, -1, -1,  1, -1,  1, -1,
   -1,  1,  1,  1,  1,  1,  1, -1,  1, -1, -1, -1,  1,  1, -1,  1,  1,  1,  1,
    1,  1,  1,  1,  1, -1, -1, -1,  1,  1, -1, -1,  1, -1, -1,  1, -1,  1, -1,
   -1,  1,  1,  1,  1,  1, -1,  1,  1, -1, -1, -1, -1,  1, -1,  1,  1,  1, -1,
    1,  1,  1,  1, -1,  1, -1, -1, -1, -1,  1,  1, -1,  1,  1,  1,  1,  1,  1,
    1,  1,  1,  1,  1,  1,  1,  1,  1,  1, -1, -1, -1,  1,  1, -1,  1, -1, -1,
    1,  1,  1, -1, -1,  1, -1, -1,  1,  1, -1, -1,  1,  1, -1, -1,  1, -1,  1,
   -1, -1,  1,  1, -1,  1,  1, -1, -1, -1, -1, -1, -1,  1, -1, -1, -1,  1, -1,
    1, -1,  1, -1,  1, -1,  1, -1,  1,  1,  1, -1,  1,  1,  1,  1, -1, -1, -1,
   -1, -1, -1, -1, -1, -1, -1,  1, -1,  1,  1, -1,  1, -1,  1, -1, -1,  1,  1,
   -1,  1, -1,  1,  1, -1, -1, -1, -1, -1, -1, -1,  1,  1,  1, -1,  1, -1,  1,
   -1,  1, -1, -1, -1, -1, -1,  1, -1,  1, -1, -1,  1,  1, -1,  1, -1, -1,  1,
    1,  1,  1, -1, -1,  1, -1,  1,  1,  1, -1,  1,  1,  1,  1, -1, -1, -1,  1,
    1, -1, -1,  1, -1, -1, -1,  1,  1,  1,  1, -1, -1,  1, -1,  1,  1, -1, -1,
   -1,  1, -1,  1,  1,  1, -1,  1, -1, -1,  1, -1,  1, -1,  1,  1, -1,  1,  1,
   -1,  1,  1, -1, -1, -1, -1, -1,  1, -1, -1,  1,  1, -1,  1, -1,  1,  1, -1,
   -1,  1, -1, -1,  1,  1,  1,  1,  1, -1, -1, -1, -1,  1,  1, -1,  1, -1, -1,
    1,  1, -1, -1, -1, -1, -1,  1, -1, -1, -1,  1, -1,  1,  1,  1,  1,  1,  1,
    1,  1,  1,  1,  1,  1,  1,  1, -1,  1,  1, -1,  1,  1, -1, -1,  1,  1, -1,
    1, -1,  1,  1,  1, -1,  1, -1, -1, -1, -1, -1,  1,  1, -1,  1, -1, -1, -1,
   -1, -1,  1, -1,  1,  1,  1, -1, -1, -1, -1, -1, -1,  1, -1,  1,  1, -1,  1,
   -1,  1,  1, -1, -1, -1,  1, -1,  1, -1, -1, -1,  1,  1, -1, -1,  1, -1,  1,
    1,  1, -1,  1,  1,  1, -1, -1, -1, -1, -1,  1,  1, -1, -1,  1,  1,  1,  1,
   -1, -1, -1,  1,  1, -1, -1, -1,  1,  1,  1,  1,  1, -1,  1,  1, -1, -1, -1,
   -1,  1,  1, -1, -1,  1, -1, -1, -1, -1, -1, -1,  1,  1, -1, -1, -1, -1,  1,
    1,  1, -1,  1,  1,  1, -1, -1, -1,  1,  1,  1, -1, -1, -1, -1,  1,  1,  1,
    1, -1,  1,  1,  1,  1, -1,  1, -1, -1,  1, -1,  1, -1, -1,  1, -1,  1, -1,
    1,  1, -1, -1,  1,  1,  1,  1,  1, -1,  1,  1, -1,  1,  1,  1,  1,  1, -1,
   -1, -1,  1, -1, -1, -1,  1, -1,  1,  1,  1, -1, -1,  1,  1,  1,  1,  1,  1,
    1,  1,  1, -1,  1, -1, -1,  1,  1,  1, -1,  1, -1,  1, -1,  1,  1,  1,  1,
   -1,  1, -1,  1,  1, -1, -1,  1, -1, -1, -1,  1,  1,  1,  1, -1, -1, -1,  1,
    1, -1, -1, -1,  1,  1, -1,  1, -1,  1,  1,  1,  1,  1,  1,  1, -1,  1,  1,
   -1, -1, -1,  1, -1, -1,  1, -1, -1,  1,  1,  1,  1,  1,  1, -1,  1, -1,  1,
   -1, -1,  1, -1, -1,  1, -1, -1, -1, -1,  1,  1, -1, -1, -1, -1,  1, -1, -1,
   -1,  1,  1, -1,  1,  1, -1, -1,  1,  1,  1,  1,  1, -1, -1, -1,  1,  1,  1,
   -1, -1, -1, -1,  1,  1,  1, -1, -1, -1,  1, -1,  1, -1,  1,  1,  1,  1,  1,
   -1,  1,  1,  1, -1, -1, -1,  1,  1,  1,  1, -1,  1,  1, -1,  1,  1, -1, -1,
   -1,  1,  1, -1,  1,  1, -1, -1,  1,  1, -1, -1, -1,  1, -1, -1, -1,  1,  1,
    1, -1, -1,  1, -1,  1, -1,  1,  1,  1, -1, -1,  1,  1, -1, -1,  1, -1, -1,
    1, -1,  1, -1,  1, -1,  1,  1,  1, -1, -1,  1,  1, -1,  1, -1, -1, -1,  1,
    1,  1, -1, -1,  1, -1,  1,  1, -1, -1, -1,  1,  1, -1,  1,  1, -1,  1,  1,
    1, -1,  1,  1,  1,  1, -1,  1,  1,  1, -1, -1, -1, -1,  1,  1,  1,  1,  1,
    1,  1,  1, -1, -1,  1,  1,  1,  1, -1, -1, -1,  1,  1,  1,  1,  1, -1, -1,
    1, -1, -1,  1, -1, -1, -1, -1,  1, -1, -1, -1, -1,  1,  1,  1,  1, -1,  1,
   -1, -1, -1, -1,  1, -1, -1, -1, -1, -1,  1,  1,  1, -1, -1,  1, -1,  1,  1,
    1, -1,  1, -1,  1, -1, -1,  1, -1,  1, -1, -1, -1, -1,  1,  1, -1, -1, -1,
   -1, -1,  1,  1,  1,  1,  1, -1, -1, -1,  1, -1, -1,  1, -1, -1,  1,  1,  1,
    1,  1, -1, -1,  1, -1, -1, -1,  1,  1, -1,  1, -1,  1, -1,  1,  1,  1,  1,
    1, -1,  1, -1,  1,  1,  1,  1, -1, -1,  1, -1,  1,  1,  1, -1,  1,  1, -1,
   -1, -1, -1, -1, -1, -1, -1,  1,  1, -1, -1,  1,  1, -1,  1,  1, -1, -1,  1,
    1,  1,  1,  1,  1, -1, -1,  1,  1, -1,  1,  1, -1, -1, -1,  1, -1, -1,  1,
   -1,  1,  1,  1, -1,  1, -1, -1,  1, -1, -1]

fixed_real_pn2 = concatenate( \
 [[ 1,  1, -1, -1, -1,  1,  1, -1, -1, -1,  1, -1,  1,  1, -1, -1],
  [ 1,  1, -1, -1,  1,  1,  1,  1, -1, -1, -1, -1,  1,  1, -1,  1],
  [-1, -1,  1,  1, -1,  1, -1,  1, -1, -1,  1, -1,  1, -1, -1, -1],
  [-1,  1,  1,  1,  1, -1,  1,  1, -1, -1, -1, -1, -1,  1, -1,  1],
  [-1, -1, -1, -1,  1, -1, -1, -1,  1, -1, -1,  1, -1,  1, -1,  1],
  [ 1,  1, -1,  1, -1,  1,  1,  1,  1,  1, -1, -1, -1,  1,  1, -1],
  [ 1, -1, -1, -1,  1, -1, -1,  1, -1,  1,  1, -1, -1,  1, -1,  1],
  [ 1,  1,  1, -1,  1,  1, -1, -1,  1,  1, -1, -1, -1, -1,  1, -1],
  [-1,  1, -1, -1,  1,  1, -1, -1,  1,  1, -1, -1, -1, -1, -1, -1],
  [ 1, -1, -1,  1, -1,  1,  1,  1, -1, -1, -1, -1, -1, -1, -1, -1],
  [-1,  1,  1, -1,  1,  1,  1, -1, -1, -1, -1,  1, -1,  1, -1,  1],
  [-1,  1, -1, -1, -1, -1,  1,  1,  1,  1,  1,  1, -1, -1,  1, -1],
  [ 1, -1,  1,  1, -1, -1, -1,  1, -1, -1,  1,  1,  1, -1,  1,  1],
  [ 1, -1, -1,  1,  1, -1, -1, -1, -1,  1, -1,  1,  1, -1, -1, -1],
  [-1,  1, -1,  1,  1,  1, -1, -1,  1,  1, -1, -1, -1, -1,  1,  1],
  [-1, -1,  1,  1,  1, -1, -1,  1,  1,  1, -1, -1, -1, -1, -1, -1],
  [-1,  1,  1, -1,  1, -1,  1, -1,  1, -1,  1,  1, -1, -1,  1,  1],
  [-1, -1,  1, -1,  1, -1, -1,  1, -1, -1, -1, -1, -1, -1, -1,  1],
  [ 1, -1,  1,  1, -1,  1,  1,  1,  1,  1,  1,  1, -1, -1, -1,  1],
  [-1, -1, -1, -1,  1,  1, -1,  1,  1, -1, -1,  1, -1, -1,  1,  1],
  [-1, -1,  1, -1,  1,  1, -1,  1,  1, -1,  1,  1,  1,  1,  1,  1],
  [ 1, -1,  1,  1, -1, -1,  1,  1,  1, -1,  1,  1, -1,  1,  1, -1],
  [ 1,  1,  1,  1, -1, -1,  1,  1,  1,  1,  1, -1, -1,  1, -1,  1],
  [ 1,  1,  1,  1, -1, -1,  1, -1,  1,  1,  1, -1, -1,  1,  1, -1],
  [ 1,  1,  1,  1,  1, -1,  1, -1,  1,  1,  1, -1, -1, -1, -1,  1],
  [-1, -1, -1,  1, -1, -1, -1,  1,  1, -1,  1, -1, -1,  1,  1,  1],
  [-1, -1,  1, -1, -1,  1, -1,  1, -1, -1,  1, -1,  1,  1,  1,  1],
  [ 1, -1, -1,  1, -1, -1,  1,  1, -1, -1,  1,  1,  1,  1,  1,  1],
  [ 1, -1,  1, -1,  1, -1,  1,  1,  1, -1, -1,  1,  1,  1, -1,  1],
  [-1, -1,  1,  1, -1,  1,  1, -1,  1,  1, -1,  1, -1,  1,  1, -1],
  [-1, -1,  1,  1, -1,  1,  1, -1,  1,  1,  1,  1, -1, -1,  1, -1],
  [ 1,  1,  1,  1,  1, -1, -1,  1,  1,  1, -1,  1,  1,  1,  1, -1],
  [ 1, -1,  1,  1, -1,  1,  1,  1, -1,  1,  1,  1,  1,  1,  1,  1],
  [-1, -1,  1, -1,  1,  1, -1, -1, -1,  1,  1, -1,  1,  1,  1, -1],
  [ 1, -1,  1, -1,  1, -1, -1, -1, -1,  1, -1, -1,  1,  1,  1,  1],
  [-1,  1, -1, -1,  1, -1, -1,  1,  1, -1,  1, -1,  1, -1, -1, -1],
  [ 1, -1,  1,  1, -1,  1,  1,  1, -1,  1, -1,  1, -1, -1,  1, -1],
  [ 1,  1,  1, -1, -1, -1, -1, -1, -1,  1,  1,  1, -1, -1,  1,  1],
  [-1, -1, -1,  1,  1,  1, -1, -1, -1, -1, -1,  1, -1, -1, -1, -1],
  [-1,  1,  1,  1, -1, -1, -1,  1,  1, -1, -1,  1,  1,  1, -1,  1],
  [ 1,  1, -1, -1,  1, -1,  1, -1, -1,  1,  1, -1, -1,  1, -1,  1],
  [-1, -1, -1, -1, -1,  1,  1,  1,  1, -1, -1,  1, -1,  1,  1, -1],
  [-1,  1,  1, -1, -1, -1,  1,  1,  1, -1, -1,  1,  1, -1, -1, -1],
  [ 1,  1, -1,  1, -1,  1,  1, -1,  1, -1,  1,  1,  1, -1, -1, -1],
  [ 1,  1, -1, -1,  1, -1, -1,  1, -1,  1,  1,  1,  1,  1, -1, -1],
  [ 1,  1, -1,  1,  1,  1, -1,  1,  1,  1,  1,  1, -1, -1,  1, -1],
  [ 1, -1, -1, -1,  1, -1,  1,  1, -1,  1, -1, -1,  1,  1,  1, -1],
  [ 1, -1,  1, -1,  1, -1, -1, -1, -1, -1, -1, -1, -1,  1, -1,  1],
  [ 1, -1,  1,  1, -1, -1, -1, -1, -1, -1, -1, -1,  1, -1, -1, -1],
  [-1, -1,  1,  1,  1,  1,  1,  1, -1,  1,  1,  1,  1,  1, -1, -1],
  [ 1,  1,  1,  1, -1,  1, -1, -1,  1,  1,  1, -1,  1,  1,  1,  1],
  [ 1, -1, -1, -1,  1,  1, -1, -1, -1, -1, -1,  1, -1, -1,  1, -1],
  [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  1,  1,  1, -1,  1, -1],
  [-1, -1,  1, -1, -1, -1,  1, -1,  1, -1, -1, -1,  1,  1, -1,  1],
  [ 1, -1,  1, -1, -1, -1,  1,  1,  1,  1, -1,  1,  1,  1,  1, -1],
  [ 1,  1, -1, -1,  1,  1,  1, -1,  1,  1, -1,  1, -1,  1, -1,  1],
  [-1,  1,  1,  1, -1,  1,  1,  1,  1, -1, -1, -1, -1,  1,  1, -1],
  [-1,  1, -1, -1, -1,  1, -1,  1,  1,  1, -1, -1,  1, -1, -1,  1],
  [ 1, -1, -1, -1,  1,  1,  1, -1,  1,  1,  1, -1, -1, -1,  1, -1],
  [-1, -1, -1, -1, -1, -1, -1,  1, -1, -1,  1,  1,  1, -1, -1, -1],
  [ 1,  1, -1,  1,  1,  1, -1,  1, -1,  1, -1,  1,  1,  1, -1, -1],
  [ 1, -1,  1,  1,  1, -1, -1,  1, -1, -1,  1, -1, -1, -1, -1,  1],
  [ 1,  1, -1,  1,  1, -1,  1, -1, -1, -1, -1,  1,  1,  1, -1, -1],
  [ 1,  1, -1, -1, -1, -1, -1,  1, -1, -1, -1,  1,  1,  1, -1,  1],
  [-1,  1,  1,  1,  1,  1, -1, -1, -1, -1, -1,  1, -1, -1, -1, -1],
  [ 1, -1, -1, -1, -1,  1,  1,  1, -1, -1, -1,  1,  1,  1,  1,  1],
  [-1, -1, -1,  1,  1, -1,  1, -1, -1,  1,  1, -1,  1,  1, -1,  1],
  [-1, -1,  1,  1,  1, -1,  1,  1,  1,  1, -1, -1, -1,  1, -1, -1],
  [-1,  1, -1, -1, -1,  1, -1,  1, -1,  1, -1,  1,  1, -1, -1,  1],
  [-1,  1, -1,  1,  1, -1,  1,  1,  1,  1,  1, -1,  1,  1, -1, -1],
  [ 1,  1,  1, -1, -1, -1, -1,  1, -1, -1, -1,  1,  1,  1,  1,  1],
  [-1,  1, -1,  1, -1,  1,  1,  1, -1, -1,  1, -1, -1,  1,  1,  1],
  [ 1,  1,  1, -1,  1,  1, -1,  1, -1, -1,  1,  1, -1,  1, -1, -1],
  [-1,  1, -1,  1,  1, -1, -1,  1,  1, -1, -1,  1, -1,  1,  1, -1],
  [ 1, -1,  1, -1, -1,  1,  1, -1, -1,  1,  1,  1,  1, -1, -1,  1],
  [ 1,  1,  1, -1, -1, -1,  1,  1, -1, -1,  1, -1,  1,  1, -1, -1],
  [ 1,  1,  1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,  1, -1],
  [ 1,  1, -1,  1, -1, -1,  1,  1,  1, -1, -1,  1,  1,  1,  1,  1],
  [-1, -1, -1, -1, -1,  1,  1,  1, -1,  1, -1,  1,  1, -1,  1, -1],
  [-1, -1, -1,  1,  1, -1, -1,  1, -1,  1,  1, -1,  1,  1,  1,  1],
  [ 1,  1, -1,  1,  1, -1,  1, -1,  1, -1, -1,  1,  1,  1,  1, -1],
  [-1,  1,  1, -1, -1,  1,  1, -1,  1, -1, -1, -1, -1, -1,  1, -1],
  [-1, -1,  1, -1,  1,  1, -1,  1,  1, -1, -1, -1, -1, -1,  1, -1],
  [ 1, -1, -1, -1,  1,  1, -1,  1, -1,  1,  1, -1, -1,  1,  1, -1],
  [-1,  1, -1,  1,  1, -1, -1,  1, -1, -1,  1,  1, -1, -1,  1, -1],
  [-1,  1,  1,  1, -1,  1,  1, -1, -1,  1,  1,  1,  1,  1, -1, -1],
  [-1, -1,  1,  1, -1, -1,  1, -1, -1, -1,  1,  1, -1,  1,  1, -1],
  [-1,  1, -1, -1, -1, -1,  1,  1, -1, -1, -1, -1, -1,  1, -1,  1],
  [-1,  1,  1,  1,  1,  1, -1, -1, -1, -1, -1,  1, -1, -1, -1, -1],
  [ 1,  1,  1,  1,  1,  1, -1,  1, -1, -1,  1,  1, -1,  1, -1, -1],
  [ 1, -1, -1, -1, -1,  1, -1, -1,  1,  1, -1, -1, -1,  1, -1,  1],
  [-1, -1, -1,  1,  1, -1, -1,  1,  1,  1, -1, -1, -1,  1, -1, -1],
  [-1, -1,  1,  1, -1, -1, -1, -1,  1,  1, -1, -1,  1, -1,  1, -1],
  [-1, -1, -1,  1, -1, -1, -1, -1, -1,  1,  1, -1,  1, -1, -1,  1],
  [-1,  1,  1,  1,  1, -1,  1, -1,  1, -1, -1,  1, -1,  1,  1, -1],
  [-1, -1,  1,  1,  1,  1, -1, -1, -1, -1,  1,  1,  1, -1,  1,  1],
  [-1, -1,  1, -1,  1, -1, -1,  1,  1, -1, -1, -1,  1,  1,  1,  1],
  [-1,  1,  1,  1, -1,  1, -1, -1, -1,  1,  1, -1, -1,  1,  1,  1],
  [ 1, -1, -1,  1,  1, -1, -1, -1,  1,  1,  1, -1, -1,  1, -1, -1],
  [-1, -1, -1, -1,  1, -1,  1,  1, -1,  1,  1,  1,  1,  1, -1, -1],
  [-1,  1, -1, -1,  1, -1,  1, -1,  1, -1, -1,  1, -1,  1,  1, -1],
  [-1, -1,  1, -1,  1,  1,  1,  1,  1,  1,  1,  1,  1, -1,  1, -1],
  [-1,  1, -1,  1,  1,  1, -1,  1,  1, -1, -1, -1, -1,  1,  1,  1],
  [-1,  1, -1,  1,  1, -1,  1, -1, -1,  1,  1, -1,  1, -1, -1,  1],
  [ 1,  1, -1,  1, -1,  1,  1,  1, -1,  1,  1,  1,  1, -1, -1,  1],
  [-1, -1, -1, -1, -1,  1,  1, -1, -1, -1,  1,  1,  1, -1,  1, -1],
  [-1, -1,  1,  1, -1,  1, -1, -1, -1,  1,  1,  1, -1, -1,  1, -1],
  [-1,  1, -1, -1,  1, -1,  1, -1,  1,  1,  1,  1, -1, -1,  1, -1],
  [-1,  1,  1,  1,  1, -1, -1,  1,  1,  1, -1, -1, -1, -1,  1,  1],
  [ 1,  1,  1,  1, -1, -1, -1,  1,  1,  1, -1, -1,  1,  1,  1,  1],
  [-1, -1, -1,  1, -1, -1,  1, -1,  1,  1,  1, -1,  1,  1, -1, -1],
  [ 1, -1,  1, -1, -1, -1,  1, -1,  1, -1,  1, -1,  1,  1,  1, -1],
  [ 1,  1,  1, -1,  1,  1,  1,  1,  1, -1, -1, -1, -1,  1,  1,  1],
  [ 1, -1, -1, -1,  1,  1, -1, -1, -1,  1, -1, -1, -1,  1, -1,  1],
  [-1,  1,  1, -1,  1, -1, -1, -1,  1, -1, -1,  1,  1,  1,  1, -1],
  [ 1,  1,  1,  1, -1,  1, -1,  1, -1,  1, -1,  1,  1, -1,  1,  1],
  [-1, -1,  1,  1,  1,  1, -1,  1, -1, -1, -1,  1,  1, -1, -1,  1],
  [ 1,  1, -1, -1, -1,  1, -1,  1, -1, -1,  1, -1,  1, -1,  1,  1],
  [ 1,  1, -1, -1, -1, -1, -1, -1,  1, -1, -1, -1, -1,  1,  1, -1],
  [ 1,  1, -1, -1,  1,  1,  1, -1,  1, -1,  1, -1,  1,  1, -1,  1],
  [-1, -1, -1,  1, -1, -1,  1, -1, -1, -1,  1,  1,  1, -1,  1,  1],
  [ 1,  1, -1,  1,  1, -1, -1,  1,  1, -1, -1,  1,  1,  1,  1, -1],
  [ 1, -1,  1,  1,  1,  1, -1, -1, -1,  1, -1, -1, -1,  1,  1,  1],
  [-1,  1, -1,  1,  1,  1, -1,  1,  1, -1, -1, -1,  1, -1, -1, -1],
  [ 1,  1,  1, -1,  1, -1, -1, -1,  1,  1, -1,  1, -1,  1,  1,  1],
  [-1,  1, -1, -1,  1,  1, -1, -1,  1, -1,  1,  1, -1, -1,  1, -1],
  [ 1,  1,  1, -1,  1,  1, -1,  1,  1,  1, -1, -1,  1,  1, -1,  1],
  [ 1, -1, -1, -1, -1,  1,  1,  1,  1,  1, -1, -1,  1,  1,  1,  1],
  [-1,  1,  1,  1,  1, -1, -1, -1,  1, -1,  1, -1,  1,  1,  1,  1],
  [-1,  1, -1,  1, -1,  1,  1,  1,  1,  1,  1,  1,  1, -1,  1,  1],
  [ 1,  1, -1, -1,  1, -1, -1, -1, -1, -1,  1, -1,  1,  1,  1, -1],
  [ 1, -1,  1,  1, -1,  1, -1, -1,  1,  1,  1,  1, -1, -1,  1,  1],
  [ 1, -1,  1,  1, -1,  1,  1, -1, -1,  1, -1,  1, -1, -1,  1, -1],
  [-1, -1, -1,  1, -1, -1,  1,  1,  1,  1,  1,  1,  1,  1, -1,  1],
  [-1,  1, -1,  1,  1,  1,  1,  1,  1, -1, -1,  1,  1,  1, -1,  1],
  [-1, -1,  1,  1, -1,  1,  1, -1, -1, -1, -1, -1, -1,  1, -1,  1],
  [ 1, -1, -1,  1, -1, -1,  1,  1, -1, -1, -1,  1, -1, -1,  1, -1],
  [ 1, -1, -1,  1,  1, -1,  1,  1,  1, -1,  1, -1,  1, -1, -1, -1],
  [-1,  1,  1, -1, -1, -1, -1,  1,  1, -1,  1,  1,  1,  1,  1, -1],
  [-1, -1,  1,  1,  1, -1,  1, -1,  1, -1,  1,  1,  1,  1,  1,  1],
  [ 1,  1, -1, -1,  1, -1,  1, -1, -1,  1, -1,  1,  1,  1,  1, -1],
  [-1,  1, -1, -1,  1, -1,  1, -1, -1,  1, -1, -1, -1,  1,  1,  1],
  [ 1, -1,  1, -1,  1, -1, -1,  1,  1, -1, -1,  1,  1,  1, -1, -1],
  [-1,  1, -1,  1, -1, -1, -1, -1,  1, -1,  1,  1,  1,  1,  1, -1],
  [ 1, -1,  1,  1, -1, -1, -1,  1,  1, -1, -1,  1, -1,  1,  1, -1],
  [-1, -1, -1,  1, -1, -1, -1, -1,  1,  1, -1, -1,  1, -1,  1, -1],
  [ 1, -1,  1, -1,  1,  1, -1,  1,  1,  1,  1,  1, -1,  1,  1, -1],
  [-1, -1,  1,  1,  1,  1, -1, -1,  1,  1, -1,  1, -1, -1,  1,  1],
  [-1,  1,  1,  1,  1,  1, -1, -1,  1,  1,  1, -1, -1,  1, -1,  1],
  [-1,  1,  1,  1,  1,  1,  1, -1,  1,  1, -1,  1,  1, -1,  1, -1],
  [ 1,  1,  1,  1, -1, -1, -1,  1, -1, -1, -1, -1,  1, -1, -1, -1],
  [-1, -1,  1, -1, -1, -1,  1,  1,  1, -1,  1, -1, -1, -1, -1,  1],
  [ 1, -1, -1,  1, -1, -1, -1,  1,  1, -1, -1, -1, -1, -1,  1, -1],
  [-1, -1,  1, -1, -1, -1,  1,  1,  1,  1, -1, -1,  1,  1, -1,  1],
  [-1, -1,  1,  1,  1, -1,  1,  1, -1,  1,  1, -1, -1, -1, -1, -1],
  [-1,  1,  1, -1,  1,  1, -1,  1,  1, -1,  1, -1, -1, -1,  1, -1],
  [ 1,  1, -1, -1, -1,  1,  1, -1,  1, -1,  1, -1,  1, -1,  1, -1],
  [ 1, -1, -1,  1, -1, -1,  1, -1,  1, -1,  1, -1, -1,  1, -1,  1],
  [ 1,  1,  1,  1,  1, -1, -1, -1, -1, -1,  1, -1,  1, -1, -1,  1],
  [ 1,  1, -1, -1,  1, -1,  1, -1,  1, -1,  1, -1, -1, -1,  1, -1],
  [-1, -1, -1,  1, -1, -1,  1, -1, -1, -1, -1,  1, -1, -1, -1,  1],
  [-1, -1, -1,  1,  1,  1,  1,  1,  1, -1,  1, -1,  1, -1, -1,  1],
  [-1,  1,  1,  1, -1, -1,  1, -1, -1,  1,  1,  1,  1, -1, -1,  1],
  [-1, -1,  1, -1, -1,  1, -1, -1,  1, -1,  1,  1,  1,  1, -1,  1],
  [ 1, -1,  1,  1, -1, -1,  1, -1, -1, -1, -1,  1,  1,  1,  1, -1],
  [ 1,  1,  1, -1,  1, -1, -1, -1,  1,  1,  1,  1,  1,  1,  1, -1],
  [-1, -1,  1,  1, -1,  1,  1, -1, -1,  1, -1,  1, -1, -1, -1,  1],
  [ 1,  1,  1, -1, -1,  1,  1, -1,  1, -1,  1, -1,  1,  1, -1,  1],
  [ 1, -1, -1, -1,  1,  1,  1, -1,  1, -1,  1, -1, -1, -1,  1, -1],
  [ 1,  1,  1, -1,  1,  1,  1,  1,  1, -1, -1,  1,  1, -1, -1, -1],
  [-1,  1,  1, -1,  1,  1,  1,  1,  1,  1, -1, -1, -1,  1, -1, -1],
  [-1, -1,  1,  1, -1, -1,  1,  1, -1, -1,  1,  1,  1, -1, -1,  1],
  [ 1, -1,  1, -1, -1, -1, -1,  1, -1,  1, -1, -1,  1,  1, -1, -1],
  [ 1,  1,  1,  1, -1,  1, -1,  1, -1,  1, -1,  1,  1,  1, -1, -1],
  [ 1,  1,  1, -1, -1, -1,  1,  1,  1, -1, -1, -1,  1,  1,  1,  1],
  [ 1,  1, -1, -1,  1, -1,  1,  1,  1, -1,  1,  1,  1,  1, -1,  1],
  [ 1,  1,  1,  1,  1,  1,  1,  1,  1, -1,  1,  1,  1,  1,  1,  1],
  [-1,  1,  1,  1, -1,  1, -1,  1,  1, -1, -1,  1,  1, -1, -1, -1],
  [-1, -1,  1, -1,  1,  1,  1,  1,  1,  1,  1,  1, -1,  1, -1, -1],
  [-1, -1, -1,  1,  1, -1, -1, -1,  1,  1, -1, -1,  1, -1, -1, -1],
  [-1, -1,  1,  1, -1, -1, -1,  1,  1,  1, -1,  1, -1, -1, -1,  1],
  [-1, -1, -1, -1,  1,  1, -1, -1, -1,  1,  1, -1,  1, -1,  1,  1],
  [ 1, -1,  1, -1,  1,  1,  1,  1,  1, -1, -1,  1, -1,  1, -1, -1],
  [ 1, -1, -1, -1,  1, -1,  1,  1, -1,  1, -1, -1, -1,  1, -1,  1],
  [ 1,  1,  1,  1,  1, -1, -1, -1, -1, -1,  1, -1, -1,  1, -1,  1],
  [ 1,  1, -1,  1, -1,  1,  1, -1, -1, -1, -1, -1,  1, -1,  1, -1],
  [-1, -1,  1,  1,  1,  1, -1, -1,  1, -1, -1, -1, -1, -1, -1, -1],
  [-1,  1,  1,  1, -1,  1, -1, -1, -1,  1, -1, -1, -1, -1, -1, -1],
  [ 1,  1,  1,  1,  1,  1,  1, -1, -1,  1,  1, -1, -1,  1, -1,  1],
  [ 1,  1,  1,  1, -1,  1, -1, -1,  1, -1, -1, -1,  1,  1,  1,  1],
  [ 1, -1,  1,  1, -1,  1,  1,  1, -1, -1, -1, -1, -1, -1,  1, -1],
  [-1, -1,  1, -1,  1, -1,  1,  1, -1, -1,  1, -1,  1,  1,  1, -1],
  [-1,  1,  1, -1,  1,  1, -1,  1, -1, -1,  1, -1, -1,  1,  1, -1],
  [-1, -1, -1, -1, -1,  1,  1, -1, -1, -1,  1,  1,  1,  1, -1,  1],
  [ 1, -1,  1,  1,  1, -1, -1, -1,  1,  1,  1, -1, -1, -1, -1, -1],
  [ 1, -1,  1,  1,  1, -1, -1, -1,  1, -1, -1,  1, -1, -1,  1,  1],
  [ 1,  1, -1, -1, -1, -1,  1, -1, -1,  1, -1,  1, -1,  1, -1,  1],
  [ 1, -1, -1,  1, -1, -1,  1,  1,  1, -1,  1,  1,  1,  1,  1,  1],
  [ 1,  1,  1,  1,  1,  1,  1,  1, -1, -1,  1, -1, -1, -1,  1,  1],
  [ 1,  1, -1,  1, -1, -1, -1,  1,  1, -1, -1, -1, -1, -1,  1,  1],
  [-1, -1, -1,  1,  1,  1,  1,  1, -1, -1, -1, -1,  1,  1,  1, -1],
  [-1, -1,  1, -1, -1, -1,  1, -1,  1,  1,  1,  1,  1, -1,  1, -1],
  [ 1,  1, -1,  1, -1, -1, -1,  1,  1, -1, -1,  1,  1, -1, -1, -1],
  [-1,  1,  1,  1, -1, -1,  1,  1,  1, -1, -1,  1,  1, -1,  1,  1],
  [ 1, -1, -1,  1,  1,  1, -1, -1, -1,  1,  1,  1, -1, -1,  1, -1],
  [ 1,  1,  1,  1, -1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1],
  [ 1, -1, -1,  1,  1,  1, -1,  1, -1,  1,  1,  1, -1, -1,  1, -1],
  [-1, -1,  1,  1,  1, -1,  1,  1,  1,  1, -1,  1,  1,  1, -1, -1],
  [-1, -1,  1, -1,  1,  1, -1,  1,  1, -1, -1,  1, -1, -1,  1, -1],
  [-1, -1, -1,  1, -1,  1,  1,  1, -1, -1,  1, -1, -1, -1, -1, -1],
  [-1, -1, -1, -1, -1, -1,  1,  1, -1, -1, -1,  1, -1, -1,  1, -1],
  [-1, -1, -1, -1,  1, -1, -1, -1, -1, -1,  1,  1,  1, -1,  1,  1],
  [-1,  1, -1,  1, -1, -1,  1,  1,  1,  1,  1, -1,  1,  1, -1,  1],
  [-1, -1, -1,  1,  1,  1,  1,  1,  1, -1, -1,  1,  1,  1, -1, -1],
  [ 1, -1, -1, -1,  1, -1,  1, -1,  1,  1, -1,  1, -1,  1,  1,  1],
  [ 1,  1,  1, -1, -1, -1,  1, -1, -1, -1, -1,  1,  1,  1, -1,  1],
  [ 1,  1, -1, -1, -1,  1,  1, -1, -1,  1, -1,  1, -1, -1, -1, -1],
  [ 1, -1, -1,  1, -1, -1, -1, -1, -1, -1,  1, -1,  1,  1, -1, -1],
  [-1,  1, -1,  1,  1,  1,  1, -1, -1,  1, -1, -1,  1, -1,  1,  1],
  [-1, -1,  1,  1, -1,  1, -1, -1,  1, -1, -1,  1, -1, -1, -1, -1],
  [ 1,  1,  1,  1,  1,  1, -1, -1,  1, -1,  1,  1, -1, -1,  1,  1],
  [ 1,  1,  1,  1, -1,  1, -1,  1, -1, -1,  1, -1,  1, -1,  1, -1],
  [ 1, -1,  1, -1,  1, -1, -1,  1,  1, -1,  1, -1,  1,  1,  1, -1],
  [-1,  1,  1, -1, -1,  1, -1, -1, -1,  1, -1, -1,  1,  1,  1,  1],
  [ 1,  1, -1,  1,  1, -1, -1,  1,  1,  1,  1,  1, -1, -1, -1,  1],
  [-1, -1,  1,  1, -1,  1,  1,  1,  1,  1, -1, -1,  1,  1, -1,  1],
  [-1,  1, -1,  1,  1, -1, -1, -1, -1, -1, -1, -1,  1,  1, -1,  1],
  [-1, -1, -1,  1,  1,  1,  1,  1, -1,  1, -1, -1, -1,  1,  1,  1],
  [-1, -1,  1,  1,  1, -1, -1,  1, -1, -1,  1,  1, -1, -1,  1, -1],
  [-1,  1,  1, -1,  1,  1, -1,  1, -1,  1, -1,  1, -1,  1, -1,  1],
  [ 1, -1,  1,  1,  1,  1, -1, -1,  1, -1,  1,  1,  1, -1, -1, -1],
  [ 1,  1, -1, -1, -1, -1, -1,  1, -1, -1,  1, -1,  1, -1, -1, -1],
  [-1, -1,  1, -1, -1,  1,  1,  1,  1, -1, -1, -1,  1, -1, -1,  1],
  [ 1,  1,  1,  1, -1,  1,  1, -1, -1,  1, -1, -1,  1, -1,  1, -1],
  [ 1,  1, -1,  1,  1, -1,  1, -1,  1, -1,  1,  1, -1, -1,  1,  1],
  [-1,  1, -1, -1, -1,  1,  1,  1,  1, -1, -1, -1, -1, -1,  1, -1],
  [ 1,  1,  1,  1,  1, -1, -1,  1,  1, -1,  1,  1, -1,  1, -1, -1],
  [ 1,  1, -1, -1,  1, -1,  1,  1,  1, -1, -1, -1, -1, -1,  1,  1],
  [ 1,  1, -1, -1, -1,  1, -1,  1,  1, -1, -1,  1,  1,  1, -1,  1],
  [-1,  1,  1, -1,  1,  1, -1,  1, -1,  1,  1,  1,  1, -1,  1,  1],
  [-1, -1,  1, -1, -1, -1, -1,  1,  1,  1, -1, -1,  1, -1, -1, -1],
  [ 1, -1, -1, -1,  1,  1,  1,  1, -1,  1,  1,  1,  1,  1, -1, -1],
  [ 1, -1, -1, -1, -1, -1,  1,  1, -1,  1, -1, -1,  1,  1, -1,  1],
  [ 1,  1,  1, -1, -1,  1,  1, -1,  1,  1,  1,  1, -1, -1, -1, -1],
  [ 1, -1, -1, -1, -1,  1,  1,  1,  1, -1, -1, -1, -1, -1, -1, -1],
  [ 1, -1, -1,  1, -1, -1, -1, -1, -1, -1,  1, -1, -1, -1,  1,  1],
  [ 1,  1, -1, -1,  1, -1, -1,  1, -1,  1, -1, -1,  1, -1,  1,  1],
  [ 1, -1, -1,  1, -1,  1,  1, -1,  1,  1, -1,  1, -1,  1, -1,  1],
  [-1, -1,  1,  1,  1,  1, -1, -1,  1, -1, -1, -1, -1, -1, -1,  1],
  [-1, -1, -1,  1, -1,  1,  1,  1,  1, -1,  1, -1,  1,  1,  1, -1],
  [-1,  1,  1, -1, -1, -1,  1,  1,  1,  1,  1, -1,  1,  1,  1,  1],
  [-1,  1,  1,  1, -1,  1,  1,  1, -1, -1, -1, -1,  1,  1, -1, -1],
  [ 1, -1, -1, -1,  1,  1,  1, -1, -1,  1, -1, -1, -1, -1, -1,  1],
  [ 1, -1, -1, -1,  1,  1,  1, -1, -1,  1,  1, -1, -1,  1, -1, -1],
  [-1, -1, -1, -1,  1, -1, -1,  1,  1, -1, -1, -1,  1,  1,  1,  1],
  [-1, -1, -1, -1, -1,  1,  1, -1, -1,  1, -1, -1,  1,  1, -1, -1]] )
