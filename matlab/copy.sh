#!/bin/bash
STRING="Done!"
#print
COPYFROM=~/fbmcdata__*.dat
COPYTO=$PWD
mv $COPYFROM $COPYTO
echo $STRING