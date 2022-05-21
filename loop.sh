#!/bin/bash

declare -a params=( "N" "Sd" "dd" "ff" "fx" "Wv" "Wn" "PPP" "TTm" "TTn" "TTd" "RR" )
declare -a cities=( "BER" "VIE" "LEI" "IBK" "ZUR" )

#for p in ${params[@]}; do
for c in ${cities[@]}; do
    #echo $c
    #python3 ap.py -p $p -c BER,VIE,IBK,LEI
    #python3 ap.py -p $p -c VIE
    #python3 ap.py -p $p
    python3 ap.py -c $c
done
