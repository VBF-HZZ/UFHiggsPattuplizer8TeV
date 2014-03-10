import FWCore.ParameterSet.Config as cms

from PhysicsTools.PatAlgos.tools.jetTools import *
from PhysicsTools.PatAlgos.tools.coreTools import *
from PhysicsTools.PatAlgos.tools.pfTools import *
from CommonTools.ParticleFlow.Isolation.tools_cfi import *

IsolationChoices = ("DetBased", "PFlow", "DetBased+PFlow", "PFlow+DetBased")
####################################################################
def addIsolations2PatCandidate(candidateType, process,module,postfix="",verbose=False, kind="DetBased+PFlow",skipVetoLeptonSeqence=False,skipSelectingPfCands=False):
    if verbose:
        print "[Info] Adding "+kind+" isolations to "+ candidateType + " with postfix '"+postfix+"'"
    checkNames(kind, IsolationChoices)
    #check which module is used
    
    cand = candidateType.capitalize()
    doDetBased = "DetBased" in kind
    doPFlow = "PFlow" in kind
    
    if doDetBased :
        if not skipVetoLeptonSeqence :
	  selectVetoLeptons4DetBasedIsolation(process)
        if cand=='Electron' :
	  customizeDetBasedElectronIsolation(process,module,"",verbose) #to customize particles used, deposits, cones, vetos etc.
        if cand=='Muon' :
	  customizeDetBasedMuonIsolation(process,module,"",verbose) #to customize particles used, deposits, cones, vetos etc.
    if doPFlow :
        if cand=='Electron' :
	  customizePFElectronIsolation(process,module,"",verbose) #to customize particles used, deposits, cones, vetos etc.
        if cand=='Muon' :
	  customizePFMuonIsolation(process,module,"",verbose) #to customize particles used, deposits, cones, vetos etc.
        
    module.isoDeposits = cms.PSet()
    #module.isolationValues = cms.PSet()
    module.userIsolation = cms.PSet()
    
    #Setup isolation sequence: 1. isodeposits, 2. isolation from deposits
    if doDetBased and not doPFlow :   
        #if cand=="Electron" :
        setattr(process,"pat"+cand+"IsoDepositsSequence"+postfix,
	      getattr(process,"DetBased"+cand+"IsoDepositsSequence"+postfix)
	      ) # no need to add isodeps for muons
        setattr(process,"pat"+cand+"IsolationFromDepositsSequence"+postfix,
	      getattr(process,"DetBased"+cand+"IsolationFromDepositsSequence"+postfix)
	      )
    elif doPFlow and not doDetBased:
        setattr(process,"pat"+cand+"IsoDepositsSequence"+postfix,
	      getattr(process,"PFlow"+cand+"IsoDepositsSequence"+postfix)
	      )
        setattr(process,"pat"+cand+"IsolationFromDepositsSequence"+postfix,
	      getattr(process,"PFlow"+cand+"IsolationFromDepositsSequence"+postfix)
	      )
    elif doPFlow and doDetBased:  
        setattr(process,"pat"+cand+"IsoDepositsSequence"+postfix,
	      cms.Sequence(
		        #getattr(process,"DetBased"+cand+"IsoDepositsSequence"+postfix) +
		        getattr(process,"PFlow"+cand+"IsoDepositsSequence"+postfix)
		        )
	      )
        #if cand=="Electron" :	     
        getattr(process,"pat"+cand+"IsoDepositsSequence"+postfix).replace(
	        getattr(process,"PFlow"+cand+"IsoDepositsSequence"+postfix),
	        getattr(process,"DetBased"+cand+"IsoDepositsSequence"+postfix) +
	        getattr(process,"PFlow"+cand+"IsoDepositsSequence"+postfix)
        )
	      
        setattr(process,"pat"+cand+"IsolationFromDepositsSequence"+postfix,
	      cms.Sequence(
		        getattr(process,"DetBased"+cand+"IsolationFromDepositsSequence"+postfix) + 
		        getattr(process,"PFlow"+cand+"IsolationFromDepositsSequence"+postfix)
		        )
	      )	   
	      
    #if doDetBased and cand=="Muon" :
        #setattr(process,"pat"+cand+"IsolationSequence"+postfix,
	      #cms.Sequence(getattr(process,"pat"+cand+"IsolationFromDepositsSequence"+postfix)
		  #)
	      #)
        
    #else :
    setattr(process,"pat"+cand+"IsolationSequence"+postfix,
	  cms.Sequence(getattr(process,"pat"+cand+"IsoDepositsSequence"+postfix) +
	        getattr(process,"pat"+cand+"IsolationFromDepositsSequence"+postfix)
	        )
	  )
        
	      
		
        #Add pf candidate selection module to sequence if not already included
    
    if doPFlow and not skipSelectingPfCands :
    #if doPFlow and not hasattr(process,"pfCandidateSelectionByType") :
        getattr(process,"PFlow"+cand+"IsoDepositsSequence"+postfix).replace(
				getattr(process,"isoDep"+cand+"WithChargedHadrons"),
				getattr(process,"pfCandidateSelectionByType")+
				getattr(process,"isoDep"+cand+"WithChargedHadrons")
				)
	
    #setup isoDeposits and isolations in Pat object itself
    if doDetBased and not doPFlow :
        module.userIsolation = cms.PSet(
	      tracker = cms.InputTag("isoVal"+cand+"TkOptimized"),
	      ecal    = cms.InputTag("isoVal"+cand+"EcalOptimized"),
	      hcal    = cms.InputTag("isoVal"+cand+"HcalOptimized"),
	      user    = cms.VPSet(
		      cms.PSet( src = cms.InputTag("isoVal"+cand+"TkOptimized5") ),
		      ###WARNING FUN FUN FUN Cheking if the size of vector is limited
		      cms.PSet( src = cms.InputTag("muIsoFromDepsEcaldr005")),
		      cms.PSet( src = cms.InputTag("muIsoFromDepsEcaldr007")),
		      cms.PSet( src = cms.InputTag("muIsoFromDepsEcaldr01")),
		      cms.PSet( src = cms.InputTag("muIsoFromDepsEcaldr005")),
		      cms.PSet( src = cms.InputTag("muIsoFromDepsEcaldr007")),
		      cms.PSet( src = cms.InputTag("muIsoFromDepsEcaldr01"))
		    )
	      )
        if cand=="Electron" :
	  module.isoDeposits = cms.PSet(
		tracker =cms.InputTag("eleIsoDepositTk"),
		ecal = cms.InputTag("eleIsoDepositEcalFromHits"),
		hcal = cms.InputTag("eleIsoDepositHcalFromTowers")				
	      )
	       
        if cand=="Muon" :
	  specialFsrIsolation = cms.VInputTag(
		cms.InputTag("muIsoFromDepsEcaldr005"),
		cms.InputTag("muIsoFromDepsEcaldr007"),
		cms.InputTag("muIsoFromDepsEcaldr01")
		)  
	  module.userIsolation.user.extend(specialFsrIsolation)
	  module.isoDeposits = cms.PSet(
		tracker = cms.InputTag("muIsoDepositTk"),
		ecal    = cms.InputTag("muIsoDepositCalByAssociatorTowers","ecal"),
		hcal    = cms.InputTag("muIsoDepositCalByAssociatorTowers","hcal"),
		user    = cms.VInputTag(
			        cms.InputTag("FsrMuIsoDepositCalByAssociatorHitsdr005","ecal"),
			)
	      )
	  module.userIsolation = cms.PSet(
		tracker = cms.InputTag("isoVal"+cand+"TkOptimized"),
		ecal    = cms.InputTag("isoVal"+cand+"EcalOptimized"),
		hcal    = cms.InputTag("isoVal"+cand+"HcalOptimized"),
		user = cms.VPSet(
			  cms.PSet( src = cms.InputTag("isoValMuonTkOptimized5") ), 
		  )      
	      )
    elif doPFlow and not doDetBased :
        module.isoDeposits = cms.PSet(
	  pfAllParticles = cms.InputTag("isoDep"+cand+"WithChargedPU"+postfix),
	  pfChargedHadrons = cms.InputTag("isoDep"+cand+"WithChargedHadrons"+postfix),
	  pfNeutralHadrons = cms.InputTag("isoDep"+cand+"WithNeutral"+postfix),
	  pfPhotons = cms.InputTag("isoDep"+cand+"WithPhotons"+postfix)
	  )
        module.userIsolation = cms.PSet(
	  pfAllParticles = cms.InputTag("isoVal"+cand+"WithChargedPU"+postfix),
	  pfChargedHadrons = cms.InputTag("isoVal"+cand+"WithChargedHadrons"+postfix),
	  pfNeutralHadrons = cms.InputTag("isoVal"+cand+"WithNeutral"+postfix),
	  pfPhotons = cms.InputTag("isoVal"+cand+"WithPhotons"+postfix)
	  )
	  
    elif doPFlow and doDetBased:    
        module.isolationValues = cms.PSet(
		  tracker = cms.InputTag("isoVal"+cand+"TkOptimized"),
		  ecal    = cms.InputTag("isoVal"+cand+"EcalOptimized"),
		  hcal    = cms.InputTag("isoVal"+cand+"HcalOptimized"),
		  pfAllParticles = cms.InputTag("isoVal"+cand+"WithChargedPU"+postfix),
		  pfChargedHadrons = cms.InputTag("isoVal"+cand+"WithChargedHadrons"+postfix),
		  pfNeutralHadrons = cms.InputTag("isoVal"+cand+"WithNeutral"+postfix),
		  pfPhotons = cms.InputTag("isoVal"+cand+"WithPhotons"+postfix),
		  user = cms.VInputTag(
		        #cms.InputTag("isoVal"+cand+"TkOptimized"),
		        cms.InputTag("isoVal"+cand+"TkOptimized5"),
		  )   
		  )
        if cand=="Electron" :
	     module.isoDeposits = cms.PSet(
		    tracker = cms.InputTag("eleIsoDepositTk"),
		    ecal    = cms.InputTag("eleIsoDepositEcalFromHits"),
		    hcal    = cms.InputTag("eleIsoDepositHcalFromTowers"),
		    pfAllParticles   = cms.InputTag("isoDep"+cand+"WithChargedPU"+postfix),
		    pfChargedHadrons = cms.InputTag("isoDep"+cand+"WithChargedHadrons"+postfix),
		    pfNeutralHadrons = cms.InputTag("isoDep"+cand+"WithNeutral"+postfix),
		    pfPhotons = cms.InputTag("isoDep"+cand+"WithPhotons"+postfix)
		    #user    = cms.VInputTag(
			        #cms.InputTag("eleIsoDepositTk"),
			        #cms.InputTag("eleIsoDepositEcalFromHits"),
			        #cms.InputTag("eleIsoDepositHcalFromTowers")				
			    #)
		)
        if cand=="Muon" :
	  specialFsrIsolation = cms.VInputTag(
		        cms.InputTag("muIsoFromDepsEcaldr005"),
		        cms.InputTag("muIsoFromDepsEcaldr007"),
		        cms.InputTag("muIsoFromDepsEcaldr01")
		  )  
	  module.isolationValues.user.extend(specialFsrIsolation)
	  module.isoDeposits = cms.PSet(
		tracker = cms.InputTag("muIsoDepositTk"),
		ecal    = cms.InputTag("muIsoDepositCalByAssociatorTowers","ecal"),
		hcal    = cms.InputTag("muIsoDepositCalByAssociatorTowers","hcal"),
		pfAllParticles = cms.InputTag("isoDep"+cand+"WithChargedPU"+postfix),
		pfChargedHadrons = cms.InputTag("isoDep"+cand+"WithChargedHadrons"+postfix),
		pfNeutralHadrons = cms.InputTag("isoDep"+cand+"WithNeutral"+postfix),
		pfPhotons = cms.InputTag("isoDep"+cand+"WithPhotons"+postfix),
		user = cms.VInputTag(
			        cms.InputTag("FsrMuIsoDepositCalByAssociatorHitsdr005","ecal"),
			        #cms.InputTag("muIsoDepositTk"),
			        #cms.InputTag("muIsoDepositCalByAssociatorTowers","ecal"),
			        #cms.InputTag("muIsoDepositCalByAssociatorTowers","hcal")				
			)
	      )
	  #module.userIsolation = cms.PSet(
		    #user = cms.VPSet(
			      #cms.PSet( src = cms.InputTag("isoValMuonTkOptimized") ), 
			      #cms.PSet( src = cms.InputTag("isoValMuonEcalOptimized") ),
			      #cms.PSet( src = cms.InputTag("isoValMuonHcalOptimized") ),
			      #cms.PSet( src = cms.InputTag("isoValMuonTkOptimized5") ), 
		      #)      
		#)

            
    process.patDefaultSequence.replace(module,
                                       getattr(process,"pat"+cand+"IsolationSequence"+postfix)+
                                       module
                                       )

   
