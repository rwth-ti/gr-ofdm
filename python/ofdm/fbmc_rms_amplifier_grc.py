from gnuradio import gr, blocks
from ofdm import multiply_const_ccf
import math

class fbmc_rms_amplifier( gr.hier_block2 ):
  def __init__(self,amplitude,subcarriers):
    #config = station_configuration()

    total_subc = subcarriers
    vlen = total_subc

    gr.hier_block2.__init__(self,"fbmc_rms_amplifier_grc",
      gr.io_signature(1,1,gr.sizeof_gr_complex),
      gr.io_signature(1,1,gr.sizeof_gr_complex))
    
    amp = self._amplifier = multiply_const_ccf(1.0)
    self._subcarriers = subcarriers
    self.connect(self,amp,self)
    self.set_rms_amplitude(amplitude)

  def set_rms_amplitude(self, ampl):
        """
        Sets the rms amplitude sent to the USRP
        @param: ampl 0 <= ampl < 32768
        """
        # The standard output amplitude depends on the subcarrier number. E.g.
        # if non amplified, the amplitude is sqrt(subcarriers).
    
        self.rms = max(0.0, min(ampl, 1.0))
        scaled_ampl = ampl/math.sqrt(self._subcarriers*0.6863)
        self._amplification = scaled_ampl
        self._amplifier.set_k(self._amplification)

    # The next block ensures that only complete frames find their way into
    # the old outer receiver. The dynamic frame start trigger is hence
    # replaced with a static one, fixed to the frame length.