#!/usr/bin/env python

from gnuradio import gr
from optparse import OptionParser
import ofdm_swig as ofdm
import math

def add_options(normal,expert):
  normal.add_option("", "--fft-length",
    type="int", default=None,
    help="fft-length")
  normal.add_option("-f", "--file",
    type="string", default=None,
    help="input file")
  normal.add_option("-o", "--out",
    type="string", default=None,
    help="output file")


def main():
  parser = OptionParser(conflict_handler="resolve")
  expert_grp = parser.add_option_group("Expert")
  add_options(parser, expert_grp)
  (options, args) = parser.parse_args ()

  fft_length = options.fft_length or 512
  file = options.file or "input.compl"
  out = options.out or "output.compl"

  src = gr.file_source(gr.sizeof_gr_complex,file)
  sampler = ofdm.vector_sampler( gr.sizeof_gr_complex, fft_length )
  trig = gr.vector_source_b([1],True)

  fft = gr.fft_vcc( fft_length, True, [], True )
  mag = gr.complex_to_mag( fft_length )
  avg = gr.single_pole_iir_filter_ff(0.01, fft_length)
  nlog = gr.nlog10_ff( 20, fft_length, -10*math.log10(fft_length) )
  dst = gr.file_sink( gr.sizeof_float * fft_length, out )

  fg = gr.top_block()
  fg.connect( src, sampler, fft, mag, avg, nlog, dst )
  fg.connect( trig, (sampler,1))
#  fg.connect(src,limit,
#             gr.stream_to_vector(gr.sizeof_gr_complex,fft_length),
#             fft,
#             gr.multiply_const_vcc([1./fft_length]*fft_length),
#             gr.complex_to_mag(fft_length),
#             gr.nlog10_ff(10.0,fft_length),
#             dst)
#  fg.connect( src, fft, dst )

  fg.run()
  print "done"



if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    pass