###################a#################################################
def addSelectedPFlowParticle(process,verbose=False):
    if verbose:
        print "[Info] Adding pf-particles (for pf-isolation and pf-seed pat-leptons)"
    process.load("CommonTools.ParticleFlow.ParticleSelectors.pfSortByType_cff")
    process.load("CommonTools.ParticleFlow.pfNoPileUp_cff")

    #process.pfAllChargedCandidates.pdgId.extend(process.pfAllElectrons.pdgId.value()) #WARNING removes
                              
                              
    process.pfPU = cms.EDProducer(
        "TPPFCandidatesOnPFCandidates",
        enable =  cms.bool( True ),
        verbose = cms.untracked.bool( False ),
        name = cms.untracked.string("puPFCandidates"),
        topCollection = cms.InputTag("pfNoPileUp"),
        bottomCollection = cms.InputTag("particleFlow"),
        )
    process.pfAllChargedHadronsPU = process.pfAllChargedHadrons.clone(src='pfPU')

    #################################################################
    process.pfNoCharged = process.pfPU.clone(
        name = cms.untracked.string("noChargedPFCandidates"),
        topCollection = cms.InputTag("pfAllChargedHadrons"),
        bottomCollection = cms.InputTag("particleFlow"),
        )
    #process.pfAllNeutral = cms.EDFilter(
        #"PdgIdPFCandidateSelector",
        #pdgId = cms.vint32(111, 130, 310, 2112, 22),
        #src = cms.InputTag("pfNoCharged")
        #)
    #################################################################

    process.pfCandidateSelectionByType = cms.Sequence(
        process.pfNoPileUpSequence *
        ( process.pfAllNeutralHadrons +
          process.pfAllChargedHadrons +
          #process.pfAllChargedCandidates +
          process.pfAllPhotons +
          (process.pfPU * process.pfAllChargedHadronsPU )
          )  #+
        #process.pfAllMuons +
        #process.pfAllElectrons +
        #( process.pfNoCharged+process.pfAllNeutral)
        )
    process.pfPileUp.Enable              = True
    process.pfPileUp.checkClosestZVertex = True
    process.pfPileUp.Vertices            = "offlinePrimaryVertices"
    #process.pfAllMuons.src               = "pfNoPileUp"
    #process.pfAllElectrons.src           = "pfNoPileUp"
    
    
