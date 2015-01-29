from gnuradio import zeromq
import math

class tx_rpc_manager():
  def __init__(self,fft_length, subcarriers, data_blocks, frame_length, cp_length, tx_freq, bandwidth):
      
    bits = 8*subcarriers*data_blocks # max. QAM256
    samples_per_frame = frame_length*(fft_length + cp_length)
    tb = 1.0*samples_per_frame/bandwidth
    print tb
    print bandwidth
    
    self.tx_parameters = {'carrier_frequency':tx_freq/1e9,'fft_size':fft_length, 'cp_size':cp_length \
                          , 'subcarrier_spacing':bandwidth/fft_length/1e3 \
                          ,'data_subcarriers':subcarriers, 'bandwidth':bandwidth/1e6 \
                          , 'frame_length':frame_length  \
                          , 'symbol_time':1.0*(cp_length + fft_length)/bandwidth*1e6, 'max_data_rate':(bits/tb)/1e6}  
    
    #path1 = eval(comm1)
    #path2 = eval(comm2)
    
    self.rpc_mgr_tx = zeromq.rpc_manager()
    self.rpc_mgr_tx.set_reply_socket("tcp://*:6660")
    self.rpc_mgr_tx.start_watcher()
    self.rpc_mgr_tx.add_interface("get_tx_parameters",self.get_tx_parameters)

  def get_tx_parameters(self):
     return self.tx_parameters
 
  def add_tx_ampl_interface(self,comm1):
     self.rpc_mgr_tx.add_interface("set_amplitude",comm1) #self.txpath.set_rms_amplitude
  def add_tx_modulation_interface(self,comm2):
     self.rpc_mgr_tx.add_interface("set_modulation",comm2) #self.txpath.allocation_src.set_allocation
     
  def add_tx_freq_offset__interface(self,comm1):
     self.rpc_mgr_tx.add_interface("set_freq_offset",comm3)#self.freq_off.set_freqoff
  def add_tx_channel_profile_interface(self,comm2):
     self.rpc_mgr_tx.add_interface("set_channel_profile",comm5)  #   self.fad_chan.set_channel_profile