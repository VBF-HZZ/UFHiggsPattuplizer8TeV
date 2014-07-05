#!/usr/bin/python
#-----------------------------------------------
# Latest update: 2012.10.11
# More info: predrag.milenovic@cern.ch
#-----------------------------------------------
import sys, os, pwd, commands
import optparse, shlex


# define function for argument/options parsing
def parseOptions():

    usage = ('usage: %prog [options] datasetList\n'
             + '%prog -h for help')
    parser = optparse.OptionParser(usage)


    thePattuplizer="PatTuplizer_53X_src.py"
    theJson="Jan22ReReco_JSON.txt"
    theLumiCalc="lumiCheck_Jan22ReReco.txt"
    theRunPeriod="2012A"
    theDir="data/53X/Legacy/2012A"
    theUserName=pwd.getpwuid(os.getuid())[0]

    parser.add_option('-c', '--cfg',      dest='cfgFile',    type='string', default=thePattuplizer, help='Configuration file for the analysis.')
    parser.add_option('-j', '--json',     dest='JSON',       type='string', default=theJson, help='The name of the JSON file to be used. The file should be in the local "./JSONs" directory.')
    parser.add_option('-n', '--njobs',    dest='nJobs',      type='int',    default=500, help='Number of crab jobs.')
    parser.add_option('-p', '--joblumis', dest='lumisPerJob',type='int',    default=10, help='Number of lumi sections per job.')
    parser.add_option('-l', '--lumicalc', dest='lumiCalc',   type='string', default=theLumiCalc, help='Specify the lumiClac output file with runs and lumis.')
    parser.add_option('-r', '--runPeriod',dest='runPeriod',  type='string', default=theRunPeriod, help='Specify the run period (JanA_Jul1, JanA_Jul2, JanA_Aug, JanA_Oct, JanB or Custom). If runPeriod = Custom, you need to specify the "runMin" and "runMax" options.')
    parser.add_option(      '--runMin',   dest='runMin',     type='int',                    help='Specify the minimum run number if runPeriod = Custom.')
    parser.add_option(      '--runMax',   dest='runMax',     type='int',                    help='Specify the maximum run number if runPeriod = Custom.')
    parser.add_option('-d', '--t2dir',    dest='T2Dir',      type='string', default=theDir, help='Crab stage-out path at the T2 relative to the user directory.')
    parser.add_option('-t', '--tag',      dest='appendName', type='string', default="8TeV", help='Tag that will be appended to the file/dir names.')
    parser.add_option('-u', '--isuser',   dest='isUSER',     type='int',    default=0, help='Is it a user generated sample (User - 1, Official - 0)')
    parser.add_option('-m', '--ismc',     dest='isMC',       type='int',    default=0, help='Is it a MC sample (MC - 1, Data - 0).')
    parser.add_option('--up', '--userpath',     dest='UserName',       type='string',    default=theUserName, help='username in the T2 SE.')

    # store options and arguments as global variables
    global opt, args
    (opt, args) = parser.parse_args()

    # sanity check for some of the arguments
    if len(args)!=1:
        parser.error('Wrong number of arguments. Exiting...')
        sys.exit()
    if (not os.path.exists(args[0])):
        print 'Datasets list file ['+args[0]+'] does not exist. Exiting...'
        sys.exit()

    if (not opt.cfgFile):
        parser.error('No configuration file specified. Using the default one.')
    if (not os.path.exists(opt.cfgFile)):
        print 'Config file ['+opt.cfgFile+'] does not exist. Exiting...'
        sys.exit()

    if (not opt.JSON):
        parser.error('No JSON file specified. Using the default one.')
    if (not os.path.exists('./JSONs/'+opt.JSON)):
        print 'JSON file [./JSONs/'+opt.JSON+'] does not exist. Exiting...'
        sys.exit()

    if (not opt.lumiCalc):
        parser.error('No lumiCalc output file specified. Using the default one.')
    if (not os.path.exists(opt.lumiCalc)):
        print 'lumiCalc output file ['+opt.lumiCalc+'] does not exist. Exiting...'
        sys.exit()

    if (not opt.runPeriod):
        parser.error('No run period specified. Using the default one.')
    if (opt.runPeriod != 'JanA_Jul1' and opt.runPeriod != 'JanA_Jul2' and opt.runPeriod != 'JanA_Aug' and opt.runPeriod != 'JanA_Oct' and opt.runPeriod != 'JanB' and opt.runPeriod != 'Custom' and opt.runPeriod != '2012A' and opt.runPeriod != '2012B' and opt.runPeriod != '2012Cv1' and opt.runPeriod != '2012D' and opt.runPeriod != 'Aug24' and opt.runPeriod != '2012Cv2' and opt.runPeriod != 'ECAL' and opt.runPeriod != '2012C' and opt.runPeriod != 'Jun08'):
        print 'The run period ['+opt.runPeriod+'] is not supported. Exiting...'
        sys.exit()
    if (opt.runPeriod == 'Custom' and (not opt.runMin or not opt.runMax)):
        print 'The --runMin and --rumMax options must be specified for the run period ['+opt.runPeriod+']. Exiting...'
        sys.exit()


    if opt.isMC:
        crab_src = 'crab_src.cfg'
        if (not os.path.exists(crab_src)):
            print 'Crab template file ['+crab_src+'] does not exist. Exiting...'
            sys.exit()
    else:
        crab_data_src = 'crab_data_src.cfg'
        if (not os.path.exists(crab_data_src)):
            print 'lumiCalc output file ['+crab_data_src+'] does not exist. Exiting...'
            sys.exit()


