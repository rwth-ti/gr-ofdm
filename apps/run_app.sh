#!/bin/sh
export LD_LIBRARY_PATH="$PWD/../build/lib:/home/zivkovic/git/gr-zmqblocks/build/lib"
export PYTHONPATH="$PWD/../build/swig:$PWD/../python:/home/zivkovic/git/gr-zmqblocks/build/swig:/home/zivkovic/git/gr-zmqblocks/python"
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
