#!/bin/bash

if [[ "$1" == "" ]]; then
    echo "Please pass a JSON file to check!"
    exit 1;
fi




#pixelLumiCalc.py -c frontier://LumiCalc/CMS_LUMI_PROD -i $1 overview 


pixelLumiCalc.py overview -i $1 