#!/bin/sh

scramv1 project CMSSW CMSSW_5_3_9_patch3
cd CMSSW_5_3_9_patch3/src
eval `scramv1 runtime -sh`
git clone https://github.com/VBF-HZZ/UFHiggsPattuplizer8TeV.git
cd UFHiggsPattuplizer8TeV
git checkout -b testProd origin/testProd
cd ../
ln -s UFHiggsPattuplizer8TeV/Utilities/* ./
tar xvzf requiredPackages.tgz
scram b -j12
