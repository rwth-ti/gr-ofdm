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
#CMAKE_POLICY( SET CMP0003 OLD )
#include(GrPlatform) #define LIB_SUFFIX

FIND_PACKAGE (Qt4 REQUIRED)

ADD_DEFINITIONS (${QT_DEFINITIONS})

SET( QT_USE_QTXML TRUE )
SET( QT_USE_QTOPENGL TRUE )
SET( QT_WRAP_CPP TRUE )

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

SET ( UI_sources
  ${CMAKE_CURRENT_SOURCE_DIR}/widgets/widget_device_info.ui
  ${CMAKE_CURRENT_SOURCE_DIR}/widgets/rx_performance.ui
  ${CMAKE_CURRENT_SOURCE_DIR}/widgets/scatter_ctrl.ui
  ${CMAKE_CURRENT_SOURCE_DIR}/widgets/pa_ctrl.ui
  ${CMAKE_CURRENT_SOURCE_DIR}/widgets/tx_ctrl.ui
  ${CMAKE_CURRENT_SOURCE_DIR}/gnuradio_qtgui.ui
)

QT4_WRAP_UI ( UI_headers ${UI_sources})


SET ( MOC_sources
  ${CMAKE_CURRENT_SOURCE_DIR}/widgets/widget_barplot.h
  #${CMAKE_CURRENT_SOURCE_DIR}/widgets/widget_complexplot.h
  ${CMAKE_CURRENT_SOURCE_DIR}/widgets/widget_device_info.h
  ${CMAKE_CURRENT_SOURCE_DIR}/widgets/widget_lineplot.h
  ${CMAKE_CURRENT_SOURCE_DIR}/widgets/widget_pa_ctrl.h
  ${CMAKE_CURRENT_SOURCE_DIR}/widgets/widget_rx_performance.h
  ${CMAKE_CURRENT_SOURCE_DIR}/widgets/widget_scatter_ctrl.h
  ${CMAKE_CURRENT_SOURCE_DIR}/widgets/widget_scatterplot.h
  ${CMAKE_CURRENT_SOURCE_DIR}/widgets/widget_tx_ctrl.h
  ${CMAKE_CURRENT_SOURCE_DIR}/gui_tx.h
  ${CMAKE_CURRENT_SOURCE_DIR}/gui_rx.h
  ${CMAKE_CURRENT_SOURCE_DIR}/gui_rxsinr.h
  ${CMAKE_CURRENT_SOURCE_DIR}/gnuradio_qtgui.h
)
	
QT4_WRAP_CPP ( MOC_headers ${MOC_sources} )