###################a#################################################
def customizePFMuonIsolation(process,module,postfix="",verbose=False):
    
    if verbose:
        print "[Info] Customizing particle isolation to muon with postfix '"+postfix+"'"
    
    if not hasattr(process, "pfCandidateSelectionByType"):
       addSelectedPFlowParticle(process,verbose=verbose)
        
    #setup correct src of isolated object

    setattr(process,"isoDepMuonWithChargedHadrons"+postfix,
            isoDepositReplace(module.muonSource,
                              'pfAllChargedHadrons'))
    setattr(process,"isoDepMuonWithChargedPU"+postfix,
            isoDepositReplace(module.muonSource,
                              'pfAllChargedHadronsPU'))
    setattr(process,"isoDepMuonWithNeutral"+postfix,
            isoDepositReplace(module.muonSource,
                              'pfAllNeutralHadrons'))
    setattr(process,"isoDepMuonWithPhotons"+postfix,
            isoDepositReplace(module.muonSource,
                              'pfAllPhotons'))

    #compute isolation values form deposits
    process.load("CommonTools.ParticleFlow.Isolation.pfMuonIsolationFromDeposits_cff")
    
    setattr(process,"isoValMuonWithChargedPU",
            process.isoValMuonWithCharged.clone())
    getattr(process,"isoValMuonWithChargedPU").deposits[0].src="isoDepMuonWithChargedPU"
    setattr(process,"isoValMuonWithChargedHadrons",
            process.isoValMuonWithCharged.clone())
    getattr(process,"isoValMuonWithChargedHadrons").deposits[0].src="isoDepMuonWithChargedHadrons"

    if postfix!="":
        setattr(process,"isoValMuonWithChargedHadrons"+postfix,
                process.isoValMuonWithCharged.clone())
        getattr(process,"isoValMuonWithChargedHadrons"+postfix).deposits[0].src="isoDepMuonWithChargedHadrons"+postfix
        setattr(process,"isoValMuonWithChargedPU"+postfix,
                process.isoValMuonWithChargedPU.clone())
        getattr(process,"isoValMuonWithChargedPU"+postfix).deposits[0].src="isoDepMuonWithChargedPU"+postfix
        setattr(process,"isoValMuonWithNeutral"+postfix,
                process.isoValMuonWithNeutral.clone())
        getattr(process,"isoValMuonWithNeutral"+postfix).deposits[0].src="isoDepMuonWithNeutral"+postfix
        setattr(process,"isoValMuonWithPhotons"+postfix,
                process.isoValMuonWithPhotons.clone())
        getattr(process,"isoValMuonWithPhotons"+postfix).deposits[0].src="isoDepMuonWithPhotons"+postfix
        

    setattr(process,"PFlowMuonIsoDepositsSequence"+postfix,
            cms.Sequence(
                         getattr(process,"isoDepMuonWithChargedHadrons"+postfix) +
                         getattr(process,"isoDepMuonWithChargedPU"+postfix) +
                         getattr(process,"isoDepMuonWithNeutral"+postfix) +
                         getattr(process,"isoDepMuonWithPhotons"+postfix)
                         )
            )
    setattr(process,"PFlowMuonIsolationFromDepositsSequence"+postfix,
            cms.Sequence(
                         getattr(process,"isoValMuonWithChargedHadrons"+postfix) +
                         getattr(process,"isoValMuonWithChargedPU"+postfix) +
                         getattr(process,"isoValMuonWithNeutral"+postfix) +
                         getattr(process,"isoValMuonWithPhotons"+postfix)
                         )
            )



    getattr(process,"isoDepMuonWithChargedHadrons"+postfix).ExtractorPSet = cms.PSet(
        Diff_z = cms.double(99999.99),
        ComponentName = cms.string('CandViewExtractor'),
        DR_Max = cms.double(1.0),
        Diff_r = cms.double(99999.99),
        inputCandView = cms.InputTag("pfAllChargedHadrons"),
        DR_Veto = cms.double(1e-05),
        DepositLabel = cms.untracked.string('')
        )
    getattr(process,"isoDepMuonWithNeutral"+postfix).ExtractorPSet = cms.PSet(
        Diff_z = cms.double(99999.99),
        ComponentName = cms.string('CandViewExtractor'),
        DR_Max = cms.double(1.0),
        Diff_r = cms.double(99999.99),
        inputCandView = cms.InputTag("pfAllNeutralHadrons"),
        DR_Veto = cms.double(1e-05),
        DepositLabel = cms.untracked.string('')
        )
    getattr(process,"isoDepMuonWithPhotons"+postfix).ExtractorPSet = cms.PSet(
        Diff_z = cms.double(99999.99),
        ComponentName = cms.string('CandViewExtractor'),
        DR_Max = cms.double(1.0),
        Diff_r = cms.double(99999.99),
        inputCandView = cms.InputTag("pfAllPhotons"),
        DR_Veto = cms.double(1e-05),
        DepositLabel = cms.untracked.string('')
        )   
        
        
    #    
    getattr(process,"isoValMuonWithChargedHadrons"+postfix).deposits = cms.VPSet(
        cms.PSet(
        src = cms.InputTag("isoDepMuonWithChargedHadrons"+postfix),
        deltaR = cms.double(0.3),
        weight = cms.string('1'),
        vetos = cms.vstring('Threshold(0.0)'),
        skipDefaultVeto = cms.bool(True),
        mode = cms.string('sum')
        )
        )    
    getattr(process,"isoValMuonWithNeutral"+postfix).deposits = cms.VPSet(
        cms.PSet(
        src = cms.InputTag("isoDepMuonWithNeutral"+postfix),
        deltaR = cms.double(0.3),
        weight = cms.string('1'),
        vetos = cms.vstring('Threshold(0.5)'),
        skipDefaultVeto = cms.bool(True),
        mode = cms.string('sum')
        )
        )
    getattr(process,"isoValMuonWithPhotons"+postfix).deposits = cms.VPSet(
        cms.PSet(
        src = cms.InputTag("isoDepMuonWithPhotons"+postfix),
        deltaR = cms.double(0.3),
        weight = cms.string('1'),
        vetos = cms.vstring('Threshold(0.5)'),
        skipDefaultVeto = cms.bool(True),
        mode = cms.string('sum')
        )
        )
    getattr(process,"isoValMuonWithChargedPU"+postfix).deposits[0].vetos = getattr(
        process,"isoValMuonWithChargedHadrons"+postfix).deposits[0].vetos


