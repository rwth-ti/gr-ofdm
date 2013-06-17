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

include(GrPython)
add_subdirectory(data)
if (NOT EXISTS  ${CMAKE_CURRENT_BINARY_DIR}/data/256qam_pipe)


ADD_CUSTOM_COMMAND(OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/data/256qam_pipe ${CMAKE_CURRENT_SOURCE_DIR}/data/128qam_pipe ${CMAKE_CURRENT_SOURCE_DIR}/data/64qam_pipe ${CMAKE_CURRENT_SOURCE_DIR}/data/32qam_pipe ${CMAKE_CURRENT_SOURCE_DIR}/data/16qam_pipe ${CMAKE_CURRENT_SOURCE_DIR}/data/8psk_pipe ${CMAKE_CURRENT_SOURCE_DIR}/data/qpsk_pipe ${CMAKE_CURRENT_SOURCE_DIR}/data/bpsk_pipe
    				COMMAND cd ${CMAKE_CURRENT_SOURCE_DIR} && /bin/sh  ${CMAKE_CURRENT_SOURCE_DIR}/create_fifos
					)
ADD_CUSTOM_TARGET(MakeFifo ALL
   DEPENDS  ${CMAKE_CURRENT_SOURCE_DIR}/data/256qam_pipe ${CMAKE_CURRENT_SOURCE_DIR}/data/128qam_pipe ${CMAKE_CURRENT_SOURCE_DIR}/data/64qam_pipe ${CMAKE_CURRENT_SOURCE_DIR}/data/32qam_pipe ${CMAKE_CURRENT_SOURCE_DIR}/data/16qam_pipe ${CMAKE_CURRENT_SOURCE_DIR}/data/8psk_pipe ${CMAKE_CURRENT_SOURCE_DIR}/data/qpsk_pipe ${CMAKE_CURRENT_SOURCE_DIR}/data/bpsk_pipe
)

endif()


GR_PYTHON_INSTALL(
    PROGRAMS
#   ofdm_template.py
    DESTINATION bin
)
