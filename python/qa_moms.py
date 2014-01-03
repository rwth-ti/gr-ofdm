#!/usr/bin/env python

from gnuradio import gr, gr_unittest
from moms import moms
import ofdm.ofdm_swig as ofdm

class qa_scf (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ("test_block")

    def tearDown (self):
        self.tb = None 

    def std_test (self, src_data, soff, expected):
        src = gr.vector_source_c (src_data,False,1)
        interp = moms(2,1)
        dst = gr.vector_sink_c (1)
        self.tb.connect (src, interp)
        self.tb.connect (interp, dst)
        self.tb.run ()
        result_data = dst.data ()
        print result_data
        self.assertEqual(expected, result_data)

    def test_001_moms (self):
        soff = 1
        src_vec = range(1,10)
        expected = (0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0)
        self.std_test (src_vec, soff, expected)

if __name__ == '__main__':
    gr_unittest.main ()


