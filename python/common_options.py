#!/usr/bin/env python

from gnuradio import eng_notation
from gnuradio.eng_option import eng_option
from optparse import OptionParser
import preambles

def_data_blocks_per_frame = 9

def add(normal,expert):
  expert.add_option("", "--data-blocks",
    type="intx", default=def_data_blocks_per_frame,
    help="set the number of data blocks per ofdm frame [default=%default]")

  normal.add_option("", "--fft-length",
    type="intx", default=512,
    help="set the number of FFT bins [default=%default]")
  expert.add_option("", "--subcarriers",
    type="intx", default=None,
    help="set the number of occupied FFT bins. Default: fft window size - Pilot Subcarriers")
  expert.add_option("", "--cp-length",
    type="intx", default=None,
    help="set the number of bits in the cyclic prefix. Default: 12.5% of fft window size")
  expert.add_option("", "--station-id",
    type="intx", default=None,
    help="unique station id")
  expert.add_option("", "--rx-station-id",
    type="intx", default=None,
    help="unique station id")

  expert.add_option("", "--nameservice-ip",
    type="string", default="tabur",
    help="Set IP address or hostname that hosts the CORBA NameService")
  expert.add_option("", "--nameservice-port",
    type="string", default="50001",
    help="Set access port to NameService")

  normal.add_option("-v", "--verbose", action="store_true", default=False)
  expert.add_option("", "--log",
    action="store_true", default=False,
    help="enable file logs [default=%default]")
  
  expert.add_option("", "--debug",
                    action="store_true", default=False,
                    help="Enable debugging mode [default=%default]")
  
  expert.add_option("", "--benchmark",
                    action="store_true", default=False,
                    help="settle the station id for benchmark_ofdm [default=%default]")

  preambles.default_block_header.add_options(normal,expert)

def defaults(options):
  # default values if parameters not set
  if options.subcarriers is None:
    options.subcarriers = options.fft_length-8 #TODO: pilot subcarrier number!!
  if options.cp_length is None:
    options.cp_length = int(options.fft_length/20)

def add_freq_option(parser):
  """
  Hackery that has the -f / --freq option set both tx_freq and rx_freq
  """
  def freq_callback(option, opt_str, value, parser):
      parser.values.rx_freq = value
      parser.values.tx_freq = value

  if not parser.has_option('--freq'):
      parser.add_option('-f', '--freq', type="eng_float",
                        action="callback", callback=freq_callback,
                        help="set Tx and/or Rx frequency to FREQ [default=%default]",
                        metavar="FREQ")

def add_subdev_option(parser):
  """
  Hackery that has the -f / --freq option set both tx_freq and rx_freq
  """
  def subdev_callback(option, opt_str, value, parser):
      parser.values.tx_subdev_spec = value
      parser.values.rx_subdev_spec = value

  if not parser.has_option('--subdev'):
      parser.add_option('-d', '--subdev', type="subdev", default=None,
                        action="callback", callback=subdev_callback,
                        help="select USRP Tx/Rx side A or B",
                        metavar="SUBDEV")

def common_tx_rx_usrp_options(normal,expert):
    add_freq_option(normal)
    add_subdev_option(normal)

    normal.add_option("", "--which-usrp", type="int", default=0,
                      help="select usrp box to use")
    expert.add_option("", "--bandwidth", type="eng_float", default='500k',
                      help="set total bandwidth. [default=%default]")
    normal.add_option("-v", "--verbose", action="store_true", default=False)
