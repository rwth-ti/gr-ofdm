from gnuradio import gr, blocks
from ofdm import vector_sampler

class fbmc_frame_sampler( gr.hier_block2 ):
  def __init__(self,total_subcarriers, frame_length, frame_data_part, training_data):
    #config = station_configuration()

    total_subc = total_subcarriers
    vlen = total_subc

    gr.hier_block2.__init__(self,"fbmc_frame_sampler_grc",
      gr.io_signature2(2,2,gr.sizeof_gr_complex*vlen,
                       gr.sizeof_char),
      gr.io_signature2(2,2,gr.sizeof_gr_complex*vlen,
                 gr.sizeof_char))

    frame_size = frame_data_part + training_data.fbmc_no_preambles/2
    print "frame_size: ", frame_size
    ft = [0] * frame_size
    ft[0] = 1

    # The next block ensures that only complete frames find their way into
    # the old outer receiver. The dynamic frame start trigger is hence
    # replaced with a static one, fixed to the frame length.

    frame_sampler = vector_sampler( gr.sizeof_gr_complex * total_subc,
                                              frame_size )
    symbol_output = blocks.vector_to_stream( gr.sizeof_gr_complex * total_subc,
                                              frame_size )
    #delayed_frame_start = blocks.delay( gr.sizeof_char, config.frame_length-1  - config.training_data.fbmc_no_preambles/2 )
    delayed_frame_start = blocks.delay( gr.sizeof_char, frame_length/2-1)

    damn_static_frame_trigger = blocks.vector_source_b( ft, True )
    
    #oqam_postpro = ofdm.fbmc_oqam_postprocessing_vcvc(total_subc,0,0)

    self.connect( self, frame_sampler, symbol_output ,self)

    #self.connect( (self,1), blocks.keep_m_in_n(gr.sizeof_char,frame_data_part + training_data.fbmc_no_preambles/2,2*frame_data_part + training_data.fbmc_no_preambles,0),delayed_frame_start, ( frame_sampler, 1 ) )
    self.connect( (self,1),delayed_frame_start, ( frame_sampler, 1 ) )

    #self.connect( self, blocks.multiply_const_vcc(([1.0]*total_subc)) ,self)
    #terminate_stream(self,frame_sampler)

    self.connect( damn_static_frame_trigger, (self,1) )