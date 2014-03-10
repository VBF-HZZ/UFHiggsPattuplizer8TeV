#!/bin/bash

if [[ "$1" == "" ]]; then 
    echo "Please pass a Submission directory!"
    exit 1;
fi


for d in $1/*/crab_*
  do
  
  crab -c $d -report
  lumiCalc2.py overview -i $d/res/lumiSummary.json >& $d/lumiSummary.txt
  
  cat $d/lumiSummary.txt

done
