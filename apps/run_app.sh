#!/bin/sh
export LD_LIBRARY_PATH=$PWD/../build/lib
export PYTHONPATH=$PWD/../build/swig
echo $PYTHONPATH
/usr/bin/python $1
