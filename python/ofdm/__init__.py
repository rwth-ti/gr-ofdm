#
# Copyright 2008,2009 Free Software Foundation, Inc.
#
# This application is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This application is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

# The presence of this file turns this directory into a Python package

'''
This is the GNU Radio OFDM module. Place your Python package
description here (python/__init__.py).
'''

# ----------------------------------------------------------------
# Temporary workaround for ticket:181 (swig+python problem)
import sys
_RTLD_GLOBAL = 0
try:
    from dl import RTLD_GLOBAL as _RTLD_GLOBAL
except ImportError:
    try:
	from DLFCN import RTLD_GLOBAL as _RTLD_GLOBAL
    except ImportError:
	pass

if _RTLD_GLOBAL != 0:
    _dlopenflags = sys.getdlopenflags()
    sys.setdlopenflags(_dlopenflags|_RTLD_GLOBAL)
# ----------------------------------------------------------------


# import swig generated symbols into the ofdm namespace
from ofdm_swig import *

# import any pure python here
from fbmc_insert_preamble_vcvc import fbmc_insert_preamble_vcvc
from fbmc_overlapping_parallel_to_serial_vcc import fbmc_overlapping_parallel_to_serial_vcc
from fbmc_overlapping_serial_to_parallel_cvc import fbmc_overlapping_serial_to_parallel_cvc
from fbmc_vector_reshape_vcvc import fbmc_vector_reshape_vcvc
from fbmc_remove_preamble_vcvc import fbmc_remove_preamble_vcvc
from fbmc_channel_hier_cc import fbmc_channel_hier_cc
from fbmc_receiver_hier_cb import fbmc_receiver_hier_cb
from fbmc_transmitter_hier_bc import fbmc_transmitter_hier_bc
from fbmc_symbol_estimation_vcb import fbmc_symbol_estimation_vcb
from fbmc_symbol_creation_bvc import fbmc_symbol_creation_bvc
from ber_reference_source_grc import ber_reference_source_grc
from ofdm_frame_sampler_grc import ofdm_frame_sampler
from fbmc_frame_sampler_grc import fbmc_frame_sampler
#

# ----------------------------------------------------------------
# Tail of workaround
if _RTLD_GLOBAL != 0:
    sys.setdlopenflags(_dlopenflags)      # Restore original flags
# ----------------------------------------------------------------
