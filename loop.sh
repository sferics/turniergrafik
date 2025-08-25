#!/bin/bash

# This script runs the Python script ap.py with different parameters and cities.
#declare -a params=( "N" "Sd" "dd" "ff" "fx" "Wv" "Wn" "PPP" "TTm" "TTn" "TTd" "RR" )
declare -a params=( "Sd1" "Sd24" )
# Uncomment the line below to run with all parameters
declare -a cities=( "BER" "VIE" "LEI" "IBK" "ZUR" )

# Uncomment the line below to run with all parameters
#for p in ${params[@]}; do
# For each parameter, run the script with all cities
for c in ${cities[@]}; do
    #echo $c
    #python3 turniergrafik.py -p $p -c BER,VIE,IBK,LEI
    #python3 turniergrafik.py -p $p -c VIE
    #python3 turniergrafik.py -p $p
    # Run the script with the current city
    python3 turniergrafik.py -c $c
done
