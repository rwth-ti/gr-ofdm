#!/usr/bin/env python

from gnuradio import gr, blocks, digital, analog, trellis
import random, numpy, ofdm
from random import randint, random
from ofdm import generic_softdemapper_vcf, symbol_random_src, depuncture_ff
import os

class bm_decoding:
    '''
    @title: Benchmark demapper
    '''
    
    def __init__(self, N):
        self.N = N
        

        # Generate some random bits
        #rndm = random.Random()
        #rndm.seed(0)
        self.coding = 1
        self.interleave = 0
        self.fo=ofdm.fsm(1,2,[91,121])
        


    def setup_test07(self):
        print "... benchmarking BPSK demapper"
        self.mode = 1
        bitspermode = [0.5,1,1.5,2,3,4,4.5,5,6]
        self.data_subcarriers = 200
        self.chunkdivisor = 2
        bitcount_vec = [(int)(self.data_subcarriers*10*bitspermode[self.mode-1])]
        dm_csi = [1]*self.data_subcarriers # TODO
        self.dm_csi = blocks.vector_source_f(dm_csi,True)
        
        self.blks = self.N*(10 + 1)
        self.tb = gr.top_block()
        
        self.bitcount_src = blocks.vector_source_i(bitcount_vec,True,1)
        self.depuncturing = depuncture_ff(self.data_subcarriers,0)
        bmaptrig_stream_puncturing = [1]+[0]*(10/2-1)
        self.bitmap_trigger_puncturing = blocks.vector_source_b(bmaptrig_stream_puncturing, True)
        self.data_decoder = ofdm.viterbi_combined_fb(self.fo,self.data_subcarriers,-1,-1,2,self.chunkdivisor,[-1,-1,-1,1,1,-1,1,1],ofdm.TRELLIS_EUCLIDEAN)
        if self.interleave:
            int_object=trellis.interleaver(2000,666)
            self.deinterlv = trellis.permutation(int_object.K(),int_object.DEINTER(),1,gr.sizeof_float)
            
        #self.bitmap = [self.nobits]*self.data_subcarriers
        self.demodulator = generic_softdemapper_vcf(self.data_subcarriers, 11, self.coding)
        #const =  self.demodulator.get_constellation( self.nobits )
        #assert( len( const ) == 2**self.nobits )
               
    
        self.bitdata = [random()+1j*random() for i in range(self.blks*self.data_subcarriers)]
        self.src = blocks.vector_source_c(self.bitdata,False, self.data_subcarriers)
        #self.src = symbol_random_src( const, self.data_subcarriers )
        
        self.bitmap = [self.mode]*self.data_subcarriers      
        self.bitmap_src = blocks.vector_source_b(self.bitmap,True, self.data_subcarriers)
        
        #self.bmaptrig_stream = [1, 2]+[0]*(11-2)
        #self.bitmap_trigger = blocks.vector_source_b(self.bmaptrig_stream, True)
        
        self.snk = blocks.null_sink(gr.sizeof_char)
        
        #Connect blocks     
        self.tb.connect(self.src,self.demodulator)
        if self.interleave:
            self.tb.connect(self.demodulator,self.deinterlv, self.depuncturing, self.data_decoder,self.snk)
        else:
            self.tb.connect(self.demodulator, self.depuncturing, self.data_decoder,self.snk)
        self.tb.connect(self.bitmap_src,(self.demodulator,1))
        self.tb.connect(self.dm_csi,blocks.stream_to_vector(gr.sizeof_float,self.data_subcarriers),(self.demodulator,2))
        self.tb.connect(self.bitmap_src,(self.depuncturing,1))
        self.tb.connect(self.bitmap_trigger_puncturing, (self.depuncturing,2))
        self.tb.connect(self.bitcount_src, ofdm.multiply_const_ii(1./self.chunkdivisor), (self.data_decoder,1))
        #self.tb.connect(self.bitmap_trigger,(self.demodulator,2))

    def run_test07(self):
        self.src.rewind()
        self.tb.run()
    
