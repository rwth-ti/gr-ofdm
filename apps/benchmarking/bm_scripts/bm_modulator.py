#!/usr/bin/env python

from gnuradio import gr, blocks, digital, analog
import random, numpy
from random import randint
from ofdm import generic_mapper_bcv

class bm_modulator:
    '''
    @title: Benchmark PSK modulators
    '''
    
    def __init__(self, N):
        self.N = N
        

        # Generate some random bits
        rndm = random.Random()
        rndm.seed(0)
        self.coding = 0
        


    def setup_BPSK(self):
        self.nobits = 1
        self.data_subcarriers = 200
        
        self.blks = self.N*(10*self.nobits +1)
        self.tb = gr.top_block()
            
        #self.bitmap = [self.nobits]*self.data_subcarriers
        self.bitmap = [1]*self.data_subcarriers + [self.nobits]*self.data_subcarriers         
        self.bmaptrig_stream = [1, 1]+[0]*(11-2)
    
        self.bitdata = [randint(0,1) for i in range(self.blks*self.data_subcarriers)]
        self.data = numpy.array(self.bitdata)*(-2)+1
        
        self.src = blocks.vector_source_b(self.bitdata)
        self.bitmap_src = blocks.vector_source_b(self.bitmap,True, self.data_subcarriers)
        self.bitmap_trigger = blocks.vector_source_b(self.bmaptrig_stream, True)
        self.modulator = generic_mapper_bcv(self.data_subcarriers,self.coding)
        self.snk = blocks.null_sink(gr.sizeof_gr_complex*self.data_subcarriers)
        self.tb.connect(self.src, self.modulator, self.snk)
        self.tb.connect(self.bitmap_src, (self.modulator,1))
        self.tb.connect(self.bitmap_trigger, (self.modulator,2))

    def run_BPSK(self):
        self.src.rewind()
        self.tb.run()
        
    def setup_QPSK(self):
        self.nobits = 2
        self.data_subcarriers = 200
        
        self.blks = self.N*(10*self.nobits +1)
        self.tb = gr.top_block()
            
        #self.bitmap = [self.nobits]*self.data_subcarriers
        self.bitmap = [1]*self.data_subcarriers + [self.nobits]*self.data_subcarriers         
        self.bmaptrig_stream = [1, 1]+[0]*(11-2)
    
        self.bitdata = [randint(0,1) for i in range(self.blks*self.data_subcarriers)]
        self.data = numpy.array(self.bitdata)*(-2)+1
        
        self.src = blocks.vector_source_b(self.bitdata)
        self.bitmap_src = blocks.vector_source_b(self.bitmap,True, self.data_subcarriers)
        self.bitmap_trigger = blocks.vector_source_b(self.bmaptrig_stream, True)
        self.modulator = generic_mapper_bcv(self.data_subcarriers,self.coding)
        self.snk = blocks.null_sink(gr.sizeof_gr_complex*self.data_subcarriers)
        self.tb.connect(self.src, self.modulator, self.snk)
        self.tb.connect(self.bitmap_src, (self.modulator,1))
        self.tb.connect(self.bitmap_trigger, (self.modulator,2))

    def run_QPSK(self):
        self.src.rewind()
        self.tb.run()
        
    def setup_8_PSK(self):
        self.nobits = 3
        self.data_subcarriers = 200
        
        self.blks = self.N*(10*self.nobits +1)
        self.tb = gr.top_block()
            
        #self.bitmap = [self.nobits]*self.data_subcarriers
        self.bitmap = [1]*self.data_subcarriers + [self.nobits]*self.data_subcarriers        
        self.bmaptrig_stream = [1, 1]+[0]*(11-2)
    
        self.bitdata = [randint(0,1) for i in range(self.blks*self.data_subcarriers)]
        self.data = numpy.array(self.bitdata)*(-2)+1
        
        self.src = blocks.vector_source_b(self.bitdata)
        self.bitmap_src = blocks.vector_source_b(self.bitmap,True, self.data_subcarriers)
        self.bitmap_trigger = blocks.vector_source_b(self.bmaptrig_stream, True)
        self.modulator = generic_mapper_bcv(self.data_subcarriers,self.coding)
        self.snk = blocks.null_sink(gr.sizeof_gr_complex*self.data_subcarriers)
        self.tb.connect(self.src, self.modulator, self.snk)
        self.tb.connect(self.bitmap_src, (self.modulator,1))
        self.tb.connect(self.bitmap_trigger, (self.modulator,2))

    def run_8_PSK(self):
        self.src.rewind()
        self.tb.run()
        
    def setup_16_QAM(self):
        self.nobits = 4
        self.data_subcarriers = 200
        
        self.blks = self.N*(10*self.nobits +1)
        self.tb = gr.top_block()
            
        #self.bitmap = [self.nobits]*self.data_subcarriers
        self.bitmap = [1]*self.data_subcarriers + [self.nobits]*self.data_subcarriers         
        self.bmaptrig_stream = [1, 1]+[0]*(11-2)
    
        self.bitdata = [randint(0,1) for i in range(self.blks*self.data_subcarriers)]
        self.data = numpy.array(self.bitdata)*(-2)+1
        
        self.src = blocks.vector_source_b(self.bitdata)
        self.bitmap_src = blocks.vector_source_b(self.bitmap,True, self.data_subcarriers)
        self.bitmap_trigger = blocks.vector_source_b(self.bmaptrig_stream, True)
        self.modulator = generic_mapper_bcv(self.data_subcarriers,self.coding)
        self.snk = blocks.null_sink(gr.sizeof_gr_complex*self.data_subcarriers)
        self.tb.connect(self.src, self.modulator, self.snk)
        self.tb.connect(self.bitmap_src, (self.modulator,1))
        self.tb.connect(self.bitmap_trigger, (self.modulator,2))

    def run_16_QAM(self):
        self.src.rewind()
        self.tb.run()    
        
    def setup_32_QAM(self):
        self.nobits = 5
        self.data_subcarriers = 200
        
        self.blks = self.N*(10*self.nobits +1)
        self.tb = gr.top_block()
            
        #self.bitmap = [self.nobits]*self.data_subcarriers
        self.bitmap = [1]*self.data_subcarriers + [self.nobits]*self.data_subcarriers         
        self.bmaptrig_stream = [1, 1]+[0]*(11-2)
    
        self.bitdata = [randint(0,1) for i in range(self.blks*self.data_subcarriers)]
        self.data = numpy.array(self.bitdata)*(-2)+1
        
        self.src = blocks.vector_source_b(self.bitdata)
        self.bitmap_src = blocks.vector_source_b(self.bitmap,True, self.data_subcarriers)
        self.bitmap_trigger = blocks.vector_source_b(self.bmaptrig_stream, True)
        self.modulator = generic_mapper_bcv(self.data_subcarriers,self.coding)
        self.snk = blocks.null_sink(gr.sizeof_gr_complex*self.data_subcarriers)
        self.tb.connect(self.src, self.modulator, self.snk)
        self.tb.connect(self.bitmap_src, (self.modulator,1))
        self.tb.connect(self.bitmap_trigger, (self.modulator,2))

    def run_32_QAM(self):
        self.src.rewind()
        self.tb.run() 
        
    def setup_64_QAM(self):
        self.nobits = 6
        self.data_subcarriers = 200
        
        self.blks = self.N*(10*self.nobits +1)
        self.tb = gr.top_block()
            
        #self.bitmap = [self.nobits]*self.data_subcarriers
        self.bitmap = [1]*self.data_subcarriers + [self.nobits]*self.data_subcarriers         
        self.bmaptrig_stream = [1, 1]+[0]*(11-2)
    
        self.bitdata = [randint(0,1) for i in range(self.blks*self.data_subcarriers)]
        self.data = numpy.array(self.bitdata)*(-2)+1
        
        self.src = blocks.vector_source_b(self.bitdata)
        self.bitmap_src = blocks.vector_source_b(self.bitmap,True, self.data_subcarriers)
        self.bitmap_trigger = blocks.vector_source_b(self.bmaptrig_stream, True)
        self.modulator = generic_mapper_bcv(self.data_subcarriers,self.coding)
        self.snk = blocks.null_sink(gr.sizeof_gr_complex*self.data_subcarriers)
        self.tb.connect(self.src, self.modulator, self.snk)
        self.tb.connect(self.bitmap_src, (self.modulator,1))
        self.tb.connect(self.bitmap_trigger, (self.modulator,2))

    def run_64_QAM(self):
        self.src.rewind()
        self.tb.run()
        
    def setup_128_QAM(self):
        self.nobits = 7
        self.data_subcarriers = 200
        
        self.blks = self.N*(10*self.nobits +1)
        self.tb = gr.top_block()
            
        #self.bitmap = [self.nobits]*self.data_subcarriers
        self.bitmap = [1]*self.data_subcarriers + [self.nobits]*self.data_subcarriers         
        self.bmaptrig_stream = [1, 1]+[0]*(11-2)
    
        self.bitdata = [randint(0,1) for i in range(self.blks*self.data_subcarriers)]
        self.data = numpy.array(self.bitdata)*(-2)+1
        
        self.src = blocks.vector_source_b(self.bitdata)
        self.bitmap_src = blocks.vector_source_b(self.bitmap,True, self.data_subcarriers)
        self.bitmap_trigger = blocks.vector_source_b(self.bmaptrig_stream, True)
        self.modulator = generic_mapper_bcv(self.data_subcarriers,self.coding)
        self.snk = blocks.null_sink(gr.sizeof_gr_complex*self.data_subcarriers)
        self.tb.connect(self.src, self.modulator, self.snk)
        self.tb.connect(self.bitmap_src, (self.modulator,1))
        self.tb.connect(self.bitmap_trigger, (self.modulator,2))

    def run_128_QAM(self):
        self.src.rewind()
        self.tb.run()
        
        
    def setup_256_QAM(self):
        self.nobits = 8
        self.data_subcarriers = 200
        
        self.blks = self.N*(10*self.nobits +1)
        self.tb = gr.top_block()
            
        #self.bitmap = [self.nobits]*self.data_subcarriers
        self.bitmap = [1]*self.data_subcarriers + [self.nobits]*self.data_subcarriers         
        self.bmaptrig_stream = [1, 1]+[0]*(11-2)
    
        self.bitdata = [randint(0,1) for i in range(self.blks*self.data_subcarriers)]
        self.data = numpy.array(self.bitdata)*(-2)+1
        
        self.src = blocks.vector_source_b(self.bitdata)
        self.bitmap_src = blocks.vector_source_b(self.bitmap,True, self.data_subcarriers)
        self.bitmap_trigger = blocks.vector_source_b(self.bmaptrig_stream, True)
        self.modulator = generic_mapper_bcv(self.data_subcarriers,self.coding)
        self.snk = blocks.null_sink(gr.sizeof_gr_complex*self.data_subcarriers)
        self.tb.connect(self.src, self.modulator, self.snk)
        self.tb.connect(self.bitmap_src, (self.modulator,1))
        self.tb.connect(self.bitmap_trigger, (self.modulator,2))

    def run_256_QAM(self):
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

