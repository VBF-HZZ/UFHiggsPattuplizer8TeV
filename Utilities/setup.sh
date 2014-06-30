#!/bin/sh

source /afs/cern.ch/cms/LCG/LCG-2/UI/cms_ui_env.sh
eval `scramv1 runtime -sh`
source /afs/cern.ch/cms/ccs/wm/scripts/Crab/crab.sh
voms-proxy-init -voms cms -hours 192 -valid 192:00
