from gnuradio import zeromq
import math

class rx_rpc_manager():
  def __init__(self):
    self.rpc_mgr_rx = zeromq.rpc_manager()
    self.rpc_mgr_rx.set_reply_socket("tcp://*:5550")
    self.rpc_mgr_rx.start_watcher()
 
  def add_set_scatter_subcarrier_interface(self,comm1):
    self.rpc_mgr_rx.add_interface("set_scatter_subcarrier",comm1)
  