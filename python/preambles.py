#!/usr/bin/env python

from math import sqrt, pi
from numpy import concatenate,conjugate,array
from gr_tools import fft,ifft
from gnuradio import gr
from cmath import exp
from numpy import abs,concatenate
import numpy, ofdm
from station_configuration import *
from ofdm import stream_controlled_mux,skip

from ofdm import static_mux_c, static_mux_v

class default_block_header (object):
  def __init__(self,data_subcarriers,fft_length,options):
    self.no_preambles = 2
    self.no_pilotsyms = self.no_preambles
    self.pilotsym_td = []
    self.pilotsym_fd = []
    self.pilotsym_pos = []
    self.pilot_tones = []
    self.pilot_tone_map = []

    self._prepare_pilot_subcarriers(data_subcarriers, fft_length)

    # symbol position inside ofdm block!
    self.mm_preamble_pos = self.sc_preamble_pos = 0 # restricted to 0!
    self.channel_estimation_pilot = [1] # TODO: remove when interpolating channel estimator available
    

    # Morelli & Mengali + Schmidl & Cox Preamble
    self.mm_periodic_parts = L = 8
    td,fd = morellimengali_designer.create(self.subcarriers, fft_length, L)
    

    assert(len(td) == fft_length)
    assert(len(fd) == self.subcarriers)

    self.pilotsym_td.append(td)
    self.pilotsym_fd.append(fd)
    self.pilotsym_pos.append(0)


    # Known pilot block to ease estimation of CTF
    td,fd = schmidl_ifo_designer.create(self.subcarriers, fft_length)

    assert(len(td) == fft_length)
    assert(len(fd) == self.subcarriers)

    self.pilotsym_td.append(td)
    self.pilotsym_fd.append(fd)
    self.pilotsym_pos.append(1)


    assert(self.no_pilotsyms == len(self.pilotsym_fd))
    assert(self.no_pilotsyms == len(self.pilotsym_td))
    assert(self.no_pilotsyms == len(self.pilotsym_pos))


  def _prepare_pilot_subcarriers(self,data_subcarriers,fft_length):
    # FIXME make this parameterisable
    # FIXME pilot subcarriers fixed to 1.0
    self.pilot_subcarriers = 8
    self.subcarriers = subc = self.pilot_subcarriers+data_subcarriers
    self.pilot_subc_sym = [2.0 , -2.0j, -2.0 , 2.0j, 2.0 , -2.0j, -2.0 , 2.0j]
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
    #assert( ( numpy.abs( t.imag ) < 1e-6 ).all() )
    

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
    pass

  # Make a static method to call before instantiation
  add_options = staticmethod(add_options)

################################################################################

# time domain
class pilot_block_inserter(gr.hier_block2):
  """
  Multiplex pilot blocks to time domain signal.
  """
  def __init__ (self, add_cyclic_prefix = False):

    config = station_configuration()
    fft_length = config.fft_length
    block_length = config.block_length
    cp_length = config.cp_length
    
    if add_cyclic_prefix:
      vlen = block_length
    else:
      vlen = fft_length

    gr.hier_block2.__init__(self, "pilot_block_inserter",
        gr.io_signature(1,1,gr.sizeof_gr_complex*vlen),
        gr.io_signature(1,1,gr.sizeof_gr_complex*vlen))

    mux = ofdm.frame_mux( vlen, config.frame_length )
    for x in range( config.training_data.no_pilotsyms ):
      mux.add_preamble( config.training_data.pilotsym_td[ x ] )

    self.connect( self, mux, self )
    return



    #data_stream_port = 0
    #pilot block ports = 1 .. x

    # compute multiplexing scheme for frame, create one src per pilot block
    pilot_block_src = []
    mux_stream = [0]*config.frame_length
    for x in range(config.training_data.no_pilotsyms):
      mux_stream[config.training_data.pilotsym_pos[x]] = x+1
      
      sym = config.training_data.pilotsym_td[x]
      if add_cyclic_prefix:
        sym = concatenate( [ sym[len(sym)-cp_length:len(sym)], sym ] )
        
      pilot_block_src.append( gr.vector_source_c( sym, True, vlen ) )
      
    print "pilot block inserter, mux stream length", len(mux_stream)
    
    imux = []
    for x in mux_stream:
      imux.append(int(x))
    
#    mux_ctrl = gr.vector_source_s(mux_stream,True) #i.e. static
#    mux = stream_controlled_mux(gr.sizeof_gr_complex*fft_length)
    mux = static_mux_v(gr.sizeof_gr_complex*vlen, imux)

#    self.connect(mux_ctrl,mux)
    self.connect(self,(mux,0)) # data stream
    i = 1
    for x in pilot_block_src:
      self.connect(x,(mux,i))
      i = i + 1

    self.connect(mux,self)

################################################################################

class pilot_block_filter(gr.hier_block2):
  """
  Remove pilot blocks from ofdm block stream. Frequency domain operation.

  Input 0: ofdm frames
  Input 1: frame trigger
  Output 0: data blocks
  Output 1: frame trigger for data blocks
  """
  def __init__ (self):

    config = station_configuration()
    subcarriers = config.subcarriers
    frame_length = config.frame_length

    gr.hier_block2.__init__(self, "pilot_block_filter",
        gr.io_signature2(2,2,gr.sizeof_gr_complex*subcarriers,gr.sizeof_char),
        gr.io_signature2(2,2,gr.sizeof_gr_complex*subcarriers,gr.sizeof_char))

    filt = skip(gr.sizeof_gr_complex*subcarriers,frame_length)# skip_known_symbols(frame_length,subcarriers)
    for x in config.training_data.pilotsym_pos:
      filt.skip(x)

    self.connect(self,filt)
    self.connect(filt,self)
    self.connect((self,1),(filt,1),(self,1))


################################################################################

class pilot_subcarrier_inserter (gr.hier_block2):
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

    gr.hier_block2.__init__(self,"pilot_subcarrier_inserter",
        gr.io_signature(1,1,gr.sizeof_gr_complex*subc),
        gr.io_signature(1,1,gr.sizeof_gr_complex*total_subc))
    
    ins = ofdm.pilot_subcarrier_inserter( subc,
        config.training_data.pilot_subc_sym,
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
      

    
    v2s = gr.vector_to_stream(gr.sizeof_gr_complex,subc)
    pilot_src = gr.vector_source_c(config.training_data.pilot_subc_sym,True)

    mux = static_mux_c(imux)
    s2v = gr.stream_to_vector(gr.sizeof_gr_complex,total_subc)

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
  def __init__(self, complex_value=True):

    config = station_configuration()
    data_subc = config.data_subcarriers
    subc = config.subcarriers

    if complex_value:
      itemsize = gr.sizeof_gr_complex
    else:
      itemsize = gr.sizeof_float

    gr.hier_block2.__init__(self,"pilot_subcarrier_filter",
        gr.io_signature(1,1,itemsize*subc),
        gr.io_signature(1,1,itemsize*data_subc))

    # FIXME inefficient

    skipcarrier = skip(itemsize,subc)
    for x in config.training_data.shifted_pilot_tones:
      skipcarrier.skip(x)

    trigger = [0]*subc
    trigger[0] = 1
    trigger_src = gr.vector_source_b(trigger,True) # FIXME static

    v2s = gr.vector_to_stream(itemsize,subc)
    s2v = gr.stream_to_vector(itemsize,data_subc)

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
    

    # transform to time domain
    td = ifft(seq1, (fft_length-subcarriers)/2)
    fd = seq1

    return (td,fd)

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