###################a#################################################
def customizePFElectronIsolation(process,module,postfix="",verbose=False):
    if verbose:
        print "[Info] Customizing particle isolation to electron with postfix '"+postfix+"'"
    
    if not hasattr(process, "pfCandidateSelectionByType"):
       addSelectedPFlowParticle(process,verbose=verbose)
        
    #setup correct src of isolated object
    setattr(process,"isoDepElectronWithChargedHadrons"+postfix,
            isoDepositReplace(module.electronSource,
                              'pfAllChargedHadrons'))
    setattr(process,"isoDepElectronWithChargedPU"+postfix,
            isoDepositReplace(module.electronSource,
                              'pfAllChargedHadronsPU'))
    setattr(process,"isoDepElectronWithNeutral"+postfix,
            isoDepositReplace(module.electronSource,
                              'pfAllNeutralHadrons'))
    setattr(process,"isoDepElectronWithPhotons"+postfix,
            isoDepositReplace(module.electronSource,
                              'pfAllPhotons'))

    #compute isolation values form deposits
    process.load("CommonTools.ParticleFlow.Isolation.pfElectronIsolationFromDeposits_cff")
    setattr(process,"isoValElectronWithChargedPU",
	  process.isoValElectronWithCharged.clone())
    getattr(process,"isoValElectronWithChargedPU").deposits[0].src="isoDepElectronWithChargedPU"
    
    setattr(process,"isoValElectronWithChargedHadrons",
            process.isoValElectronWithCharged.clone())
    getattr(process,"isoValElectronWithChargedHadrons").deposits[0].src="isoDepElectronWithChargedHadrons"
    
   
    #compute isolation values form deposits
    if postfix!="":
        setattr(process,"isoValElectronWithChargedHadrons"+postfix,
                process.isoValElectronWithCharged.clone())
        getattr(process,"isoValElectronWithChargedHadrons"+postfix).deposits[0].src="isoDepElectronWithChargedHadrons"+postfix
        setattr(process,"isoValElectronWithChargedPU"+postfix,
                process.isoValElectronWithChargedPU.clone())
        getattr(process,"isoValElectronWithChargedPU"+postfix).deposits[0].src="isoDepElectronWithChargedPU"+postfix,
     
        setattr(process,"isoValElectronWithNeutral"+postfix,
                process.isoValElectronWithNeutral.clone())
        getattr(process,"isoValElectronWithNeutral"+postfix).deposits[0].src="isoDepElectronWithNeutral"+postfix
        setattr(process,"isoValElectronWithPhotons"+postfix,
                process.isoValElectronWithPhotons.clone())
        getattr(process,"isoValElectronWithPhotons"+postfix).deposits[0].src="isoDepElectronWithPhotons"+postfix
        


    setattr(process,"PFlowElectronIsoDepositsSequence"+postfix,
            cms.Sequence(
                         getattr(process,"isoDepElectronWithChargedHadrons"+postfix) +
                         getattr(process,"isoDepElectronWithChargedPU"+postfix) +
                         getattr(process,"isoDepElectronWithNeutral"+postfix) +
                         getattr(process,"isoDepElectronWithPhotons"+postfix)
                         )
            )
            
    setattr(process,"PFlowElectronIsolationFromDepositsSequence"+postfix,
	  cms.Sequence(
		      getattr(process,"isoValElectronWithChargedHadrons"+postfix) +
		      getattr(process,"isoValElectronWithChargedPU"+postfix) +
		      getattr(process,"isoValElectronWithNeutral"+postfix) +
		      getattr(process,"isoValElectronWithPhotons"+postfix)
		      )
	  )

    #Deposit extractor PSets
    getattr(process,"isoDepElectronWithChargedHadrons"+postfix).ExtractorPSet = cms.PSet(
        Diff_z = cms.double(99999.99),
        ComponentName = cms.string('CandViewExtractor'),
        DR_Max = cms.double(1.0),
        Diff_r = cms.double(99999.99),
        inputCandView = cms.InputTag("pfAllChargedHadrons"),
        DR_Veto = cms.double(1e-05),
        DepositLabel = cms.untracked.string('')
        )
 
    getattr(process,"isoDepElectronWithNeutral"+postfix).ExtractorPSet = cms.PSet(
        Diff_z = cms.double(99999.99),
        ComponentName = cms.string('CandViewExtractor'),
        DR_Max = cms.double(1.0),
        Diff_r = cms.double(99999.99),
        inputCandView = cms.InputTag("pfAllNeutralHadrons"),
        DR_Veto = cms.double(1e-05),
        DepositLabel = cms.untracked.string('')
        )
    getattr(process,"isoDepElectronWithPhotons"+postfix).ExtractorPSet = cms.PSet(
        Diff_z = cms.double(99999.99),
        ComponentName = cms.string('CandViewExtractor'),
        DR_Max = cms.double(1.0),
        Diff_r = cms.double(99999.99),
        inputCandView = cms.InputTag("pfAllPhotons"),
        DR_Veto = cms.double(1e-05),
        DepositLabel = cms.untracked.string('')
        )
        
    #IsoFromDeps PSets
    getattr(process,"isoValElectronWithChargedHadrons"+postfix).deposits = cms.VPSet(
        cms.PSet(
        src = cms.InputTag("isoDepElectronWithChargedHadrons"+postfix),
        deltaR = cms.double(0.3),
        weight = cms.string('1'),
        vetos = cms.vstring('Threshold(0.0)',
                            'EcalEndcaps:0.015',
		        ),
        skipDefaultVeto = cms.bool(True),
        mode = cms.string('sum')
        )
        )
    getattr(process,"isoValElectronWithNeutral"+postfix).deposits = cms.VPSet(
        cms.PSet(
        src = cms.InputTag("isoDepElectronWithNeutral"+postfix),
        deltaR = cms.double(0.3),
        weight = cms.string('1'),
        vetos = cms.vstring('Threshold(0.5)'),
        skipDefaultVeto = cms.bool(True),
        mode = cms.string('sum')
        )
        )
    getattr(process,"isoValElectronWithPhotons"+postfix).deposits = cms.VPSet(
        cms.PSet(
        src = cms.InputTag("isoDepElectronWithPhotons"+postfix),
        deltaR = cms.double(0.3),
        weight = cms.string('1'),
        vetos = cms.vstring('Threshold(0.5)',                            
		        'EcalEndcaps:0.08'
		        ),
        skipDefaultVeto = cms.bool(True),
        mode = cms.string('sum')
        )
        )



    getattr(process,"isoValElectronWithChargedPU"+postfix).deposits[0].vetos = getattr(
        process,"isoValElectronWithChargedHadrons"+postfix).deposits[0].vetos


