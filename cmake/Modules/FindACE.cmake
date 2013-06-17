set( ACE_FOUND 0 )
if ( UNIX )
  FIND_PATH( ACE_INCLUDE_DIR
    NAMES
      ace/ACE.h
    PATHS
      /usr/include
      /usr/include/ace
      /usr/local/include
      /usr/local/include/ace
      ${ACE_ROOT}
      ${ACE_ROOT}/include
      $ENV{ACE_ROOT}
      $ENV{ACE_ROOT}/include
      # ${CMAKE_SOURCE_DIR}/dep/ACE_wrappers
  DOC
    "Specify include-directories that might contain ace.h here."
  )
  FIND_LIBRARY( ACE_LIBRARIES
    NAMES
      ace ACE
    PATHS
      /usr/lib
      /usr/lib/ace
      /usr/lib/ace/lib
      /usr/local/lib
      /usr/local/lib/ace
      /usr/local/ace/lib
      ${ACE_ROOT}
      ${ACE_ROOT}/lib
      $ENV{ACE_ROOT}/lib
      $ENV{ACE_ROOT}
    DOC "Specify library-locations that might contain the ACE library here."
  )

#  FIND_LIBRARY( ACE_EXTRA_LIBRARIES
#    NAMES
#      z zlib
#    PATHS
#      /usr/lib
#      /usr/local/lib
#    DOC
#      "if more libraries are necessary to link into ACE, specify them here."
#  )

  if ( ACE_LIBRARIES )
    if ( ACE_INCLUDE_DIR )
      set( ACE_FOUND 1 )
      message( STATUS "Found ACE library: ${ACE_LIBRARIES}")
      message( STATUS "Found ACE headers: ${ACE_INCLUDE_DIR}")
    else ( ACE_INCLUDE_DIR )
      message(FATAL_ERROR "Could not find ACE headers! Please install ACE libraries and headers")
    endif ( ACE_INCLUDE_DIR )
  endif ( ACE_LIBRARIES )

  mark_as_advanced( ACE_FOUND ACE_LIBRARIES ACE_EXTRA_LIBRARIES ACE_INCLUDE_DIR )
endif (UNIX)