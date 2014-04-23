#!/bin/bash
files=(/home/mme{1..12}/resetaccount)
echo "write resetaccount to home directories:"
for file in ${files[*]}
do
    echo $file
    touch $file
done