####################################################################
def customizeDetBasedMuonIsolation(process,module,postfix="",verbose=False):
  
    #####Code for the muISO
    #from RecoMuon.MuonIsolationProducers.muIsoDepositTk_cfi import *
    #import RecoMuon.MuonIsolationProducers.muIsoDepositTk_cfi
    #process.muIsoDepositTkFiltered=muIsoDepositTk.clone()
    #muIsoDepositTkFiltered.IOPSet.inputMuonCollection = cms.InputTag("muons")
    #process.muIsoDepositTkFiltered.ExtractorPSet.Pt_Min = 1;
    
    #selectVetoLeptons4DetBasedIsolation(process)
        
    process.isoValMuonTkOptimized = cms.EDProducer("CandIsolatorFromDeposits",
      deposits = cms.VPSet(cms.PSet(
	mode = cms.string('sum'),
	src = cms.InputTag("muIsoDepositTk"),
	weight = cms.string('1'),
	deltaR = cms.double(0.3),
	vetos = cms.vstring('vetoMuons:0.015',
			'vetoElectrons:0.015',
			'Threshold(1.0)'),
	skipDefaultVeto = cms.bool(True)
      ))
    )

    process.isoValMuonTkOptimized5 = cms.EDProducer("CandIsolatorFromDeposits",
      deposits = cms.VPSet(cms.PSet(
	mode = cms.string('sum'),
	src = cms.InputTag("muIsoDepositTk"),
	weight = cms.string('1'),
	deltaR = cms.double(0.3),
	vetos = cms.vstring('vetoMuons:0.015',
			'vetoElectrons5:0.015',
			'Threshold(1.0)'),
	skipDefaultVeto = cms.bool(True)
      ))
    )


    process.isoValMuonEcalOptimized = cms.EDProducer("CandIsolatorFromDeposits",
      deposits = cms.VPSet(cms.PSet(
	mode = cms.string('sum'),
	src = cms.InputTag("muIsoDepositCalByAssociatorTowers","ecal"),
	weight = cms.string('1'),
	deltaR = cms.double(0.3),
	vetos = cms.vstring('vetoMuons:0.015',
			'vetoElectrons:0.015'),
	skipDefaultVeto = cms.bool(True)
      ))
    )

    process.isoValMuonHcalOptimized = cms.EDProducer("CandIsolatorFromDeposits",
      deposits = cms.VPSet(cms.PSet(
	mode = cms.string('sum'),
	src = cms.InputTag("muIsoDepositCalByAssociatorTowers","hcal"),
	weight = cms.string('1'),
	deltaR = cms.double(0.3),
	vetos = cms.vstring('vetoMuons:0.015',
			'vetoElectrons:0.015'),
	skipDefaultVeto = cms.bool(True)
      ))
    )
    
    #David Fsr muon isolation part
    
    #process.load("RecoMuon.MuonIsolationProducers.trackAssociatorBlocks_cff")
    #process.load("TrackingTools.TrackAssociator.default_cfi")
    from TrackingTools.TrackAssociator.default_cfi import TrackAssociatorParameterBlock

    FsrMIsoTrackAssociatorHits = cms.PSet(
        TrackAssociatorParameterBlock
    )
    FsrMIsoTrackAssociatorHits.TrackAssociatorParameters.useEcal = True ## RecoHits
    FsrMIsoTrackAssociatorHits.TrackAssociatorParameters.useHcal = False ## RecoHits
    FsrMIsoTrackAssociatorHits.TrackAssociatorParameters.useHO = False ## RecoHits
    FsrMIsoTrackAssociatorHits.TrackAssociatorParameters.useCalo = False ## CaloTowers
    FsrMIsoTrackAssociatorHits.TrackAssociatorParameters.useMuon = False ## RecoHits
    FsrMIsoTrackAssociatorHits.TrackAssociatorParameters.usePreshower = False
    FsrMIsoTrackAssociatorHits.TrackAssociatorParameters.dREcalPreselection = 1.0
    FsrMIsoTrackAssociatorHits.TrackAssociatorParameters.dRHcalPreselection = 1.0
    FsrMIsoTrackAssociatorHits.TrackAssociatorParameters.dREcal = 1.0
    FsrMIsoTrackAssociatorHits.TrackAssociatorParameters.dRHcal = 1.0
    FsrMIsoTrackAssociatorHits.TrackAssociatorParameters.EBRecHitCollectionLabel="reducedEcalRecHitsEB"
    FsrMIsoTrackAssociatorHits.TrackAssociatorParameters.EERecHitCollectionLabel="reducedEcalRecHitsEE"
    FsrMIsoTrackAssociatorHits.TrackAssociatorParameters.HBHERecHitCollectionLabel="HBHERecHitsSorted_reducedHcalRecHits_hbhereco"
    FsrMIsoTrackAssociatorHits.TrackAssociatorParameters.HORecHitCollectionLabel="HORecHitsSorted_reducedHcalRecHits_horeco"

    from RecoMuon.MuonIsolationProducers.isoDepositProducerIOBlocks_cff import MIsoDepositViewMultiIOBlock
    
    process.FsrMuIsoDepositCalByAssociatorHitsdr007 = cms.EDProducer("MuIsoDepositProducer",
        IOPSet = cms.PSet(
	  MIsoDepositViewMultiIOBlock   #from isoDepositProducerIOBlocks_cff
        ),
        ExtractorPSet = cms.PSet(
	  FsrMIsoTrackAssociatorHits,
	  Noise_HE = cms.double(0.2),
	  DR_Veto_H = cms.double(0.1),
	  Noise_EE = cms.double(0.025),
	  UseRecHitsFlag = cms.bool(True),
	  NoiseTow_EE = cms.double(0.15),
	  Threshold_HO = cms.double(0.1),
	  Noise_EB = cms.double(0.005),
	  Noise_HO = cms.double(0.2),
	  CenterConeOnCalIntersection = cms.bool(False),
	  DR_Max = cms.double(1.0),
	  PropagatorName = cms.string('SteppingHelixPropagatorAny'),
	  ServiceParameters = cms.PSet(
	      Propagators = cms.untracked.vstring( 'SteppingHelixPropagatorAny' ),
	      RPCLayers = cms.bool( False ),
	      UseMuonNavigation = cms.untracked.bool( False )
	  ),
	  Threshold_E = cms.double(0.04),
	  Noise_HB = cms.double(0.2),
	  NoiseTow_EB = cms.double(0.04),
	  PrintTimeReport = cms.untracked.bool(False),
	  Threshold_H = cms.double(0.1),
	  DR_Veto_E = cms.double(0.07),
	  DepositLabel = cms.untracked.string('Cal'),
	  ComponentName = cms.string('RecHitCaloExtractorByAssociator'),
	  DR_Veto_HO = cms.double(0.1),
	  DepositInstanceLabels = cms.vstring('ecal', 'hcal', 'ho')
	)
    )


    process.FsrMuIsoDepositCalByAssociatorHitsdr005=process.FsrMuIsoDepositCalByAssociatorHitsdr007.clone()
    process.FsrMuIsoDepositCalByAssociatorHitsdr005.ExtractorPSet.DR_Veto_E=0.05

    process.FsrMuIsoDepositCalByAssociatorHitsdr01=process.FsrMuIsoDepositCalByAssociatorHitsdr007.clone()
    process.FsrMuIsoDepositCalByAssociatorHitsdr01.ExtractorPSet.DR_Veto_E=0.1
    
    process.muIsoFromDepsEcaldr005 = cms.EDProducer("CandIsolatorFromDeposits",
	  deposits = cms.VPSet(cms.PSet(                                            
	    src = cms.InputTag("FsrMuIsoDepositCalByAssociatorHitsdr005","ecal"),
	    mode = cms.string('sum'),
	    weight = cms.string('1'),
	    deltaR = cms.double(0.3),
	    vetos = cms.vstring(),
	    skipDefaultVeto = cms.bool(True)
	    ))
    )

    process.muIsoFromDepsEcaldr007 = cms.EDProducer("CandIsolatorFromDeposits",
	  deposits = cms.VPSet(cms.PSet(                                            
	    src = cms.InputTag("FsrMuIsoDepositCalByAssociatorHitsdr007","ecal"),
	    mode = cms.string('sum'),
	    weight = cms.string('1'),
	    deltaR = cms.double(0.3),
	    vetos = cms.vstring(),
	    skipDefaultVeto = cms.bool(True)
	    ))
    )

    process.muIsoFromDepsEcaldr01 = cms.EDProducer("CandIsolatorFromDeposits",
	  deposits = cms.VPSet(cms.PSet(
	    mode = cms.string('sum'),
	    src = cms.InputTag("FsrMuIsoDepositCalByAssociatorHitsdr01","ecal"),
	    weight = cms.string('1'),
	    deltaR = cms.double(0.3),
	    vetos = cms.vstring(),
	    skipDefaultVeto = cms.bool(True)
	    ))
    )
    
    setattr(process,"DetBasedMuonIsoDepositsSequence"+postfix,
	  cms.Sequence(     
		  getattr(process,"FsrMuIsoDepositCalByAssociatorHitsdr005"+postfix) +
		  getattr(process,"FsrMuIsoDepositCalByAssociatorHitsdr007"+postfix) +
		  getattr(process,"FsrMuIsoDepositCalByAssociatorHitsdr01"+postfix) )	
    )

    setattr(process,"DetBasedMuonIsolationFromDepositsSequence"+postfix,
	  cms.Sequence(
		  #getattr(process,"isoVetoSeq"+postfix) +
		  getattr(process,"isoValMuonTkOptimized"+postfix) +
		  getattr(process,"isoValMuonTkOptimized5"+postfix) +
		  getattr(process,"isoValMuonEcalOptimized"+postfix) +
		  getattr(process,"isoValMuonHcalOptimized"+postfix) +
		  getattr(process,"muIsoFromDepsEcaldr005"+postfix) +
		  getattr(process,"muIsoFromDepsEcaldr007"+postfix) +
		  getattr(process,"muIsoFromDepsEcaldr01"+postfix)
		  
		  )	
    )
    #if not hasattr(process,'isoVetoSeq') :
