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
# Setup library
########################################################################
#include(GrPlatform) #define LIB_SUFFIX

FIND_PACKAGE (Qt4 REQUIRED)
#FIND_PACKAGE (GL REQUIRED)
find_package (Threads)

ADD_DEFINITIONS (${QT_DEFINITIONS})

SET( QT_USE_QTXML TRUE )
SET( QT_USE_QTOPENGL TRUE )
SET( QT_USE_GL TRUE )
SET( QT_WRAP_CPP TRUE )
SET( QT_USE_QTNETWORK TRUE )
SET( QT_USE_PTHREAD TRUE )

INCLUDE (${QT_USE_FILE})

include_directories(
    ${CMAKE_CURRENT_BINARY_DIR}
    ${CMAKE_BINARY_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/interface
    ${CMAKE_SOURCE_DIR}/include
    ${CMAKE_SOURCE_DIR}
    ${Boost_INCLUDE_DIRS}
    ${TAO_INCLUDE_DIR}/tao
    ${TAO_INCLUDE_DIR}/orbsvc
    ${ACE_INCLUDE_DIR}/ace
    ${ACE_INCLUDE_DIR}}
    ${TAO_INCLUDE_DIR}
    ${QWT_INCLUDE_DIRS}
    ${QT_INCLUDE_DIRS}
    #${TAO_UTILS_INCLUDEDIR}/tao
    #${TAO_COSNAMING_INCLUDEDIR}/orbsvc
)




SET ( MOC_sources
  ${CMAKE_CURRENT_SOURCE_DIR}/CGLScatter.h
  ${CMAKE_CURRENT_SOURCE_DIR}/MainApp.h
)
	
QT4_WRAP_CPP ( MOC_headers ${MOC_sources} )

SET ( App_sources
    ${CMAKE_CURRENT_SOURCE_DIR}/main.cc 
    ${CMAKE_CURRENT_SOURCE_DIR}/MainApp.cc
    ${CMAKE_CURRENT_SOURCE_DIR}/CGLScatter.cc
    ${CMAKE_SOURCE_DIR}/lib/util_ipc.cc
)


add_executable ( scatterplot-gui
  ${App_sources}
  ${MOC_headers}
)



target_link_libraries(scatterplot-gui 
    ${Boost_LIBRARIES}
    /usr/lib/libboost_system.so
    ${QT_LIBRARIES}
    ${GL_LIBRARIES}
    ${CMAKE_THREAD_LIBS_INIT}
    /usr/lib/x86_64-linux-gnu/librt.so
    ${GRUEL_LIBRARIES}
    )
    

    
    
  #add_dependencies(qtgui tao_ofdmti)

    #message(STATUS "GNURADIO_CORE_LIBRARIES at: ${GNURADIO_CORE_LIBRARIES}")
    # message(STATUS "GRUEL_LIBRARIESat: ${GRUEL_LIBRARIES}")
    #message(STATUS "LIBTAO_OFDMTI at: ${CMAKE_BINARY_DIR}/tao_skeleton/libtao_ofdmti.a")
    #message(STATUS "TAO_LIBRARIES at: ${TAO_LIBRARIES}")
   message(STATUS "Boost_LIBRARIES at: ${Boost_LIBRARIES}")
    message(STATUS "QWT_LIBRARIES at: ${QWT_LIBRARIES}")
    message(STATUS "QT_LIBRARIES at: ${QT_LIBRARIES}")
    message(STATUS "CMAKE_THREAD_LIBS_INIT at: ${CMAKE_THREAD_LIBS_INIT}")

#set_target_properties(qtgui PROPERTIES DEFINE_SYMBOL "qtgui2")

