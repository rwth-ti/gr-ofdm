#!/bin/sh
export LD_LIBRARY_PATH=$PWD/../build/lib
export PYTHONPATH=$PWD/../build/swig
echo $PYTHONPATH

#/usr/bin/python $1

ok=yes
if ! $*
then
  ok=no
fi

if [ $ok = yes ]
then
  exit 0
else
  exit 1
fi