####################################################################
def customizeDetBasedElectronIsolation(process,module,postfix="",verbose=False):
    #Code for the eISO
    process.load("RecoEgamma.EgammaIsolationAlgos.eleIsoDepositTk_cff")
    process.load("RecoEgamma.EgammaIsolationAlgos.eleIsoDepositEcalFromHits_cff")
    process.load("RecoEgamma.EgammaIsolationAlgos.eleIsoDepositHcalFromTowers_cff")

    #process.eleIsoDepositTk.src = "gsfElectrons"
    #process.eleIsoDepositEcalFromHits.src = "gsfElectrons"
    #process.eleIsoDepositHcalFromTowers.src = "gsfElectrons"
    
    #selectVetoLeptons4DetBasedIsolation(process)


    
    process.isoValElectronTkOptimized = cms.EDProducer("CandIsolatorFromDeposits",
      deposits = cms.VPSet(cms.PSet(
	mode = cms.string('sum'),
	src = cms.InputTag("eleIsoDepositTk"),
	weight = cms.string('1'),
	deltaR = cms.double(0.3),
	vetos = cms.vstring('vetoMuons:0.015', 
			'vetoElectrons:RectangularEtaPhiVeto(-0.015,0.015,-0.5,0.5)', 
			'RectangularEtaPhiVeto(-0.015,0.015,-0.5,0.5)', 
			'Threshold(0.7)'),
	skipDefaultVeto = cms.bool(True)
      ))
    )

    process.isoValElectronTkOptimized5 = cms.EDProducer("CandIsolatorFromDeposits",
      deposits = cms.VPSet(cms.PSet(
	mode = cms.string('sum'),
	src = cms.InputTag("eleIsoDepositTk"),
	weight = cms.string('1'),
	deltaR = cms.double(0.3),
	vetos = cms.vstring('vetoMuons:0.015', 
			'vetoElectrons5:RectangularEtaPhiVeto(-0.015,0.015,-0.5,0.5)', 
			'RectangularEtaPhiVeto(-0.015,0.015,-0.5,0.5)', 
			'Threshold(0.7)'),
	skipDefaultVeto = cms.bool(True)
      ))
    )


    process.isoValElectronEcalOptimized = cms.EDProducer("CandIsolatorFromDeposits",
      deposits = cms.VPSet(cms.PSet(
	mode = cms.string('sum'),
	src = cms.InputTag("eleIsoDepositEcalFromHits"),
	weight = cms.string('1'),
	deltaR = cms.double(0.3),
	vetos = cms.vstring('NumCrystalVeto(3.0)',
			'EcalBarrel:NumCrystalEtaPhiVeto(1.0,9999.0)',
			'EcalEndcaps:NumCrystalEtaPhiVeto(1.5,9999.0)',
			'EcalBarrel:AbsThresholdFromTransverse(0.08)',
			'EcalEndcaps:AbsThreshold(0.20)',
			'vetoMuons:0.05',
			'vetoElectrons:NumCrystalVeto(3.0)',
			'vetoElectrons:NumCrystalEtaPhiVeto(1.5,15.0)'),
	skipDefaultVeto = cms.bool(True)
      ))
    )
    process.isoValElectronHcalOptimized = cms.EDProducer("CandIsolatorFromDeposits",
      deposits = cms.VPSet(cms.PSet(
	src = cms.InputTag("eleIsoDepositHcalFromTowers"),
	deltaR = cms.double(0.4),
	weight = cms.string('1'),
	vetos = cms.vstring('0.15', 'vetoMuons:0.05'),
	skipDefaultVeto = cms.bool(True),
	mode = cms.string('sum')
      ))
    )   
    setattr(process,"DetBasedElectronIsoDepositsSequence"+postfix,
	  cms.Sequence(
		    getattr(process,"eleIsoDepositTk"+postfix) +
		    getattr(process,"eleIsoDepositEcalFromHits"+postfix) +
		    getattr(process,"eleIsoDepositHcalFromTowers"+postfix)
		    )
	  )
	  
    setattr(process,"DetBasedElectronIsolationFromDepositsSequence"+postfix,
	  cms.Sequence(
		    getattr(process,"isoVetoSeq"+postfix) +
		    getattr(process,"isoValElectronTkOptimized"+postfix) +
		    getattr(process,"isoValElectronTkOptimized5"+postfix) +
		    getattr(process,"isoValElectronEcalOptimized"+postfix) +
		    getattr(process,"isoValElectronHcalOptimized"+postfix)
		    )
	  )

