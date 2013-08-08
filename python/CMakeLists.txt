# Copyright 2011 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.

########################################################################
# Include python install macros
########################################################################
include(GrPython)
if(NOT PYTHONINTERP_FOUND)
    return()
endif()

########################################################################
# Include ofdm_ti_idl
########################################################################
ADD_CUSTOM_COMMAND(OUTPUT corba_stubs/ofdm_ti_idl.py  corba_stubs/__init__.py  corba_stubs/ofdm_ti/__init__.py  corba_stubs/ofdm_ti__POA/__init__.py
    				COMMAND omniidl -bpython -Wbpackage=corba_stubs -C${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_SOURCE_DIR}/tao_skeleton/ofdm_ti.idl
					)
ADD_CUSTOM_TARGET(CompileIdl ALL
    DEPENDS  corba_stubs/ofdm_ti_idl.py  corba_stubs/__init__.py  corba_stubs/ofdm_ti/__init__.py  corba_stubs/ofdm_ti__POA/__init__.py 
)

########################################################################
# Install python sources
########################################################################
GR_PYTHON_INSTALL(
    FILES
    __init__.py
    test_channel_estimator.py
    DESTINATION ${GR_PYTHON_DIR}/ofdm
)