SET ( App_sources
    ${CMAKE_CURRENT_SOURCE_DIR}/main.cc 
    ${CMAKE_CURRENT_SOURCE_DIR}/ListElement.h 
    ##${CMAKE_CURRENT_SOURCE_DIR}/gui_tx.h 
    ${CMAKE_CURRENT_SOURCE_DIR}/gui_tx.cc 
    ##${CMAKE_CURRENT_SOURCE_DIR}/gui_rx.h 
    ${CMAKE_CURRENT_SOURCE_DIR}/gui_rx.cc 
    ##${CMAKE_CURRENT_SOURCE_DIR}/gui_rxsinr.h 
    ${CMAKE_CURRENT_SOURCE_DIR}/gui_rxsinr.cc 
    ${CMAKE_CURRENT_SOURCE_DIR}/analyse.h 
    ${CMAKE_CURRENT_SOURCE_DIR}/interface/IF/IF_transmission_data.h 
    ${CMAKE_CURRENT_SOURCE_DIR}/widgets/WidgetControl.h 
    ##${CMAKE_CURRENT_SOURCE_DIR}/generateData.h 
    ##${CMAKE_CURRENT_SOURCE_DIR}/widgets/widget_lineplot.h 
    ##${CMAKE_CURRENT_SOURCE_DIR}/widgets/widget_barplot.h 
    ##${CMAKE_CURRENT_SOURCE_DIR}/widgets/widget_scatterplot.h 
    ${CMAKE_CURRENT_SOURCE_DIR}/interface/IF/IF_scalar_complex.h 
    ${CMAKE_CURRENT_SOURCE_DIR}/interface/IF/IF_scalar_float.h 
    ${CMAKE_CURRENT_SOURCE_DIR}/interface/IF/IF_scalar_int.h 
    ${CMAKE_CURRENT_SOURCE_DIR}/interface/IF/IF_vector_complex.h 
    ${CMAKE_CURRENT_SOURCE_DIR}/interface/IF/IF_vector_float.h 
    ${CMAKE_CURRENT_SOURCE_DIR}/interface/IF/IF_vector_int.h 
    ${CMAKE_CURRENT_SOURCE_DIR}/interface/IF/IF_rx_performance.h 
    ${CMAKE_CURRENT_SOURCE_DIR}/interface/IF/IF_power_control.h 
    ${CMAKE_CURRENT_SOURCE_DIR}/interface/IF/IF_scatter_control.h 
    ${CMAKE_CURRENT_SOURCE_DIR}/interface/IF/IF_tx_control.h 
    ${CMAKE_CURRENT_SOURCE_DIR}/interface/IF_ident.h 
    ${CMAKE_CURRENT_SOURCE_DIR}/interface/broker.h
    ${CMAKE_CURRENT_SOURCE_DIR}/interface/interface.h 
    ${CMAKE_CURRENT_SOURCE_DIR}/interface/types.h 
    ${CMAKE_CURRENT_SOURCE_DIR}/interface/unique_id.h 
    ${CMAKE_CURRENT_SOURCE_DIR}/gnuradio_qtgui.h 
    ${CMAKE_CURRENT_SOURCE_DIR}/widgets/widget_lineplot.cc
    #${CMAKE_CURRENT_SOURCE_DIR}/widgets/widget_complexplot.cc
    ${CMAKE_CURRENT_SOURCE_DIR}/widgets/widget_barplot.cc 
    ${CMAKE_CURRENT_SOURCE_DIR}/widgets/widget_scatterplot.cc 
    ##${CMAKE_CURRENT_SOURCE_DIR}/widgets/widget_rx_performance.h 
    ${CMAKE_CURRENT_SOURCE_DIR}/widgets/widget_rx_performance.cc 
    ##${CMAKE_CURRENT_SOURCE_DIR}/widgets/widget_pa_ctrl.h 
    ${CMAKE_CURRENT_SOURCE_DIR}/widgets/widget_pa_ctrl.cc 
    ##${CMAKE_CURRENT_SOURCE_DIR}/widgets/widget_tx_ctrl.h 
    ${CMAKE_CURRENT_SOURCE_DIR}/widgets/widget_tx_ctrl.cc 
    ##${CMAKE_CURRENT_SOURCE_DIR}/widgets/widget_scatter_ctrl.h 
    ${CMAKE_CURRENT_SOURCE_DIR}/widgets/widget_scatter_ctrl.cc 
    ##${CMAKE_CURRENT_SOURCE_DIR}/gnuradio_qtgui.cc 
    ${CMAKE_CURRENT_SOURCE_DIR}/interface/broker.cc 
    ${CMAKE_CURRENT_SOURCE_DIR}/viewWidget.cc 
    ${CMAKE_CURRENT_SOURCE_DIR}/viewWidget.h 
    ${CMAKE_CURRENT_SOURCE_DIR}/widgets/widget_device_info.cc 
    ${CMAKE_CURRENT_SOURCE_DIR}/interface/corba_push_consumer.h 
    ${CMAKE_CURRENT_SOURCE_DIR}/interface/corba_push_consumer.cc 
    ${CMAKE_CURRENT_SOURCE_DIR}/interface/corba_push_consumer_rx.h 
    ${CMAKE_CURRENT_SOURCE_DIR}/interface/corba_push_consumer_rx.cc 
    ${CMAKE_CURRENT_SOURCE_DIR}/interface/corba_push_consumer_rxbas.h 
    ${CMAKE_CURRENT_SOURCE_DIR}/interface/corba_push_consumer_rxbas.cc 
    ${CMAKE_CURRENT_SOURCE_DIR}/interface/orb.h 
    ${CMAKE_CURRENT_SOURCE_DIR}/interface/orb.cc
)

