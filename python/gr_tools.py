#!/usr/bin/env python

from gnuradio import gr
from numpy import concatenate, array, complex, sum
import ofdm

from delaylines import *

def ifft(subcarrier_data, virtual_subcarriers=0):
  if virtual_subcarriers > 0:
    vec = concatenate([[0.0]*virtual_subcarriers,subcarrier_data,[0.0]*virtual_subcarriers])
  else:
    vec = subcarrier_data

  data = array(vec, complex)
  src = gr.vector_source_c(data, False)
  dst = gr.vector_sink_c()

  s2v = gr.stream_to_vector(gr.sizeof_gr_complex, len(data))
  v2s = gr.vector_to_stream(gr.sizeof_gr_complex, len(data))

  # inverse, no window, blockshift on
  ifft = gr.fft_vcc(len(data), False, [], True)

  fg = gr.top_block()
  fg.connect(src, s2v, ifft, v2s, dst)
  fg.run()

  fft_data = dst.data()
  return fft_data


def fft(data,virtual_subcarriers=0):
  data = array(data, complex)
  src = gr.vector_source_c(data, False)
  dst = gr.vector_sink_c()

  s2v = gr.stream_to_vector(gr.sizeof_gr_complex, len(data))
  v2s = gr.vector_to_stream(gr.sizeof_gr_complex, len(data))

  # inverse, no window, blockshift on
  fft = gr.fft_vcc(len(data), True, [], True)

  fg = gr.top_block()
  fg.connect(src, s2v, fft, v2s, dst)
  fg.run()

  fft_data = dst.data()

  if virtual_subcarriers > 0:
    fft_data = fft_data[virtual_subcarriers:len(fft_data)-virtual_subcarriers]

  return fft_data

"""
  bits_per_channel: vector indicating bits per ofdm symbol for each subcarrier
  data: 0/1 byte data. 1 bit per byte used!
"""
def ofdm_mapper(bits_per_channel, bitdata):
  bits = sum(bits_per_channel)
  vlen = len(bits_per_channel)
  ofdm_blocks = len( bitdata ) / bits
  
  assert( ( len( bitdata ) % bits ) == 0 )

  cv_src = gr.vector_source_b(bits_per_channel,True,vlen)
  data_src = gr.vector_source_b(bitdata)
  trigger = [0]*ofdm_blocks
  trigger[0] = 1
  trigger = gr.vector_source_b( trigger )
  mapper = ofdm.generic_mapper_bcv(vlen)
  v2s = gr.vector_to_stream(gr.sizeof_gr_complex,vlen)
  dst = gr.vector_sink_c()

  fg = gr.top_block()

  fg.connect(data_src, (mapper,0))
  fg.connect(cv_src,(mapper,1))
  fg.connect( trigger, ( mapper, 2 ) )
  fg.connect(mapper,v2s,dst)
  fg.run()

  ofdm_symbol = dst.data()
  return ofdm_symbol

"""
 returns new array with one bit per byte
 use gr_blocks to make sure that transformation is always identical
"""
def unpack_array(arr):
  src = gr.vector_source_b(arr)
  data_p2u = gr.packed_to_unpacked_bb(1, gr.GR_LSB_FIRST)
  dst = gr.vector_sink_b()
  fg = gr.top_block()
  fg.connect(src, data_p2u,dst)
  fg.run()
  unpacked_array = dst.data()
  assert(len(unpacked_array) == 8*len(arr))
  return unpacked_array

"""
Determine streamsize from output signature
"""
def determine_streamsize(block):
  if hasattr(block, "__getitem__") and len(block) == 2:
    streamsize = block[0].output_signature().sizeof_stream_item(block[1])
  else:
    streamsize = block.output_signature().sizeof_stream_item(0)
  return streamsize

"""
Log stream to file.
"""
def log_to_file(hb,block,filename,mag=False,char_to_float=False):
  streamsize = determine_streamsize(block)
  
  if mag:
    vlen = streamsize/gr.sizeof_gr_complex
    gr_mag = gr.complex_to_mag(vlen)
    hb.connect( block, gr_mag )
    log_to_file( hb, gr_mag, filename )
  elif char_to_float:
    vlen = streamsize/gr.sizeof_char
    ctf = gr.char_to_float( vlen )
    hb.connect( block, ctf )
    log_to_file( hb, ctf, filename )
  else:
    file_log = gr.file_sink(streamsize,filename)
    hb.connect(block,file_log)
    
class char_to_float_stream ( gr.hier_block2 ):
  def __init__( self, block ):
    vlen = determine_streamsize( block )
    gr.hier_block2.__init__( self,
        "char_to_float_stream",
        gr.io_signature(0,0,0),
        gr.io_signature( 1, 1, gr.sizeof_float * vlen ) )
    
  
    cvt = gr.char_to_float( vlen )
    self.connect( block, cvt, self )
    
    
def terminate_stream(hb,block):
  streamsize = determine_streamsize(block)
  hb.connect(block, gr.null_sink(streamsize))

"""
Calculate mean square of stream, save to file.
Input should be gr_complex!
"""
def ms_to_file(hb,block,filename,N=4096,delay=0,fft=False,scale=1):
  streamsize = determine_streamsize(block)
  vlen = streamsize/gr.sizeof_gr_complex

  blks = [block]

  if fft and vlen > 1:
    gr_fft = gr.fft_vcc(vlen,True,[],True)
    blks.append(gr_fft)

  mag_sqrd = gr.complex_to_mag_squared(vlen)
  blks.append(mag_sqrd)

  if vlen > 1:
    v2s = gr.vector_to_stream(gr.sizeof_float,vlen)
    blks.append(v2s)

  if delay != 0:
    delayline = delayline_ff(delay)
    blks.append(delayline)

  gr_scale = gr.multiply_const_ff(scale)
  blks.append(gr_scale)

  filter = gr.fir_filter_fff(1,[1.0/N]*N)
  blks.append(filter)

  for i in range(len(blks)-1):
    hb.connect(blks[i],blks[i+1])

  log_to_file(hb,filter,filename)
