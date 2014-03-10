#!/bin/bash

if [[ "$1" == "" ]]; then
    echo "Please pass a JSON file to check!"
    exit 1;
fi




#lumiCalc2.py -c frontier://LumiCalc/CMS_LUMI_PROD -i $1 overview -b stable --norm pp8TeV

lumiCalc2.py overview -i $1 -b stable 

