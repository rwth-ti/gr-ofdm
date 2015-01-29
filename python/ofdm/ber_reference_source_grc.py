from gnuradio import gr
from ofdm import reference_data_source_02_ib
from random import seed,randint, getrandbits

class ber_reference_source_grc (gr.hier_block2):
  """
  Provide bit stream to measure BER at receiver.
  Input is the bitcount per frame. Outputs the exact number of bits for
  the each frame.
  """
  def __init__(self,subcarriers, data_blocks):
    gr.hier_block2.__init__(self, "ber_reference_source_grc",
      gr.io_signature2(2,2,gr.sizeof_short,
                       gr.sizeof_int),
      gr.io_signature(1,1,gr.sizeof_char))

    ## ID Source
    id_src = (self,0)
    ## Bitcount Source
    bc_src = (self,1)

    ## Reference Data Source
#    rand_file = file('random.dat','rb')
#    rand_string = rand_file.read()
#    rand_file.close()
#    rand_data = [ord(rand_string[i]) for i in range(len(rand_string))]
    # We have to use a fix seed so that Tx and Rx have the same random sequence in order to calculate BER
    seed(30214345)
    # Maximum bitloading is 8 and maximum ID is 256
    print "Generating random bits..."
    rand_data = [chr(getrandbits(1)) for x in range(subcarriers*8*data_blocks*256)]

    ref_src = self._reference_data_source = reference_data_source_02_ib(rand_data)
    self.connect(id_src,(ref_src,0))
    self.connect(bc_src,(ref_src,1))

    ## Setup Output
    self.connect(ref_src,self)