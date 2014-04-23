#!/usr/bin/env python

from gnuradio import gr, blocks, digital, analog
import random, numpy
from random import randint, random
from ofdm import generic_demapper_vcb, symbol_random_src

class bm_demodulator:
    '''
    @title: Benchmark demapper
    '''
    
    def __init__(self, N):
        self.N = N
        

        # Generate some random bits
        #rndm = random.Random()
        #rndm.seed(0)
        self.coding = 0
        


    def setup_BPSK(self):
        self.nobits = 1
        self.data_subcarriers = 200
        
        self.blks = self.N*(10 + 1)
        self.tb = gr.top_block()
            
        #self.bitmap = [self.nobits]*self.data_subcarriers
        self.demodulator = generic_demapper_vcb(self.data_subcarriers)
        const =  self.demodulator.get_constellation( self.nobits )
        assert( len( const ) == 2**self.nobits )
               
    
        self.bitdata = [random()+1j*random() for i in range(self.blks*self.data_subcarriers)]
        self.src = blocks.vector_source_c(self.bitdata,False, self.data_subcarriers)
        #self.src = symbol_random_src( const, self.data_subcarriers )
        
        self.bitmap = [0]*self.data_subcarriers + [self.nobits]*self.data_subcarriers      
        self.bitmap_src = blocks.vector_source_b(self.bitmap,True, self.data_subcarriers)
        
        self.bmaptrig_stream = [1, 2]+[0]*(11-2)
        self.bitmap_trigger = blocks.vector_source_b(self.bmaptrig_stream, True)
        
        self.snk = blocks.null_sink(gr.sizeof_char)
                
        self.tb.connect(self.src,self.demodulator,self.snk)
        self.tb.connect(self.bitmap_src,(self.demodulator,1))
        self.tb.connect(self.bitmap_trigger,(self.demodulator,2))

    def run_BPSK(self):
        self.src.rewind()
        self.tb.run()
    
    def setup_QPSK(self):
        self.nobits = 2
        self.data_subcarriers = 200
        
        self.blks = self.N*(10 + 1)
        self.tb = gr.top_block()
            
        #self.bitmap = [self.nobits]*self.data_subcarriers
        self.demodulator = generic_demapper_vcb(self.data_subcarriers)
        const =  self.demodulator.get_constellation( self.nobits )
        assert( len( const ) == 2**self.nobits )
               
    
        self.bitdata = [random()+1j*random() for i in range(self.blks*self.data_subcarriers)]
        self.src = blocks.vector_source_c(self.bitdata,False, self.data_subcarriers)
        #self.src = symbol_random_src( const, self.data_subcarriers )
        
        self.bitmap = [0]*self.data_subcarriers + [self.nobits]*self.data_subcarriers      
        self.bitmap_src = blocks.vector_source_b(self.bitmap,True, self.data_subcarriers)
        
        self.bmaptrig_stream = [1, 2]+[0]*(11-2)
        self.bitmap_trigger = blocks.vector_source_b(self.bmaptrig_stream, True)
        
        self.snk = blocks.null_sink(gr.sizeof_char)
                
        self.tb.connect(self.src,self.demodulator,self.snk)
        self.tb.connect(self.bitmap_src,(self.demodulator,1))
        self.tb.connect(self.bitmap_trigger,(self.demodulator,2))


    def run_QPSK(self):
        self.src.rewind()
        self.tb.run()
        
    def setup_8_PSK(self):
        self.nobits = 4
        self.data_subcarriers = 200
        
        self.blks = self.N*(10 + 1)
        self.tb = gr.top_block()
            
        #self.bitmap = [self.nobits]*self.data_subcarriers
        self.demodulator = generic_demapper_vcb(self.data_subcarriers)
        const =  self.demodulator.get_constellation( self.nobits )
        assert( len( const ) == 2**self.nobits )
               
    
        self.bitdata = [random()+1j*random() for i in range(self.blks*self.data_subcarriers)]
        self.src = blocks.vector_source_c(self.bitdata,False, self.data_subcarriers)
        #self.src = symbol_random_src( const, self.data_subcarriers )
        
        self.bitmap = [0]*self.data_subcarriers + [self.nobits]*self.data_subcarriers      
        self.bitmap_src = blocks.vector_source_b(self.bitmap,True, self.data_subcarriers)
        
        self.bmaptrig_stream = [1, 2]+[0]*(11-2)
        self.bitmap_trigger = blocks.vector_source_b(self.bmaptrig_stream, True)
        
        self.snk = blocks.null_sink(gr.sizeof_char)
                
        self.tb.connect(self.src,self.demodulator,self.snk)
        self.tb.connect(self.bitmap_src,(self.demodulator,1))
        self.tb.connect(self.bitmap_trigger,(self.demodulator,2))


    def run_8_PSK(self):
        self.src.rewind()
        self.tb.run()
        
    def setup_16_QAM(self):
        self.nobits = 4
        self.data_subcarriers = 200
        
        self.blks = self.N*(10 + 1)
        self.tb = gr.top_block()
            
        #self.bitmap = [self.nobits]*self.data_subcarriers
        self.demodulator = generic_demapper_vcb(self.data_subcarriers)
        const =  self.demodulator.get_constellation( self.nobits )
        assert( len( const ) == 2**self.nobits )
               
    
        self.bitdata = [random()+1j*random() for i in range(self.blks*self.data_subcarriers)]
        self.src = blocks.vector_source_c(self.bitdata,False, self.data_subcarriers)
        #self.src = symbol_random_src( const, self.data_subcarriers )
        
        self.bitmap = [0]*self.data_subcarriers + [self.nobits]*self.data_subcarriers      
        self.bitmap_src = blocks.vector_source_b(self.bitmap,True, self.data_subcarriers)
        
        self.bmaptrig_stream = [1, 2]+[0]*(11-2)
        self.bitmap_trigger = blocks.vector_source_b(self.bmaptrig_stream, True)
        
        self.snk = blocks.null_sink(gr.sizeof_char)
                
        self.tb.connect(self.src,self.demodulator,self.snk)
        self.tb.connect(self.bitmap_src,(self.demodulator,1))
        self.tb.connect(self.bitmap_trigger,(self.demodulator,2))


    def run_16_QAM(self):
        self.src.rewind()
        self.tb.run()    
        
    def setup_32_QAM(self):
        self.nobits = 5
        self.data_subcarriers = 200
        
        self.blks = self.N*(10 + 1)
        self.tb = gr.top_block()
            
        #self.bitmap = [self.nobits]*self.data_subcarriers
        self.demodulator = generic_demapper_vcb(self.data_subcarriers)
        const =  self.demodulator.get_constellation( self.nobits )
        assert( len( const ) == 2**self.nobits )
               
    
        self.bitdata = [random()+1j*random() for i in range(self.blks*self.data_subcarriers)]
        self.src = blocks.vector_source_c(self.bitdata,False, self.data_subcarriers)
        #self.src = symbol_random_src( const, self.data_subcarriers )
        
        self.bitmap = [0]*self.data_subcarriers + [self.nobits]*self.data_subcarriers      
        self.bitmap_src = blocks.vector_source_b(self.bitmap,True, self.data_subcarriers)
        
        self.bmaptrig_stream = [1, 2]+[0]*(11-2)
        self.bitmap_trigger = blocks.vector_source_b(self.bmaptrig_stream, True)
        
        self.snk = blocks.null_sink(gr.sizeof_char)
                
        self.tb.connect(self.src,self.demodulator,self.snk)
        self.tb.connect(self.bitmap_src,(self.demodulator,1))
        self.tb.connect(self.bitmap_trigger,(self.demodulator,2))


    def run_32_QAM(self):
        self.src.rewind()
        self.tb.run() 
        
    def setup_64_QAM(self):
        self.nobits = 6
        self.data_subcarriers = 200
        
        self.blks = self.N*(10 + 1)
        self.tb = gr.top_block()
            
        #self.bitmap = [self.nobits]*self.data_subcarriers
        self.demodulator = generic_demapper_vcb(self.data_subcarriers)
        const =  self.demodulator.get_constellation( self.nobits )
        assert( len( const ) == 2**self.nobits )
               
    
        self.bitdata = [random()+1j*random() for i in range(self.blks*self.data_subcarriers)]
        self.src = blocks.vector_source_c(self.bitdata,False, self.data_subcarriers)
        #self.src = symbol_random_src( const, self.data_subcarriers )
        
        self.bitmap = [0]*self.data_subcarriers + [self.nobits]*self.data_subcarriers      
        self.bitmap_src = blocks.vector_source_b(self.bitmap,True, self.data_subcarriers)
        
        self.bmaptrig_stream = [1, 2]+[0]*(11-2)
        self.bitmap_trigger = blocks.vector_source_b(self.bmaptrig_stream, True)
        
        self.snk = blocks.null_sink(gr.sizeof_char)
                
        self.tb.connect(self.src,self.demodulator,self.snk)
        self.tb.connect(self.bitmap_src,(self.demodulator,1))
        self.tb.connect(self.bitmap_trigger,(self.demodulator,2))


    def run_64_QAM(self):
        self.src.rewind()
        self.tb.run()
        
    def setup_128_QAM(self):
        self.nobits = 7
        self.data_subcarriers = 200
        
        self.blks = self.N*(10 + 1)
        self.tb = gr.top_block()
            
        #self.bitmap = [self.nobits]*self.data_subcarriers
        self.demodulator = generic_demapper_vcb(self.data_subcarriers)
        const =  self.demodulator.get_constellation( self.nobits )
        assert( len( const ) == 2**self.nobits )
               
    
        self.bitdata = [random()+1j*random() for i in range(self.blks*self.data_subcarriers)]
        self.src = blocks.vector_source_c(self.bitdata,False, self.data_subcarriers)
        #self.src = symbol_random_src( const, self.data_subcarriers )
        
        self.bitmap = [0]*self.data_subcarriers + [self.nobits]*self.data_subcarriers      
        self.bitmap_src = blocks.vector_source_b(self.bitmap,True, self.data_subcarriers)
        
        self.bmaptrig_stream = [1, 2]+[0]*(11-2)
        self.bitmap_trigger = blocks.vector_source_b(self.bmaptrig_stream, True)
        
        self.snk = blocks.null_sink(gr.sizeof_char)
                
        self.tb.connect(self.src,self.demodulator,self.snk)
        self.tb.connect(self.bitmap_src,(self.demodulator,1))
        self.tb.connect(self.bitmap_trigger,(self.demodulator,2))


    def run_128_QAM(self):
        self.src.rewind()
        self.tb.run()
        
        
    def setup_256_QAM(self):
        self.nobits = 8
        self.data_subcarriers = 200
        
        self.blks = self.N*(10 + 1)
        self.tb = gr.top_block()
            
        #self.bitmap = [self.nobits]*self.data_subcarriers
        self.demodulator = generic_demapper_vcb(self.data_subcarriers)
        const =  self.demodulator.get_constellation( self.nobits )
        assert( len( const ) == 2**self.nobits )
               
    
        self.bitdata = [random()+1j*random() for i in range(self.blks*self.data_subcarriers)]
        self.src = blocks.vector_source_c(self.bitdata,False, self.data_subcarriers)
        #self.src = symbol_random_src( const, self.data_subcarriers )
        
        self.bitmap = [0]*self.data_subcarriers + [self.nobits]*self.data_subcarriers      
        self.bitmap_src = blocks.vector_source_b(self.bitmap,True, self.data_subcarriers)
        
        self.bmaptrig_stream = [1, 2]+[0]*(11-2)
        self.bitmap_trigger = blocks.vector_source_b(self.bmaptrig_stream, True)
        
        self.snk = blocks.null_sink(gr.sizeof_char)
                
        self.tb.connect(self.src,self.demodulator,self.snk)
        self.tb.connect(self.bitmap_src,(self.demodulator,1))
        self.tb.connect(self.bitmap_trigger,(self.demodulator,2))


    def run_256_QAM(self):
        self.src.rewind()
        self.tb.run() 
        


