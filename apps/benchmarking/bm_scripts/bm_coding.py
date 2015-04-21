#!/usr/bin/env python

from gnuradio import gr, blocks, digital, analog, trellis
import random, numpy
from random import randint
from ofdm import generic_mapper_bcv, puncture_bb
import os

class bm_coding:
    '''
    @title: Benchmark PSK modulators
    '''
    
    def __init__(self, N):
        self.N = N
        

        # Generate some random bits
        rndm = random.Random()
        rndm.seed(0)
        self.coding = 1
        self.interleave = 0
        self.fo=trellis.fsm(1,2,[91,121]) 
        


    def setup_test07(self):
        print "... benchmarking BPSK + 1/2 mapper"
        self.mode = 1
        bitspermode= [0.5,1,1.5,2,3,4,4.5,5,6]
        self.nobits = (bitspermode[self.mode-1])
        self.data_subcarriers = 200
        
        
        self.blks = self.N*(int(10*self.nobits) +1)
        self.tb = gr.top_block()
        
        self.encoder = self._encoder = trellis.encoder_bb(self.fo,0)
        self.unpack = self._unpack = blocks.unpack_k_bits_bb(2)
        self.puncturing = puncture_bb(self.data_subcarriers)
        bmaptrig_stream_puncturing = [1]+[0]*(10/2-1)
        self.bitmap_trigger_puncturing = blocks.vector_source_b(bmaptrig_stream_puncturing, True)
        if self.interleave:
            int_object=trellis.interleaver(2000,666)
            self.interlv = trellis.permutation(int_object.K(),int_object.INTER(),1,gr.sizeof_char)
        #self.bitmap = [self.nobits]*self.data_subcarriers
        self.bitmap = [self.mode]*self.data_subcarriers + [self.mode]*self.data_subcarriers         
        #self.bmaptrig_stream = [1, 1]+[0]*(11-2)
    
        self.bitdata = [randint(0,1) for i in range(self.blks*self.data_subcarriers)]
        #self.data = numpy.array(self.bitdata)*(-2)+1
        
        self.src = blocks.vector_source_b(self.bitdata)
        self.bitmap_src = blocks.vector_source_b(self.bitmap,True, self.data_subcarriers)
        #self.bitmap_trigger = blocks.vector_source_b(self.bmaptrig_stream, True)
        self.modulator = generic_mapper_bcv(self.data_subcarriers,self.coding,10)
        self.snk = blocks.null_sink(gr.sizeof_gr_complex*self.data_subcarriers)
        
        
        #Connect blocks
        self.tb.connect(self.src,self.encoder,self.unpack,self.puncturing)
        if self.interleave:
            self.tb.connect(self.puncturing,self.interlv, self.modulator, self.snk)
        else:
            self.tb.connect(self.puncturing, self.modulator, self.snk)
        self.tb.connect(self.bitmap_src, (self.modulator,1))
        self.tb.connect(self.bitmap_src, (self.puncturing,1))
        self.tb.connect(self.bitmap_trigger_puncturing, (self.puncturing,2))
        #self.tb.connect(self.bitmap_trigger, (self.modulator,2))

    def run_test07(self):
        self.src.rewind()
        self.tb.run()
        
    def setup_test06(self):
        print "... benchmarking QPSK + 1/2 mapper"
        self.mode = 2
        bitspermode= [0.5,1,1.5,2,3,4,4.5,5,6]
        self.nobits = (bitspermode[self.mode-1])
        self.data_subcarriers = 200
         
         
        self.blks = self.N*(int(10*self.nobits) +1)
        self.tb = gr.top_block()
         
        self.encoder = self._encoder = trellis.encoder_bb(self.fo,0)
        self.unpack = self._unpack = blocks.unpack_k_bits_bb(2)
        self.puncturing = puncture_bb(self.data_subcarriers)
        bmaptrig_stream_puncturing = [1]+[0]*(10/2-1)
        self.bitmap_trigger_puncturing = blocks.vector_source_b(bmaptrig_stream_puncturing, True)
        if self.interleave:
            int_object=trellis.interleaver(2000,666)
            self.interlv = trellis.permutation(int_object.K(),int_object.INTER(),1,gr.sizeof_char)
        #self.bitmap = [self.nobits]*self.data_subcarriers
        self.bitmap = [self.mode]*self.data_subcarriers + [self.mode]*self.data_subcarriers         
        #self.bmaptrig_stream = [1, 1]+[0]*(11-2)
     
        self.bitdata = [randint(0,1) for i in range(self.blks*self.data_subcarriers)]
        #self.data = numpy.array(self.bitdata)*(-2)+1
         
        self.src = blocks.vector_source_b(self.bitdata)
        self.bitmap_src = blocks.vector_source_b(self.bitmap,True, self.data_subcarriers)
        #self.bitmap_trigger = blocks.vector_source_b(self.bmaptrig_stream, True)
        self.modulator = generic_mapper_bcv(self.data_subcarriers,self.coding,10)
        self.snk = blocks.null_sink(gr.sizeof_gr_complex*self.data_subcarriers)
         
         
        #Connect blocks
        self.tb.connect(self.src,self.encoder,self.unpack,self.puncturing)#, self.modulator, self.snk)
        if self.interleave:
            self.tb.connect(self.puncturing,self.interlv, self.modulator, self.snk)
        else:
            self.tb.connect(self.puncturing, self.modulator, self.snk)
        self.tb.connect(self.bitmap_src, (self.modulator,1))
        self.tb.connect(self.bitmap_src, (self.puncturing,1))
        self.tb.connect(self.bitmap_trigger_puncturing, (self.puncturing,2))
        #self.tb.connect(self.bitmap_trigger, (self.modulator,2))
 
    def run_test06(self):
        self.src.rewind()
        self.tb.run()
         
    def setup_test05(self):
        print "... benchmarking QPSK + 3/4 mapper"
        self.mode = 3
        bitspermode= [0.5,1,1.5,2,3,4,4.5,5,6]
        self.nobits = (bitspermode[self.mode-1])
        self.data_subcarriers = 200
         
         
        self.blks = self.N*(int(10*self.nobits) +1)
        self.tb = gr.top_block()
         
        self.encoder = self._encoder = trellis.encoder_bb(self.fo,0)
        self.unpack = self._unpack = blocks.unpack_k_bits_bb(2)
        self.puncturing = puncture_bb(self.data_subcarriers)
        bmaptrig_stream_puncturing = [1]+[0]*(10/2-1)
        self.bitmap_trigger_puncturing = blocks.vector_source_b(bmaptrig_stream_puncturing, True)
        if self.interleave:
            int_object=trellis.interleaver(2000,666)
            self.interlv = trellis.permutation(int_object.K(),int_object.INTER(),1,gr.sizeof_char)
        #self.bitmap = [self.nobits]*self.data_subcarriers
        self.bitmap = [self.mode]*self.data_subcarriers + [self.mode]*self.data_subcarriers         
        #self.bmaptrig_stream = [1, 1]+[0]*(11-2)
     
        self.bitdata = [randint(0,1) for i in range(self.blks*self.data_subcarriers)]
        #self.data = numpy.array(self.bitdata)*(-2)+1
         
        self.src = blocks.vector_source_b(self.bitdata)
        self.bitmap_src = blocks.vector_source_b(self.bitmap,True, self.data_subcarriers)
        #self.bitmap_trigger = blocks.vector_source_b(self.bmaptrig_stream, True)
        self.modulator = generic_mapper_bcv(self.data_subcarriers,self.coding,10)
        self.snk = blocks.null_sink(gr.sizeof_gr_complex*self.data_subcarriers)
         
         
        #Connect blocks
        self.tb.connect(self.src,self.encoder,self.unpack,self.puncturing)#, self.modulator, self.snk)
        if self.interleave:
            self.tb.connect(self.puncturing,self.interlv, self.modulator, self.snk)
        else:
            self.tb.connect(self.puncturing, self.modulator, self.snk)
        self.tb.connect(self.bitmap_src, (self.modulator,1))
        self.tb.connect(self.bitmap_src, (self.puncturing,1))
        self.tb.connect(self.bitmap_trigger_puncturing, (self.puncturing,2))
        #self.tb.connect(self.bitmap_trigger, (self.modulator,2))
 
    def run_test05(self):
        self.src.rewind()
        self.tb.run()
         
    def setup_test04(self):
        print "... benchmarking 16-QAM + 1/2 mapper"
        self.mode = 4
        bitspermode= [0.5,1,1.5,2,3,4,4.5,5,6]
        self.nobits = (bitspermode[self.mode-1])
        self.data_subcarriers = 200
         
         
        self.blks = self.N*(int(10*self.nobits) +1)
        self.tb = gr.top_block()
         
        self.encoder = self._encoder = trellis.encoder_bb(self.fo,0)
        self.unpack = self._unpack = blocks.unpack_k_bits_bb(2)
        self.puncturing = puncture_bb(self.data_subcarriers)
        bmaptrig_stream_puncturing = [1]+[0]*(10/2-1)
        self.bitmap_trigger_puncturing = blocks.vector_source_b(bmaptrig_stream_puncturing, True)
        if self.interleave:
            int_object=trellis.interleaver(2000,666)
            self.interlv = trellis.permutation(int_object.K(),int_object.INTER(),1,gr.sizeof_char)
        #self.bitmap = [self.nobits]*self.data_subcarriers
        self.bitmap = [self.mode]*self.data_subcarriers + [self.mode]*self.data_subcarriers         
        #self.bmaptrig_stream = [1, 1]+[0]*(11-2)
     
        self.bitdata = [randint(0,1) for i in range(self.blks*self.data_subcarriers)]
        #self.data = numpy.array(self.bitdata)*(-2)+1
         
        self.src = blocks.vector_source_b(self.bitdata)
        self.bitmap_src = blocks.vector_source_b(self.bitmap,True, self.data_subcarriers)
        #self.bitmap_trigger = blocks.vector_source_b(self.bmaptrig_stream, True)
        self.modulator = generic_mapper_bcv(self.data_subcarriers,self.coding,10)
        self.snk = blocks.null_sink(gr.sizeof_gr_complex*self.data_subcarriers)
         
         
        #Connect blocks
        self.tb.connect(self.src,self.encoder,self.unpack,self.puncturing)#, self.modulator, self.snk)
        if self.interleave:
            self.tb.connect(self.puncturing,self.interlv, self.modulator, self.snk)
        else:
            self.tb.connect(self.puncturing, self.modulator, self.snk)
        self.tb.connect(self.bitmap_src, (self.modulator,1))
        self.tb.connect(self.bitmap_src, (self.puncturing,1))
        self.tb.connect(self.bitmap_trigger_puncturing, (self.puncturing,2))
        #self.tb.connect(self.bitmap_trigger, (self.modulator,2))
 
    def run_test04(self):
        self.src.rewind()
        self.tb.run()    
         
    def setup_test03(self):
        print "... benchmarking 16-QAM + 3/4 mapper"
        self.mode = 5
        bitspermode= [0.5,1,1.5,2,3,4,4.5,5,6]
        self.nobits = (bitspermode[self.mode-1])
        self.data_subcarriers = 200
         
         
        self.blks = self.N*(int(10*self.nobits) +1)
        self.tb = gr.top_block()
         
        self.encoder = self._encoder = trellis.encoder_bb(self.fo,0)
        self.unpack = self._unpack = blocks.unpack_k_bits_bb(2)
        self.puncturing = puncture_bb(self.data_subcarriers)
        bmaptrig_stream_puncturing = [1]+[0]*(10/2-1)
        self.bitmap_trigger_puncturing = blocks.vector_source_b(bmaptrig_stream_puncturing, True)
        if self.interleave:
            int_object=trellis.interleaver(2000,666)
            self.interlv = trellis.permutation(int_object.K(),int_object.INTER(),1,gr.sizeof_char)
        #self.bitmap = [self.nobits]*self.data_subcarriers
        self.bitmap = [self.mode]*self.data_subcarriers + [self.mode]*self.data_subcarriers         
        #self.bmaptrig_stream = [1, 1]+[0]*(11-2)
     
        self.bitdata = [randint(0,1) for i in range(self.blks*self.data_subcarriers)]
        #self.data = numpy.array(self.bitdata)*(-2)+1
         
        self.src = blocks.vector_source_b(self.bitdata)
        self.bitmap_src = blocks.vector_source_b(self.bitmap,True, self.data_subcarriers)
        #self.bitmap_trigger = blocks.vector_source_b(self.bmaptrig_stream, True)
        self.modulator = generic_mapper_bcv(self.data_subcarriers,self.coding,10)
        self.snk = blocks.null_sink(gr.sizeof_gr_complex*self.data_subcarriers)
         
         
        #Connect blocks
        self.tb.connect(self.src,self.encoder,self.unpack,self.puncturing)#, self.modulator, self.snk)
        if self.interleave:
            self.tb.connect(self.puncturing,self.interlv, self.modulator, self.snk)
        else:
            self.tb.connect(self.puncturing, self.modulator, self.snk)
        self.tb.connect(self.bitmap_src, (self.modulator,1))
        self.tb.connect(self.bitmap_src, (self.puncturing,1))
        self.tb.connect(self.bitmap_trigger_puncturing, (self.puncturing,2))
        #self.tb.connect(self.bitmap_trigger, (self.modulator,2))
 
    def run_test03(self):
        self.src.rewind()
        self.tb.run() 
         
    def setup_test02(self):
        print "... benchmarking 64-QAM + 2/3 mapper"
        self.mode = 6
        bitspermode= [0.5,1,1.5,2,3,4,4.5,5,6]
        self.nobits = (bitspermode[self.mode-1])
        self.data_subcarriers = 200
         
         
        self.blks = self.N*(int(10*self.nobits) +1)
        self.tb = gr.top_block()
         
        self.encoder = self._encoder = trellis.encoder_bb(self.fo,0)
        self.unpack = self._unpack = blocks.unpack_k_bits_bb(2)
        self.puncturing = puncture_bb(self.data_subcarriers)
        bmaptrig_stream_puncturing = [1]+[0]*(10/2-1)
        self.bitmap_trigger_puncturing = blocks.vector_source_b(bmaptrig_stream_puncturing, True)
        if self.interleave:
            int_object=trellis.interleaver(2000,666)
            self.interlv = trellis.permutation(int_object.K(),int_object.INTER(),1,gr.sizeof_char)
        #self.bitmap = [self.nobits]*self.data_subcarriers
        self.bitmap = [self.mode]*self.data_subcarriers + [self.mode]*self.data_subcarriers         
        #self.bmaptrig_stream = [1, 1]+[0]*(11-2)
     
        self.bitdata = [randint(0,1) for i in range(self.blks*self.data_subcarriers)]
        #self.data = numpy.array(self.bitdata)*(-2)+1
         
        self.src = blocks.vector_source_b(self.bitdata)
        self.bitmap_src = blocks.vector_source_b(self.bitmap,True, self.data_subcarriers)
        #self.bitmap_trigger = blocks.vector_source_b(self.bmaptrig_stream, True)
        self.modulator = generic_mapper_bcv(self.data_subcarriers,self.coding,10)
        self.snk = blocks.null_sink(gr.sizeof_gr_complex*self.data_subcarriers)
         
         
        #Connect blocks
        self.tb.connect(self.src,self.encoder,self.unpack,self.puncturing)#, self.modulator, self.snk)
        if self.interleave:
            self.tb.connect(self.puncturing,self.interlv, self.modulator, self.snk)
        else:
            self.tb.connect(self.puncturing, self.modulator, self.snk)
        self.tb.connect(self.bitmap_src, (self.modulator,1))
        self.tb.connect(self.bitmap_src, (self.puncturing,1))
        self.tb.connect(self.bitmap_trigger_puncturing, (self.puncturing,2))
        #self.tb.connect(self.bitmap_trigger, (self.modulator,2))
 
    def run_test02(self):
        self.src.rewind()
        self.tb.run()
         
    def setup_test01(self):
        print "... benchmarking 64-QAM + 3/4 mapper"
        self.mode = 7
        bitspermode= [0.5,1,1.5,2,3,4,4.5,5,6]
        self.nobits = (bitspermode[self.mode-1])
        self.data_subcarriers = 200
         
         
        self.blks = self.N*(int(10*self.nobits) +1)
        self.tb = gr.top_block()
         
        self.encoder = self._encoder = trellis.encoder_bb(self.fo,0)
        self.unpack = self._unpack = blocks.unpack_k_bits_bb(2)
        self.puncturing = puncture_bb(self.data_subcarriers)
        bmaptrig_stream_puncturing = [1]+[0]*(10/2-1)
        self.bitmap_trigger_puncturing = blocks.vector_source_b(bmaptrig_stream_puncturing, True)
        if self.interleave:
            int_object=trellis.interleaver(2000,666)
            self.interlv = trellis.permutation(int_object.K(),int_object.INTER(),1,gr.sizeof_char)
        #self.bitmap = [self.nobits]*self.data_subcarriers
        self.bitmap = [self.mode]*self.data_subcarriers + [self.mode]*self.data_subcarriers         
        #self.bmaptrig_stream = [1, 1]+[0]*(11-2)
     
        self.bitdata = [randint(0,1) for i in range(self.blks*self.data_subcarriers)]
        #self.data = numpy.array(self.bitdata)*(-2)+1
         
        self.src = blocks.vector_source_b(self.bitdata)
        self.bitmap_src = blocks.vector_source_b(self.bitmap,True, self.data_subcarriers)
        #self.bitmap_trigger = blocks.vector_source_b(self.bmaptrig_stream, True)
        self.modulator = generic_mapper_bcv(self.data_subcarriers,self.coding,10)
        self.snk = blocks.null_sink(gr.sizeof_gr_complex*self.data_subcarriers)
         
         
        #Connect blocks
        self.tb.connect(self.src,self.encoder,self.unpack,self.puncturing)#, self.modulator, self.snk)
        if self.interleave:
            self.tb.connect(self.puncturing,self.interlv, self.modulator, self.snk)
        else:
            self.tb.connect(self.puncturing, self.modulator, self.snk)
        self.tb.connect(self.bitmap_src, (self.modulator,1))
        self.tb.connect(self.bitmap_src, (self.puncturing,1))
        self.tb.connect(self.bitmap_trigger_puncturing, (self.puncturing,2))
        #self.tb.connect(self.bitmap_trigger, (self.modulator,2))
 
    def run_test01(self):
        self.src.rewind()
        dot_str = self.tb.dot_graph()
        file_str = os.path.expanduser('tx.dot')
        dot_file = open(file_str,'w')
        dot_file.write(dot_str)
        dot_file.close()
        self.tb.run()
         
         
    def setup_test08(self):
        print "... benchmarking 64-QAM + 5/6 mapper"
        self.mode = 8
        bitspermode= [0.5,1,1.5,2,3,4,4.5,5,6]
        self.nobits = (bitspermode[self.mode-1])
        self.data_subcarriers = 200
         
         
        self.blks = self.N*(int(10*self.nobits) +1)
        self.tb = gr.top_block()
         
        self.encoder = self._encoder = trellis.encoder_bb(self.fo,0)
        self.unpack = self._unpack = blocks.unpack_k_bits_bb(2)
        self.puncturing = puncture_bb(self.data_subcarriers)
        bmaptrig_stream_puncturing = [1]+[0]*(10/2-1)
        self.bitmap_trigger_puncturing = blocks.vector_source_b(bmaptrig_stream_puncturing, True)
        if self.interleave:
            int_object=trellis.interleaver(2000,666)
            self.interlv = trellis.permutation(int_object.K(),int_object.INTER(),1,gr.sizeof_char)
        #self.bitmap = [self.nobits]*self.data_subcarriers
        self.bitmap = [self.mode]*self.data_subcarriers + [self.mode]*self.data_subcarriers         
        #self.bmaptrig_stream = [1, 1]+[0]*(11-2)
     
        self.bitdata = [randint(0,1) for i in range(self.blks*self.data_subcarriers)]
        #self.data = numpy.array(self.bitdata)*(-2)+1
         
        self.src = blocks.vector_source_b(self.bitdata)
        self.bitmap_src = blocks.vector_source_b(self.bitmap,True, self.data_subcarriers)
        #self.bitmap_trigger = blocks.vector_source_b(self.bmaptrig_stream, True)
        self.modulator = generic_mapper_bcv(self.data_subcarriers,self.coding,10)
        self.snk = blocks.null_sink(gr.sizeof_gr_complex*self.data_subcarriers)
         
         
        #Connect blocks
        self.tb.connect(self.src,self.encoder,self.unpack,self.puncturing)#, self.modulator, self.snk)
        if self.interleave:
            self.tb.connect(self.puncturing,self.interlv, self.modulator, self.snk)
        else:
            self.tb.connect(self.puncturing, self.modulator, self.snk)
        self.tb.connect(self.bitmap_src, (self.modulator,1))
        self.tb.connect(self.bitmap_src, (self.puncturing,1))
        self.tb.connect(self.bitmap_trigger_puncturing, (self.puncturing,2))
        #self.tb.connect(self.bitmap_trigger, (self.modulator,2))
 
    def run_test08(self):
        self.src.rewind()
        self.tb.run()    

    """
    def setup_qpsk0(self):
        self.tb = gr.top_block()

        pts, code = digital.psk_4_0x0_0_1()
        constellation = digital.constellation_psk(pts, code, 4)
        
        self.src = blocks.vector_source_b(self.src_data_qpsk)
        self.p2u = blocks.unpacked_to_packed_bb(1, gr.GR_MSB_FIRST)
        self.mod = digital.generic_mod(constellation, True, self.sps, True, self.eb)
        self.snk = blocks.null_sink(gr.sizeof_gr_complex)

        self.tb.connect(self.src, self.p2u, self.mod, self.snk)

    def run_qpsk0(self):
        self.src.rewind()
        self.tb.run()



    def setup_8psk0(self):
        self.tb = gr.top_block()

        constellation = digital.psk_constellation(8)

        self.src = blocks.vector_source_b(self.src_data_8psk)
        self.p2u = blocks.unpacked_to_packed_bb(1, gr.GR_MSB_FIRST)
        self.mod = digital.generic_mod(constellation, True, self.sps, True, self.eb)
        self.snk = blocks.null_sink(gr.sizeof_gr_complex)

        self.tb.connect(self.src, self.p2u, self.mod, self.snk)

    def run_8psk0(self):
        self.src.rewind()
        self.tb.run()
        
        """

