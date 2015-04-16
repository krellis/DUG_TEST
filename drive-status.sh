#!/bin/bash

clear

for i in {0..5}
do
  echo ""
  echo "DRIVE $i (/dev/dst$i)============================================================="
  #echo "DRIVE $i (/dev/dst$i)_____________________________________________________________"
  mt -f /dev/dst$i status
done

echo ""
