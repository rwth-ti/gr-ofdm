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

  


ADD_CUSTOM_COMMAND(OUTPUT ofdm_tiS.cpp  ofdm_tiS.h  ofdm_tiS.inl  ofdm_tiC.cpp ofdm_tiC.h ofdm_tiC.inl
    				COMMAND ${TAO_IDL_COMPILER} ${CMAKE_CURRENT_SOURCE_DIR}/ofdm_ti.idl
					)

#ADD_CUSTOM_TARGET(CompileIdl ALL
#    DEPENDS  ofdm_tiS.cpp  ofdm_tiS.h  ofdm_tiS.inl  ofdm_tiC.cpp 
#  ofdm_tiC.h ofdm_tiC.inl
#)

SET(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -fPIC"  )
SET(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_DEBUG} -fPIC"  )

ADD_LIBRARY(tao_ofdmti STATIC
              #[EXCLUDE_FROM_ALL]
              ofdm_tiS.cpp  ofdm_tiS.h  ofdm_tiC.cpp ofdm_tiC.h
   			)
   
TARGET_LINK_LIBRARIES(tao_ofdmti
    #${TAO_LIBRARIES}
    ${SKEL_LIBRARIES}
    
    )
    
     set_property(TARGET tao_ofdmti PROPERTY
                IMPORTED_LOCATION ${CMAKE_BINARY_DIR}/tao_skeleton/libtao_ofdmti.a)

########################################################################
# Install public header files
########################################################################
install(FILES
    ofdm_tiS.cpp 
    ofdm_tiS.h 
    ofdm_tiS.inl 
    ofdm_tiC.cpp 
    ofdm_tiC.h 
    ofdm_tiC.inl
    DESTINATION include/tao_skeleton
)
