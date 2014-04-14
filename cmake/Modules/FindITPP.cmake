# - Find ITPP
# Find the native ITPP includes and library
# This module defines
#  ITPP_INCLUDE_DIR, where to find itpp/itbase.h, etc.
#  ITPP_LIBRARIES, the libraries needed to use ITPP.
#  ITPP_FOUND, If false, do not try to use ITPP.
# also defined, but not for general use are
#  ITPP_LIBRARY, where to find the ITPP library.

#MESSAGE("ITPP_DIR set to ${ITPP_DIR}" )

FIND_PATH(ITPP_INCLUDE_DIR itpp/itbase.h
    ${ITPP_DIR}
    /usr/pkgs64/include
    /usr/include
    NO_DEFAULT_PATH
    )

FIND_LIBRARY(ITPP_LIBRARY
    NAMES itpp #itpp_debug
    PATHS ${ITPP_DIR}/libs
    ${ITPP_DIR}/itpp/.libs/
    "${ITPP_DIR}\\win32\\lib"
    /usr/lib/x86_64-linux-gnu
    /usr/pkgs64/lib
    /usr/lib64
    /usr/lib
    NO_DEFAULT_PATH
    )

IF (ITPP_LIBRARY AND ITPP_INCLUDE_DIR)
    SET(ITPP_LIBRARIES ${ITPP_LIBRARY})
    SET(ITPP_FOUND "YES")
ELSE (ITPP_LIBRARY AND ITPP_INCLUDE_DIR)
    SET(ITPP_FOUND "NO")
ENDIF (ITPP_LIBRARY AND ITPP_INCLUDE_DIR)


IF (ITPP_FOUND)
    IF (NOT ITPP_FIND_QUIETLY)
        MESSAGE(STATUS "Found ITPP: ${ITPP_LIBRARIES}")
	MESSAGE(STATUS "Found ITPP include dir : ${ITPP_INCLUDE_DIR}")
    ENDIF (NOT ITPP_FIND_QUIETLY)
ELSE (ITPP_FOUND)
    IF (ITPP_FIND_REQUIRED)
        MESSAGE(FATAL_ERROR "Could not find ITPP library")
    ENDIF (ITPP_FIND_REQUIRED)
ENDIF (ITPP_FOUND)

# Deprecated declarations.
GET_FILENAME_COMPONENT (NATIVE_ITPP_LIB_PATH ${ITPP_LIBRARY} PATH)

MARK_AS_ADVANCED(
    ITPP_LIBRARY
    ITPP_INCLUDE_DIR
    )