# read in the lumiCalc output file and create simplified output file [Run:Lumi:Unit] and list of run ranges
def processLumiCalc(lumiCalOutput, runlumisSimplified, runRanges):
    global opt

    # open the lumi calc output file
    f = open(lumiCalOutput, 'r')
    runlumis = f.readlines()
    f.close()

    # set the runMin and runMax
    runMin = []
    runMax = []
    getRunPeriodLimits(runMin, runMax)
    runMin = runMin[0]
    runMax = runMax[0]
    
    lumiStep = 100
    lumiTot = 0
    lumiTotPrev = 0
    runPrev = runMin
    for runlumi in runlumis:
        runlumi_parts = runlumi.rstrip('\n').split('|')
        if (len(runlumi_parts[len(runlumi_parts)-2].split('(')) == 2) and (len(runlumi_parts[1].split(':')) == 2):
            run = runlumi_parts[1].split(':')[0].lstrip(' ')
            lumiTmp = runlumi_parts[len(runlumi_parts)-2].split('(')[0]
            unit = runlumi_parts[len(runlumi_parts)-2].split('(/')[1].split(')')[0]
            runlumiSimplified = run +'\t'+ lumiTmp +'\t'+ unit+'\n'
            runlumisSimplified.append(runlumiSimplified)
            if (int(run) < runMin or int(run) > runMax):
                continue
            lumiFact = 0
            if (unit == 'ub'):
                lumiFact = 0.000001
            if (unit == 'nb'):
                lumiFact = 0.001
            if (unit == 'pb'):
                lumiFact = 1.0
            if (unit == 'fb'):
                lumiFact = 1000.0
            lumi = lumiFact * float(lumiTmp)
            lumiTot = lumiTot + lumi
            if (lumiTot > lumiTotPrev + lumiStep):
                runRanges.append(str(runPrev)+'-'+str(run))
                print 'Run range:  ' + str(runPrev) + '-' + str(run)+', IntLumi: '+ str(lumiTot) +' \pb'
                runPrev = int(run)+1  
                lumiTotPrev = lumiTot
    if (int(runPrev) != int(run)+1) and not (int(run) < runMin or int(run) > runMax):
        runRanges.append(str(runPrev)+'-'+str(run))
        print 'Run range:  ' + str(runPrev) + '-' + str(run)+', IntLumi: '+ str(lumiTot) +' \pb'

    if (runPrev != runMax) and (int(run) > runMax):
        runRanges.append(str(runPrev)+'-'+str(runMax))
        print 'Run range:  ' + str(runPrev) + '-' + str(runMax)+', IntLumi: '+ str(lumiTot) +' \pb'

    return lumiCalOutput, runlumisSimplified, runRanges


def prepareCrabArea(dataset, runRange, subDirName):        
    global opt, args
    
    # different string treatment for DATA/MC/USER samples
    if opt.isMC and opt.isUSER:
        # for run on official samples
        splitStr = '_GENSIMRECO'
    elif opt.isMC and not opt.isUSER:
        # for run on user samples
        splitStr = '_Summer12'
    else:
        #for run on data
        splitStr = '_AOD'
    USERNAME=opt.UserName
    
    # prepare directories and file names
    dataset = dataset.rstrip('\n')
    if (runRange != ''):
        datasetDirName = dataset.replace('/','_').split(splitStr)[0][1:]+'_'+runRange
    else:
        datasetDirName = dataset.replace('/','_').split(splitStr)[0][1:]
    workDirName = subDirName + '/' + datasetDirName
    crabFileName = workDirName + '/crab.cfg'
    makeDirectory(workDirName)

