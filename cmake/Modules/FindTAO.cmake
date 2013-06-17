set(TAO_FOUND FALSE)

find_path(TAO_INCLUDE_DIR tao/corba.h PATHS $ENV{ACE_ROOT} $ENV{TAO_ROOT} $ENV{TAO_ROOT}/include $ENV{ACE_ROOT}/include /usr/include NO_DEFAULT_PATH)
find_library(TAO_LIBRARY NAMES TAO TAOd PATHS $ENV{ACE_ROOT}/lib $ENV{TAO_ROOT}/lib /usr/lib NO_DEFAULT_PATH)
find_program(TAO_IDL_COMPILER "tao_idl" $ENV{TAO_ROOT}/bin $ENV{ACE_ROOT}/bin /usr/bin NO_DEFAULT_PATH)
message(STATUS "TAO include at: ${TAO_INCLUDE_DIR}")
message(STATUS "TAO lib at: ${TAO_LIBRARY}")
message(STATUS "tao_idl at: ${TAO_IDL_COMPILER}")

if(TAO_INCLUDE_DIR AND TAO_LIBRARY AND TAO_IDL_COMPILER)
  SET(TAO_FOUND TRUE)
endif(TAO_INCLUDE_DIR AND TAO_LIBRARY AND TAO_IDL_COMPILER)
#now let's search for parts of tao we need.

message(STATUS "TAO_FOUND: ${TAO_FOUND}")

GET_FILENAME_COMPONENT(TAO_LIBRARY_DIR ${TAO_LIBRARY} PATH)

set(TAO_LIBRARIES ${TAO_LIBRARY})

set(TAO_FIND_LIBS "Utils" "PortableServer"  "CosNaming" "CosNaming_Skel" 
    "CosEvent" "CosEvent_Skel" "AnyTypeCode"
    "ObjRefTemplate" 
    "CosNaming_Serv" "ImR_Client" "Svc_Utils"
    "Messaging" "PI" "CodecFactory" "Valuetype" "IORTable")
if(TAO_FOUND)
    foreach(LIBRARY ${TAO_FIND_LIBS})
        find_library(TAO_${LIBRARY}_LIB NAMES "TAO_${LIBRARY}" "TAO_${LIBRARY}d" ${TAO_LIBRARY} 
            PATHS $ENV{TAO_ROOT}/lib $ENV{ACE_ROOT}/lib /usr/lib NO_DEFAULT_PATH)
        if(TAO_${LIBRARY}_LIB)
          message(STATUS "${LIBRARY} found at: ${TAO_${LIBRARY}_LIB}")
          list(APPEND TAO_LIBRARIES ${TAO_${LIBRARY}_LIB})
        else(TAO_${LIBRARY}_LIB)
          set(TAO_FOUND FALSE)
        endif(TAO_${LIBRARY}_LIB)
    endforeach()
endif(TAO_FOUND)

message(STATUS "${TAO_LIBRARIES}")
message(STATUS "TAO_FOUND: ${TAO_FOUND}")



set(SKEL_LIBRARIES )

set(SKEL_FIND_LIBS  "CosNaming" "CosNaming_Skel" 
    "CosEvent" "CosEvent_Skel" )
if(TAO_FOUND)
    foreach(LIBRARY ${SKEL_FIND_LIBS})
        find_library(TAO_${LIBRARY}_LIB NAMES "TAO_${LIBRARY}" "TAO_${LIBRARY}d" ${TAO_LIBRARY} 
            PATHS $ENV{TAO_ROOT}/lib $ENV{ACE_ROOT}/lib /usr/lib NO_DEFAULT_PATH)
        if(TAO_${LIBRARY}_LIB)
          message(STATUS "${LIBRARY} found at: ${TAO_${LIBRARY}_LIB}")
          list(APPEND SKEL_LIBRARIES ${TAO_${LIBRARY}_LIB})
        else(TAO_${LIBRARY}_LIB)
          set(TAO_FOUND FALSE)
        endif(TAO_${LIBRARY}_LIB)
    endforeach()
endif(TAO_FOUND)

set(COS_LIBRARIES )

set(COS_FIND_LIBS "Utils" "PortableServer")
if(TAO_FOUND)
    foreach(LIBRARY ${COS_FIND_LIBS})
        find_library(TAO_${LIBRARY}_LIB NAMES "TAO_${LIBRARY}" "TAO_${LIBRARY}d" ${TAO_LIBRARY} 
            PATHS $ENV{TAO_ROOT}/lib $ENV{ACE_ROOT}/lib /usr/lib NO_DEFAULT_PATH)
        if(TAO_${LIBRARY}_LIB)
          message(STATUS "${LIBRARY} found at: ${TAO_${LIBRARY}_LIB}")
          list(APPEND COS_LIBRARIES ${TAO_${LIBRARY}_LIB})
        else(TAO_${LIBRARY}_LIB)
          set(TAO_FOUND FALSE)
        endif(TAO_${LIBRARY}_LIB)
    endforeach()
endif(TAO_FOUND)


message(STATUS "COS_LIBRARIES: ${COS_LIBRARIES}")
message(STATUS "SKEL_LIBRARIES: ${SKEL_LIBRARIES}")
message(STATUS "TAO_FOUND: ${TAO_FOUND}")