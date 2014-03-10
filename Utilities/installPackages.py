#!/usr/bin/python
import sys, os, pwd, commands
import optparse, shlex


def parseOptions():
    
    usage = ('usage: %prog [options] datasetList\n'
             + '%prog -h for help')
    parser = optparse.OptionParser(usage)
    
    parser.add_option('-v', '--version',   dest='version', type='string', default="53X", help='CMSSW release version')
    parser.add_option('-f', '--file',   dest='file', type='string', default="packages_src.txt", help='package source list file')

    # store options and arguments as global variables
    global opt, args
    (opt, args) = parser.parse_args()

    if (opt.version != '53X' and opt.version != '52X' and opt.version != '42X'):
        print opt.version, " is not a possible version, please choose 53X, 52X, or 42X"
        sys.exit()

    if not os.path.exists(opt.file):
        print opt.file, " not found!"
        sys.exit()


def processCmd(cmd):
    print cmd
    status, output = commands.getstatusoutput(cmd)
    if status !=0:
        print 'Error in processing command:\n   ['+cmd+'] \nExiting...'
        sys.exit()
        
    
def installPackages():
    global opt

    parseOptions()
    
    for line in open(opt.file,'r'):
        f = line.split()
        if len(f) < 1: continue
        if f[0].startswith("#"): continue

        if len(f) == 2:
            cmd = 'cvs co -r '+f[0]+' '+f[1]
        if len(f) == 3:
            cmd = 'cvs co -r '+f[0]+' -d '+f[2]+' '+f[1]
        processCmd(cmd)

    cmd = 'cvs update -r1.6 PhysicsTools/PatAlgos/plugins/PATPFParticleProducer.cc'
    processCmd(cmd)
    cmd = 'cvs update -r1.8 PhysicsTools/PatAlgos/plugins/PATPFParticleProducer.h'
    processCmd(cmd)
    cmd = 'cvs update -r1.6 PhysicsTools/PatAlgos/plugins/PATCleaner.cc'
    processCmd(cmd)
    cmd = 'mv UFHZZSkim/PFMuons/plugins/MuonCleanerBySegments.cc UFHZZSkim/PFMuons/plugins/MuonCleanerBySegments.cc.old'
    processCmd(cmd)
    cmd = 'cd EgammaAnalysis/ElectronTools/data/; cat download.url | xargs wget; cd ../../../'
    processCmd(cmd)

    sys.exit()


if __name__ == "__main__":
    installPackages()
        
        



