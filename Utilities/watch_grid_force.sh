#!/bin/bash

if [[ "$1" == "" ]]; then echo "Please pass a Submission directory!"; exit 1; fi;

cd ${1}

for f in $(ls .)
  do

  MASS=$f
  cd $MASS || exit 1
  ls crab_* > /dev/null 2>&1 || exit 0;
  
  for d in crab_*; do 
      test -L $d && continue;
      if echo $d | grep -q LSF && echo $HOSTNAME | grep -v -q lxplus; then continue; fi
      if test -f status.$d; then
	  if grep -q 'Waiting\|Submitted\|Ready\|Running\|RUN\|DONE\|Aborted\|Done\|Created' status.$d; then
	      crab -c $d -status 2>&1 | tee status.$d;    
	  elif [[ "$FORCE" == "1" ]]; then
	      crab -c $d -status 2>&1 | tee status.$d;    
	  elif grep -q 'Retrieved' status.$d; then
	      echo "Job $d is completed, nothing to do for it"
	  else
	      crab -c $d -status 2>&1 | tee status.$d;    
	  fi;
      else
	  crab -c $d -status 2>&1 | tee status.$d;
      fi 
      if grep -q 'Created' status.$d; then crab -c $d -submit; fi;
      if grep -q 'Done\|DONE\|Terminated' status.$d; then crab -c $d -get; fi;
#      if grep -q 'Terminated' status.$d; then crab -c $d -get; fi;
      if grep -q 'Aborted' status.$d; then 
	  crab -c $d $(perl -e '
    %bl=();@a=(); 
    while(<>){ 
        ($j,$e,$s) = m/^(\d+)\s+\S+\s+(?:Aborted|Done)\s+Aborted(\s+\S+?\.(\S+))?/ or next; 
        push @a,$j; 
        $bl{$s}=1 if $e;
    } 
    $blc = "";
    if (scalar(keys(%bl))) { $blc = " -GRID.ce_black_list  " . join(",", keys(%bl))  }
    print "-resubmit " . join(",",@a) . "\n"' status.$d);
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
      
      if grep -q '60317\|8001\|8002\|60307\|8003\|8020\|8021\|60318\|70500\|10034\|8028\|10020\|10030' status.$d; then
	  read -t7 -n1 -r -p "pausing..." key; echo;
	  crab -c $d $(perl -e '
    @a=();
    while(<>){
        ($j,$e) = m/^(\d+)\s+\S+\s+\S+\s+\S+\s+\S+\s+(?:60317|8001|8002|60307|7|9|8003|8020|8021|8028|60318|70500|10034|10020|10030)\s+\S+/  or next;
        push @a,$j; 
    }
    print "-forceResubmit " . join(",",@a) . " -GRID.ce_black_list T2_IT_Rome,cmsrm-ce01.roma1.infn.it,cmsrm-ce02.roma1.infn.it \n"' status.$d);
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