#SET(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -fPIC"  )
#SET(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_DEBUG} -fPIC"  )

#QT4_AUTOMOC(${App_sources})


#ADD_LIBRARY(dummy SHARED
 #  			)
   
#TARGET_LINK_LIBRARIES(dummy
 #   ${ACE_LIBRARIES}
    
 #   )
 
 link_directories(
    ${Boost_LIBRARY_DIRS}
    ${GRUEL_LIBRARY_DIRS}
    ${GNURADIO_CORE_LIBRARY_DIRS}
    /usr/lib
    ${CMAKE_BINARY_DIR}/tao_skeleton
    #${TAO_LIBRARIES}
    #${ACE_LIBRARIES}
)
   


 
add_executable ( qtgui 
  ${App_sources}
  ${MOC_headers}
  ${UI_headers}
)

#SET (tao_ofdmti -Wl,-whole-archive ${CMAKE_BINARY_DIR}/tao_skeleton/libtao_ofdmti.a -Wl,-no_whole-archive)

SET(CMAKE_EXE_LINKER_FLAGS -shared)
 
SET(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -fPIC"  )
SET(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_DEBUG} -fPIC"  )

add_dependencies(tao_ofdmti ACE boost_system)  

target_link_libraries(qtgui 
${CMAKE_THREAD_LIBS_INIT}
 #/usr/lib/libboost_system.so

    /usr/lib/libboost_system.so
    ${Boost_LIBRARIES}
    ${QT_LIBRARIES}
    ${GL_LIBRARIES}
    ${QWT_LIBRARIES}
    ${GRUEL_LIBRARIES}
    ${GNURADIO_CORE_LIBRARIES}
    
    /usr/lib/libTAO_AnyTypeCode.so
    /usr/lib/libACE.so
    
    #${ITPP_LIBRARIES}
    
    #${ACE_LIBRARIES}
    #/usr/lib/libTAO_AnyTypeCode.so
    #/usr/lib/libACE.so
   # ${CMAKE_BINARY_DIR}/qt/gui/libdummy.so
    ${TAO_LIBRARIES}
    
    #${ACE_LIBRARIES}
    #/usr/lib/ace/lib/libACE.so
    
   
    
    
    ${CMAKE_THREAD_LIBS_INIT}
     "-Wl,--whole-archive"
     ${CMAKE_BINARY_DIR}/tao_skeleton/libtao_ofdmti.a
      "-Wl,--no-whole-archive"
      
      
    #${CMAKE_BINARY_DIR}/tao_skeleton/libtao_ofdmti.a
    #/usr/lib/libTAO_AnyTypeCode.so
    #/usr/lib/libboost_system.so
        
    )
    
    #SET(CMAKE_EXE_LINKER_FLAGS -static)
    #
#
    # ${CMAKE_BINARY_DIR}/tao_skeleton/libtao_ofdmti.a
 
  #  )
    
add_dependencies(qtgui tao_ofdmti) 
  #add_dependencies(tao_ofdmti ACE boost_system)  
    
 

    message(STATUS "GNURADIO_CORE_LIBRARIES at: ${GNURADIO_CORE_LIBRARIES}")
     message(STATUS "GRUEL_LIBRARIESat: ${GRUEL_LIBRARIES}")
    message(STATUS "LIBTAO_OFDMTI at: ${CMAKE_BINARY_DIR}/tao_skeleton/libtao_ofdmti.a")
    message(STATUS "TAO_LIBRARIES at: ${TAO_LIBRARIES}")
    message(STATUS "ACE_LIBRARIES at: ${ACE_LIBRARIES}")
    message(STATUS "QWT_LIBRARIES at: ${QWT_LIBRARIES}")
    message(STATUS "QT_LIBRARIES at: ${QT_LIBRARIES}")

#set_target_properties(qtgui PROPERTIES DEFINE_SYMBOL "qtgui2")

