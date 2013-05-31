#!/usr/bin/env python

from gnuradio import gr, gr_unittest
import sys
sys.path.append('../')
from ofdm_swig import vector_element

class qa_scf (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ("test_block")

    def tearDown (self):
        self.tb = None 

    def std_test (self, vlen, src_data, element, expected):
        src = gr.vector_source_c (src_data,False,vlen)
        elem = vector_element(vlen,element)
        dst = gr.vector_sink_c (1)
        self.tb.connect (src, elem)
        self.tb.connect (elem, dst)
        self.tb.run ()
        result_data = dst.data ()
        print result_data
        self.assertEqual(expected, result_data)
             
    def test_001_scf (self):
        vlen = 4
        element = 1
        src_vec = (1+1j, 1, 0, -1, 17, 2, 3, 4)
        expected = (1+1j, 17)
        self.std_test (vlen, src_vec, element, expected)
        
    def test_002_scf (self):
        vlen = 5
        element = 4
        src_vec = (1, 2, 3, 4, 5, 6, 7, 8, 9-2j, 10, 11, 12, 13, 14, 15)
        expected = (4, 9-2j, 14)
        self.std_test (vlen, src_vec, element, expected)

if __name__ == '__main__':
    gr_unittest.main ()