#    cmd = 'cp ' + opt.cfgFile + ' ' + workDirName
    cmd = 'cat '+opt.cfgFile+' | sed "s%MYOUTPUTFILE%'+datasetDirName+'.root%g" > '+workDirName+'/'+opt.cfgFile
    processCmd(cmd)
    if opt.isMC:
        outputDirName = opt.T2Dir + '/' + datasetDirName + '_' + opt.appendName
        cmd = 'cat crab_src.cfg | sed "s%MYDATASET%'+dataset+'%g" | sed "s%MYCFGFILE%'+opt.cfgFile+'%g" | sed "s%MYOUTPUTFILE%'+datasetDirName+'.root%g" | sed "s%NJOBS%'+str(opt.nJobs)+'%g" | sed "s%MYT2DIR%'+outputDirName+'%g" | sed "s%MYUSERNAME%'+USERNAME+'%g" > '+crabFileName 
        processCmd(cmd)
    else:
        outputDirName = opt.T2Dir + '/' + runRange        
        cmd = 'cat crab_data_src.cfg | sed "s%MYDATASET%'+dataset+'%g" | sed "s%MYCFGFILE%'+opt.cfgFile+'%g" | sed "s%MYOUTPUTFILE%'+datasetDirName+'.root%g" | sed "s%NJOBS%'+str(opt.nJobs)+'%g" | sed "s%MYT2DIR%'+outputDirName+'%g" | sed "s%MYUSERNAME%'+USERNAME+'%g" | sed "s%MYJSON%'+opt.JSON+'%g" | sed "s%MYRUNRANGE%'+runRange+'%g" | sed "s%NLUMISPERJOB%'+str(opt.lumisPerJob)+'%g"  > '+crabFileName
        processCmd(cmd)
        cmd = 'cp ' + './JSONs/'+opt.JSON + ' ' + workDirName
        processCmd(cmd)

# read in the lumiCalc output file and create simplified output file [Run:Lumi:Unit] and list of run ranges
def getRunPeriodLimits(runMin, runMax):
    global opt

    print 'Run Period: ' + opt.runPeriod

    if opt.runPeriod == '2012A':
        runMin.append(190456)
        runMax.append(193751)
    if opt.runPeriod == '2012B':
        runMin.append(193752)
        runMax.append(196531)
    if opt.runPeriod == 'Aug24':
        runMin.append(198022)
        runMax.append(198523)
    if opt.runPeriod == '2012Cv1':
        runMin.append(196532)
        runMax.append(198933)
    if opt.runPeriod == '2012Cv2':
        runMin.append(198934)
        runMax.append(203755)
    if opt.runPeriod == '2012C':
        runMin.append(196532)
        runMax.append(203772)
    if opt.runPeriod == '2012D':
        runMin.append(203773)
        runMax.append(208940)
    if opt.runPeriod == 'ECAL':
        runMin.append(190782)
        runMax.append(190949)
    if opt.runPeriod == 'Jun08':
        runMin.append(190646)
        runMax.append(193193)
    if opt.runPeriod == 'JanA_Jul1':
        runMin.append(160404)
        runMax.append(163869)
    if opt.runPeriod == 'JanA_Jul2':
        runMin.append(165088)
        runMax.append(167913)
    if opt.runPeriod == 'JanA_Aug':
        runMin.append(170249)
        runMax.append(172619)
    if opt.runPeriod == 'JanA_Oct':
        runMin.append(172620)
        runMax.append(175770)
    if opt.runPeriod == 'JanB':
        runMin.append(175832)
        runMax.append(180252)
    if opt.runPeriod == 'Custom':
        runMin.append(opt.runMin)
        runMax.append(opt.runMax)

    return runMin, runMax

# define make directory function
def makeDirectory(subDirName):
    if (not os.path.exists(subDirName)):
        cmd = 'mkdir -p '+subDirName
        status, output = commands.getstatusoutput(cmd)
        if status !=0:
            print 'Error in creating submission dir '+subDirName+'. Exiting...'
            sys.exit()
    else:
        print 'Directory '+subDirName+' already exists. Exiting...'
        sys.exit()


#define function for processing of os command
def processCmd(cmd):
#    print cmd
    status, output = commands.getstatusoutput(cmd)
    if status !=0:
        print 'Error in processing command:\n   ['+cmd+'] \nExiting...'
        sys.exit()


# the main procedure
def create_RM_cfg():
    
    # parse the arguments and options
    global opt, args
    parseOptions()
    
    # prepare new submission directory 
    if ('.txt' in args[0]):
        subDirName = args[0].split('.txt')[0]
    else:
        subDirName = args[0].split('.')[0]
    subDirName = 'Submission_'+subDirName+'_'+opt.appendName
    if opt.runPeriod and not opt.isMC:
        subDirName += '_'+opt.runPeriod
        if opt.runPeriod == 'Custom' :
            subDirName += '_'+str(opt.runMin)+'-'+str(opt.runMax)
    makeDirectory(subDirName)


    # print main config info
    print '--------------------------------------------------';
    print 'Submission dir: ' + subDirName;
    print 'Datasets list:  ' + args[0];
    print '--------------------------------------------------';

    # process lumi calc output and get run ranges
    runRanges = []
    if not opt.isMC:
        runlumisSimplified = []
        processLumiCalc(opt.lumiCalc, runlumisSimplified, runRanges)
        f = open('run-IntLumi-list.txt', 'w')
        f.writelines(runlumisSimplified)
        f.close()

    # read in the list of datasets from the specified file
    f = open(args[0], 'r')
    datasets = f.readlines()
    f.close()
    
    # process each dataset
    for dataset in datasets:
        if opt.isMC:
            runRange = ''
            prepareCrabArea(dataset, runRange, subDirName)
        else:            
            for runRange in runRanges:
                prepareCrabArea(dataset, runRange, subDirName)
    sys.exit()

# run the create_RM_cfg() as main()
if __name__ == "__main__":
    create_RM_cfg()

