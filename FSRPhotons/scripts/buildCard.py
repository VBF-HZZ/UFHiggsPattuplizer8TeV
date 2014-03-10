#!/usr/bin/env python

import getopt, os, sys
from ROOT import TFile

seperator = '------------------------------------------------------------------------------------------------'

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "n:s:c:l:i:e:h",
                                  ["nuissences=",
                                   "help"])

    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(1)

    nuissFile = "nuissances.txt"
    for o, a in opts:
        if o in ('-n','--thumb-dir'):
            nuissFile = str(a)
        elif o in ("-h", "--help"):
            usage()
            sys.exit(0)
        else:
            assert False, "unhandled option"

    #Make sure we have an input file
    if len(args) < 1:
        usage()
        print 'Error: Not enough arguments! Need input root file with histograms'
        sys.exit(2)

    # grab the nuissance parameters and set
    # the kmax to # of params
    allNuiss = getNuissances(nuissFile)
    kmax = len(allNuiss['type'])
    
    # grab the file from the system and retrieve keys
    histFile = TFile(args[0])
    keys = [key.GetName() for key in histFile.GetListOfKeys()]

    # check to make sure all the keys have nuissance 
    # parameters associated and set jmax to the number of
    # 'background' samples
    # currently assuming that the signal is the 0th key FIXME
    for x in keys:
        if x not in allNuiss:
            print 'Error: No nuissance parameters defined for {0} .. exiting'.format(x)
            exit(4)
    jmax = len(keys)-1

    # check how many bins we have, i.e. how many channesl
    # and ensure that each hist has the same #
    # then set imax to the number of 'channels'
    nbins = histFile.Get(keys[0]).GetNbinsX()
    for key in keys[1:]:
        if nbins != histFile.Get(key).GetNbinsX():
            print 'Error: Histograms should all be the same size ... exiting'
            exit(5)
    imax = nbins


    cardFile = open(args[0].replace('.root','.txt'),'w')
    print >> cardFile, 'imax {0} number of channels'.format(imax)
    print >> cardFile, 'jmax {0} number of background'.format(jmax)
    print >> cardFile, 'kmax {0} number of nuisance parameters'.format(kmax)
    print >> cardFile, seperator

    print >> cardFile, '{0:<10}'.format('bin'),
    for i in range(0,imax):
        for j in range(0,jmax+1):
            print >> cardFile, '{0:^10}'.format(i+1),
    print >> cardFile

    print >> cardFile, '{0:<10}'.format('process'),
    for i in range(0,imax):
        for j in range(0,jmax+1):
            print >> cardFile, '{0:^10}'.format(keys[j]),
    print >> cardFile

    print >> cardFile, '{0:<10}'.format('process'),
    for i in range(0,imax):
        for j in range(0,jmax+1):
            print >> cardFile, '{0:^10}'.format(j),
    print >> cardFile

    print >> cardFile, '{0:<10}'.format('rate'),
    for i in range(0,imax):
        for j in range(0,jmax+1):
            print >> cardFile, '{0:^10}'.format(histFile.Get(keys[j]).GetBinContent(i+1)),
    print >> cardFile

    print >> cardFile, seperator
    for k in range(0,kmax):
        print >> cardFile, '{0:<4}{1:<6}'.format(k+1,allNuiss['type'][k]),
        for i in range(0,imax):
            for key in keys:
                print >> cardFile, '{0:^10}'.format(allNuiss[key][k]),
#                 print >> cardFile, '{0:^10}'.format(key),
        print >> cardFile

    cardFile.close()





def getNuissances(fn):
    f = open(fn,'r')
    lines = f.readlines()
    title = lines[0].split()
    if title[0] != "type" or len(title) < 2:
        print 'Error: invalid nuissance file, check {0} for correctness'.format(fn)
        sys.exit(3)

    samples = []
    nuissances = []
    for sample in title[1:]:
        samples.append(sample)
        nuissances.append([])

    types = []
    for line in lines[1:]:
        words = line.split()
        types.append(words[0])
        for i in range(1,len(words)):
            nuissances[i-1].append(words[i])

    allNuiss = dict(zip(samples,nuissances))
    allNuiss['type'] = types
    return allNuiss


def usage():
    print """

./buildCard.py [OPTIONS] rootFile 

Options:

    -h, --help          this message
    -n, --nuissance     text file with corresponding list of \033[01;31mnuissance\033[00m parameters

    """

if __name__ == "__main__":
    main()
 