####################################################################
def selectVetoLeptons4DetBasedIsolation(process, postfix=""):
     
    ELE_SOFT_CUT=( "pt>5" )     #used for candidates building
    ELE_ISOVETO_CUT=( "pt>7" )  #used for isoVeto
        #To be used for iso vetos, with present default of pt>7
    MUON_VETO_CUT=(  "isGlobalMuon &&" +
                 "pt>5"
                 #"((pt>5 && abs(eta)<1.2) || (p>9 && pt>3 && abs(eta)>=1.2 && abs(eta)<2.4))" #&&" +
                 ) #used for candidates building
    
    #veto leptons passing ID
    
    setattr(process,"vetoElectrons",
	        cms.EDFilter("GsfElectronRefSelector",
		  src = cms.InputTag("gsfElectrons"),
		  cut = cms.string(ELE_ISOVETO_CUT)
    )
    )

    #Additional veto for softer pT threshold
    setattr(process,"vetoElectrons5",
	        cms.EDFilter("GsfElectronRefSelector",
		  src = cms.InputTag("gsfElectrons"),
		  cut = cms.string(ELE_SOFT_CUT)
    )
    )
        # To be used for iso vetos
    setattr(process,"vetoMuons",
	        cms.EDFilter("MuonRefSelector",
		  src = cms.InputTag("muons"),
		  cut = cms.string(MUON_VETO_CUT)
    )
    )
    # ----------------------------------------------------------------------
    # Create collection for for vetos and for the cleaning 
    # ----------------------------------------------------------------------
    setattr(process,"isoVetoSeq", 
	        cms.Sequence(
		  process.vetoMuons +
		  process.vetoElectrons +
		  process.vetoElectrons5 
    )    
    )

    
####################################################################
def checkNames(kind, choices) :    
    if kind not in choices :
        try :
	  raise NameError('IsolationType')
        except NameError:
	  print "[ERROR] You must choose isolation string like ["+ choices+"], and not "+kind
	  raise
