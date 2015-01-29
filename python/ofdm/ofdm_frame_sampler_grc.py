from gnuradio import gr, blocks
from ofdm import vector_sampler

class ofdm_frame_sampler( gr.hier_block2 ):
  def __init__(self,subcarriers, frame_length):
    #config = station_configuration()

    total_subc = subcarriers
    vlen = total_subc

    gr.hier_block2.__init__(self,"ofdm_frame_sampler_grc",
      gr.io_signature2(2,2,gr.sizeof_gr_complex*vlen,
                       gr.sizeof_char),
      gr.io_signature2(2,2,gr.sizeof_gr_complex*vlen,
                 gr.sizeof_char))


    ft = [0] * frame_length
    ft[0] = 1

    # The next block ensures that only complete frames find their way into
    # the old outer receiver. The dynamic frame start trigger is hence
    # replaced with a static one, fixed to the frame length.

    frame_sampler = vector_sampler( gr.sizeof_gr_complex * total_subc,
                                              frame_length )
    symbol_output = blocks.vector_to_stream( gr.sizeof_gr_complex * total_subc,
                                              frame_length )
    delayed_frame_start = blocks.delay( gr.sizeof_char, frame_length - 1 )
    damn_static_frame_trigger = blocks.vector_source_b( ft, True )

    self.connect( self, frame_sampler, symbol_output, self )

    self.connect( (self,1), delayed_frame_start, ( frame_sampler, 1 ) )

    self.connect( damn_static_frame_trigger, (self,1) )