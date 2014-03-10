#!/bin/bash

if [[ "$1" == "" ]]; then echo "Please pass a Submission directory!"; exit 1; fi;

cd ${1}

for f in $(ls .)
  do

  MASS=$f
  cd $MASS || exit 1
  ls crab_* > /dev/null 2>&1 || exit 0;
  
  for d in crab_*; do 
      crab -c $d -status >& /dev/null
      crab -c $d -status -get >& /dev/null
      crab -c $d -status 2>&1 | tee status.$d;    

      if grep -q 'Created' status.$d; then crab -c $d -submit; fi;
      if grep -q 'Done\|DONE\|Terminated' status.$d; then crab -c $d -get; fi;
      if grep -q 'Aborted' status.$d; then 
	  read -t7 -n1 -r -p "pausing..." key; echo;
	  crab -c $d $(perl -e '
    @a=();
    while(<>){
        ($j,$e) = m/^(\d+)\s+\S+\s+(?:Aborted|Done)\s+Aborted(\s+\S+?\.(\S+))?/ or next;
        push @a,$j; 
    }
    print "-forceResubmit " . join(",",@a) . "\n"' status.$d);
      fi;
      if grep -q 'Cancelled' status.$d; then 
	  read -t7 -n1 -r -p "pausing..." key; echo;
	  crab -c $d $(perl -e '
    @a=();
    while(<>){
        ($j,$e) = m/^(\d+)\s+\S+\s+(?:Cancelled)\s+SubSuccess(\s+\S+?\.(\S+))?/ or next;
        push @a,$j; 
    }
    print "-forceResubmit " . join(",",@a) . "\n"' status.$d);
      fi;

      if grep -q 'CannotSubmit' status.$d; then 
	  crab -c $d $(perl -e '
    @a=(); 
    while(<>){ 
        ($j,$e,$s) = m/^(\d+)\s+(?:CannotSubmit)+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+/  or next; 
        push @a,$j; 
    } 
    print "-resubmit " . join(",",@a) . "\n"' status.$d);
      fi;
      
      if grep -q '60317\|8001\|8002\|60307\|8003\|8020\|8021\|60318\|70500\|10034\|8028\|10020\|10030\|10016\|50115\| 6 \| 9 \| -1 \|60308' status.$d; then
	  read -t7 -n1 -r -p "pausing..." key; echo;
	  crab -c $d $(perl -e '
    @a=();
    while(<>){
        ($j,$e) = m/^(\d+)\s+\S+\s+\S+\s+\S+\s+\S+\s+(?:60317|8001|8002|60307|7|9|8003|8020|8021|8028|60318|70500|10034|10020|10030|10016|50115| 9 | 6 | -1 |60308)\s+\S+/  or next;
        push @a,$j; 
    }
    print "-resubmit " . join(",",@a) . "  \n"' status.$d);
      fi;
      if grep -q '50117' status.$d; then
	  read -t7 -n1 -r -p "pausing..." key; echo;
	  crab -c $d $(perl -e '
    @a=();
    while(<>){
        ($j,$e) = m/^(\d+)\s+\S+\s+\S+\s+\S+\s+\S+\s+(?:50117)\s+\S+/  or next;
        push @a,$j; 
    }
    print "-forceResubmit " . join(",",@a) . "\n"' status.$d);
      fi;

  done

cd ../
  
done