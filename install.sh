#!/bin/sh

scramv1 project CMSSW CMSSW_5_3_9_patch3
cd CMSSW_5_3_9_patch3/src
eval `scramv1 runtime -sh`
git remote add origin https://github.com/VBF-HZZ/UFHiggsPattuplizer8TeV.git
git fetch origin
git checkout testProd
ln -s UFHiggsPattuplizer8TeV/Utilities/* ./
#make sure you have 'export CVSROOT=":ext:<username>@lxplus5.cern.ch:/afs/cern.ch/user/c/cvscmssw/public/CMSSW"; export CVS_RSH=/usr/bin/ssh' in your .bash_profile
python installPackages.py
scram b -j12
