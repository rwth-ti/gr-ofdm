from gnuradio import gr
import ofdm_swig as ofdm

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