#     def setup_test06(self):
#         print "... benchmarking QPSK demapper"
#         self.nobits = 2
#         self.data_subcarriers = 200
#         
#         self.blks = self.N*(10 + 1)
#         self.tb = gr.top_block()
#             
#         #self.bitmap = [self.nobits]*self.data_subcarriers
#         self.demodulator = generic_demapper_vcb(self.data_subcarriers,10)
#         const =  self.demodulator.get_constellation( self.nobits )
#         assert( len( const ) == 2**self.nobits )
#                
#     
#         self.bitdata = [random()+1j*random() for i in range(self.blks*self.data_subcarriers)]
#         self.src = blocks.vector_source_c(self.bitdata,False, self.data_subcarriers)
#         #self.src = symbol_random_src( const, self.data_subcarriers )
#         
#         self.bitmap = [0]*self.data_subcarriers + [self.nobits]*self.data_subcarriers      
#         self.bitmap_src = blocks.vector_source_b(self.bitmap,True, self.data_subcarriers)
#         
#         #self.bmaptrig_stream = [1, 2]+[0]*(11-2)
#         #self.bitmap_trigger = blocks.vector_source_b(self.bmaptrig_stream, True)
#         
#         self.snk = blocks.null_sink(gr.sizeof_char)
#                 
#         self.tb.connect(self.src,self.demodulator,self.snk)
#         self.tb.connect(self.bitmap_src,(self.demodulator,1))
#         #self.tb.connect(self.bitmap_trigger,(self.demodulator,2))
# 
# 
#     def run_test06(self):
#         self.src.rewind()
#         self.tb.run()
#         
#     def setup_test05(self):
#         print "... benchmarking 8-PSK demapper"
#         self.nobits = 4
#         self.data_subcarriers = 200
#         
#         self.blks = self.N*(10 + 1)
#         self.tb = gr.top_block()
#             
#         #self.bitmap = [self.nobits]*self.data_subcarriers
#         self.demodulator = generic_demapper_vcb(self.data_subcarriers,10)
#         const =  self.demodulator.get_constellation( self.nobits )
#         assert( len( const ) == 2**self.nobits )
#                
#     
#         self.bitdata = [random()+1j*random() for i in range(self.blks*self.data_subcarriers)]
#         self.src = blocks.vector_source_c(self.bitdata,False, self.data_subcarriers)
#         #self.src = symbol_random_src( const, self.data_subcarriers )
#         
#         self.bitmap = [0]*self.data_subcarriers + [self.nobits]*self.data_subcarriers      
#         self.bitmap_src = blocks.vector_source_b(self.bitmap,True, self.data_subcarriers)
#         
#         #self.bmaptrig_stream = [1, 2]+[0]*(11-2)
#         #self.bitmap_trigger = blocks.vector_source_b(self.bmaptrig_stream, True)
#         
#         self.snk = blocks.null_sink(gr.sizeof_char)
#                 
#         self.tb.connect(self.src,self.demodulator,self.snk)
#         self.tb.connect(self.bitmap_src,(self.demodulator,1))
#         #self.tb.connect(self.bitmap_trigger,(self.demodulator,2))
# 
# 
#     def run_test05(self):
#         self.src.rewind()
#         self.tb.run()
#         
#     def setup_test04(self):
#         print "... benchmarking 16-QAM demapper"
#         self.nobits = 4
#         self.data_subcarriers = 200
#         
#         self.blks = self.N*(10 + 1)
#         self.tb = gr.top_block()
#             
#         #self.bitmap = [self.nobits]*self.data_subcarriers
#         self.demodulator = generic_demapper_vcb(self.data_subcarriers,10)
#         const =  self.demodulator.get_constellation( self.nobits )
#         assert( len( const ) == 2**self.nobits )
#                
#     
#         self.bitdata = [random()+1j*random() for i in range(self.blks*self.data_subcarriers)]
#         self.src = blocks.vector_source_c(self.bitdata,False, self.data_subcarriers)
#         #self.src = symbol_random_src( const, self.data_subcarriers )
#         
#         self.bitmap = [0]*self.data_subcarriers + [self.nobits]*self.data_subcarriers      
#         self.bitmap_src = blocks.vector_source_b(self.bitmap,True, self.data_subcarriers)
#         
#         #self.bmaptrig_stream = [1, 2]+[0]*(11-2)
#         #self.bitmap_trigger = blocks.vector_source_b(self.bmaptrig_stream, True)
#         
#         self.snk = blocks.null_sink(gr.sizeof_char)
#                 
#         self.tb.connect(self.src,self.demodulator,self.snk)
#         self.tb.connect(self.bitmap_src,(self.demodulator,1))
#         #self.tb.connect(self.bitmap_trigger,(self.demodulator,2))
# 
# 
#     def run_test04(self):
#         self.src.rewind()
#         self.tb.run()    
#         
#     def setup_test03(self):
#         print "... benchmarking 32-QAM demapper"
#         self.nobits = 5
#         self.data_subcarriers = 200
#         
#         self.blks = self.N*(10 + 1)
#         self.tb = gr.top_block()
#             
#         #self.bitmap = [self.nobits]*self.data_subcarriers
#         self.demodulator = generic_demapper_vcb(self.data_subcarriers,10)
#         const =  self.demodulator.get_constellation( self.nobits )
#         assert( len( const ) == 2**self.nobits )
#                
#     
#         self.bitdata = [random()+1j*random() for i in range(self.blks*self.data_subcarriers)]
#         self.src = blocks.vector_source_c(self.bitdata,False, self.data_subcarriers)
#         #self.src = symbol_random_src( const, self.data_subcarriers )
#         
#         self.bitmap = [0]*self.data_subcarriers + [self.nobits]*self.data_subcarriers      
#         self.bitmap_src = blocks.vector_source_b(self.bitmap,True, self.data_subcarriers)
#         
#         #self.bmaptrig_stream = [1, 2]+[0]*(11-2)
#         #self.bitmap_trigger = blocks.vector_source_b(self.bmaptrig_stream, True)
#         
#         self.snk = blocks.null_sink(gr.sizeof_char)
#                 
#         self.tb.connect(self.src,self.demodulator,self.snk)
#         self.tb.connect(self.bitmap_src,(self.demodulator,1))
#         #self.tb.connect(self.bitmap_trigger,(self.demodulator,2))
# 
# 
#     def run_test03(self):
#         self.src.rewind()
#         self.tb.run() 
#         
#     def setup_test02(self):
#         print "... benchmarking 64-QAM demapper"
#         self.nobits = 6
#         self.data_subcarriers = 200
#         
#         self.blks = self.N*(10 + 1)
#         self.tb = gr.top_block()
#             
#         #self.bitmap = [self.nobits]*self.data_subcarriers
#         self.demodulator = generic_demapper_vcb(self.data_subcarriers,10)
#         const =  self.demodulator.get_constellation( self.nobits )
#         assert( len( const ) == 2**self.nobits )
#                
#     
#         self.bitdata = [random()+1j*random() for i in range(self.blks*self.data_subcarriers)]
#         self.src = blocks.vector_source_c(self.bitdata,False, self.data_subcarriers)
#         #self.src = symbol_random_src( const, self.data_subcarriers )
#         
#         self.bitmap = [0]*self.data_subcarriers + [self.nobits]*self.data_subcarriers      
#         self.bitmap_src = blocks.vector_source_b(self.bitmap,True, self.data_subcarriers)
#         
#         #self.bmaptrig_stream = [1, 2]+[0]*(11-2)
#         #self.bitmap_trigger = blocks.vector_source_b(self.bmaptrig_stream, True)
#         
#         self.snk = blocks.null_sink(gr.sizeof_char)
#                 
#         self.tb.connect(self.src,self.demodulator,self.snk)
#         self.tb.connect(self.bitmap_src,(self.demodulator,1))
#         #self.tb.connect(self.bitmap_trigger,(self.demodulator,2))
# 
# 
#     def run_test02(self):
#         self.src.rewind()
#         self.tb.run()
#         
#     def setup_test01(self):
#         print "... benchmarking 128-QAM demapper"
#         self.nobits = 7
#         self.data_subcarriers = 200
#         
#         self.blks = self.N*(10 + 1)
#         self.tb = gr.top_block()
#             
#         #self.bitmap = [self.nobits]*self.data_subcarriers
#         self.demodulator = generic_demapper_vcb(self.data_subcarriers,10)
#         const =  self.demodulator.get_constellation( self.nobits )
#         assert( len( const ) == 2**self.nobits )
#                
#     
#         self.bitdata = [random()+1j*random() for i in range(self.blks*self.data_subcarriers)]
#         self.src = blocks.vector_source_c(self.bitdata,False, self.data_subcarriers)
#         #self.src = symbol_random_src( const, self.data_subcarriers )
#         
#         self.bitmap = [0]*self.data_subcarriers + [self.nobits]*self.data_subcarriers      
#         self.bitmap_src = blocks.vector_source_b(self.bitmap,True, self.data_subcarriers)
#         
#         #self.bmaptrig_stream = [1, 2]+[0]*(11-2)
#         #self.bitmap_trigger = blocks.vector_source_b(self.bmaptrig_stream, True)
#         
#         self.snk = blocks.null_sink(gr.sizeof_char)
#                 
#         self.tb.connect(self.src,self.demodulator,self.snk)
#         self.tb.connect(self.bitmap_src,(self.demodulator,1))
#         #self.tb.connect(self.bitmap_trigger,(self.demodulator,2))
# 
# 
#     def run_test01(self):
#         self.src.rewind()
#         dot_str = self.tb.dot_graph()
#         file_str = os.path.expanduser('rx.dot')
#         dot_file = open(file_str,'w')
#         dot_file.write(dot_str)
#         dot_file.close()
#         self.tb.run()
#         
#         
#     def setup_test08(self):
#         print "... benchmarking 256-QAM demapper"
#         self.nobits = 8
#         self.data_subcarriers = 200
#         
#         self.blks = self.N*(10 + 1)
#         self.tb = gr.top_block()
#             
#         #self.bitmap = [self.nobits]*self.data_subcarriers
#         self.demodulator = generic_demapper_vcb(self.data_subcarriers,10)
#         const =  self.demodulator.get_constellation( self.nobits )
#         assert( len( const ) == 2**self.nobits )
#                
#     
#         self.bitdata = [random()+1j*random() for i in range(self.blks*self.data_subcarriers)]
#         self.src = blocks.vector_source_c(self.bitdata,False, self.data_subcarriers)
#         #self.src = symbol_random_src( const, self.data_subcarriers )
#         
#         self.bitmap = [0]*self.data_subcarriers + [self.nobits]*self.data_subcarriers      
#         self.bitmap_src = blocks.vector_source_b(self.bitmap,True, self.data_subcarriers)
#         
#         #self.bmaptrig_stream = [1, 2]+[0]*(11-2)
#         #self.bitmap_trigger = blocks.vector_source_b(self.bmaptrig_stream, True)
#         
#         self.snk = blocks.null_sink(gr.sizeof_char)
#                 
#         self.tb.connect(self.src,self.demodulator,self.snk)
#         self.tb.connect(self.bitmap_src,(self.demodulator,1))
#         #self.tb.connect(self.bitmap_trigger,(self.demodulator,2))
# 
# 
#     def run_test08(self):
#         self.src.rewind()
#         self.tb.run() 
        


