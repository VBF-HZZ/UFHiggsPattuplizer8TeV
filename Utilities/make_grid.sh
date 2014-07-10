#!/bin/bash

GO=0; if [[ "$1" == "--go" ]]; then GO=1; shift; fi


if [ -z "$1" ]; then 
    echo "Please pass an input directory!"
    exit 1;
fi

inputDir=$1; shift;


cd ${inputDir}

for d in $(ls .);
do
  echo $d
  cd $d
  n=$(ls -1 crab_* | wc -l)
  if [[ "$n" == "0" ]]; then
      if [[ "$GO" == "1" ]]; then crab -cfg crab.cfg -USER.ui_working_dir=crab_$d -create -submit ; 
      else crab -cfg crab.cfg -USER.ui_working_dir=crab_$d -create ;  fi
  fi
  cd ../

done

cd ../
