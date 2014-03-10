import FWCore.ParameterSet.Config as cms

from PhysicsTools.PatAlgos.tools.jetTools import *
from PhysicsTools.PatAlgos.tools.coreTools import *
from PhysicsTools.PatAlgos.tools.pfTools import *
from CommonTools.ParticleFlow.Isolation.tools_cfi import *
from CommonTools.ParticleFlow.Tools.pfIsolation import *
from CommonTools.ParticleFlow.Isolation.tools_cfi import *
from CommonTools.ParticleFlow.pfNoPileUp_cff import *
from CommonTools.ParticleFlow.Isolation.tools_cfi import *
from CommonTools.ParticleFlow.Isolation.pfElectronIsolationFromDeposits_cff import *
from CommonTools.ParticleFlow.Isolation.electronPFIsolationDeposits_cff import *


def startPFIso(process):



    process.eleIsoSequence = setupPFElectronIso(process, 'gsfElectrons')
    process.muIsoSequence = setupPFMuonIso(process, 'muons')
    process.phIsoSequence = setupPFPhotonIso(process,'photons')

    process.isoSequence = cms.Sequence(    process.pfParticleSelectionSequence *
                                           process.eleIsoSequence *
                                           process.muIsoSequence *
                                           process.phIsoSequence
                                           )
    

def addMuonPFIso(process,module):
    
    process.pfPileUpCandidates = cms.EDProducer(
        "TPPFCandidatesOnPFCandidates",
        enable =  cms.bool( True ),
        verbose = cms.untracked.bool( False ),
        name = cms.untracked.string("pileUpCandidates"),
        topCollection = cms.InputTag("pfNoPileUp"),
        bottomCollection = cms.InputTag("particleFlow"),
        )
    
    
    process.pfPUChargedCandidates = cms.EDFilter("PdgIdPFCandidateSelector",
                                                 src = cms.InputTag("pfPileUpCandidates"),
                                                 pdgId = cms.vint32(211,-211,321,-321,999211,2212,-2212) #electrons + muons too?
                                                 )
    
    
    process.pfAllChargedCandidates = cms.EDFilter("PdgIdPFCandidateSelector",
                                                  src = cms.InputTag("pfNoPileUp"),
                                                  pdgId = cms.vint32(211,-211,321,-321,999211,2212,-2212,11,-11,13,-13)
                                                  )
    
    
    process.muonPrePFIsolationSequence =  cms.Sequence(#pfCandsForIsolationSequence +
                                                       process.pfPileUpCandidates +
                                                       process.pfPUChargedCandidates +
                                                       process.pfAllChargedCandidates
                                                       )  
    
    
    process.muPFIsoDepositAll     = isoDepositReplace('muons',"pfNoPileUp")
    process.muPFIsoDepositCharged = isoDepositReplace('muons',"pfAllChargedHadrons")
    process.muPFIsoDepositNeutral = isoDepositReplace('muons',"pfAllNeutralHadrons")
    process.muPFIsoDepositGamma = isoDepositReplace('muons',"pfAllPhotons")
    
    process.muPFIsoDepositPU = isoDepositReplace('muons',cms.InputTag("pfPUChargedCandidates"))
    
    process.muPFIsoDeposits = cms.Sequence(
        process.muPFIsoDepositAll*
        process.muPFIsoDepositCharged*
        process.muPFIsoDepositPU*
        process.muPFIsoDepositNeutral*
        process.muPFIsoDepositGamma
        )
    
    process.muPFIsoValueAll = cms.EDProducer("CandIsolatorFromDeposits",
                                             deposits = cms.VPSet(
        cms.PSet(
        src = cms.InputTag("muPFIsoDepositAll"),
        deltaR = cms.double(0.4),
        weight = cms.string('1'),
        vetos = cms.vstring('0.0001','Threshold(0.5)'),
        skipDefaultVeto = cms.bool(True),
        mode = cms.string('sum')
        )
        )
                                             )
    
    process.muPFIsoValueCharged = cms.EDProducer("CandIsolatorFromDeposits",
                                                 deposits = cms.VPSet(
        cms.PSet(
        src = cms.InputTag("muPFIsoDepositCharged"),
        deltaR = cms.double(0.4),
        weight = cms.string('1'),
        vetos = cms.vstring('0.0001','Threshold(0.0)'),
        skipDefaultVeto = cms.bool(True),
        mode = cms.string('sum')
        )
        )
                                                 )
    
    process.muPFIsoValueNeutral = cms.EDProducer("CandIsolatorFromDeposits",
                                                 deposits = cms.VPSet(
        cms.PSet(
        src = cms.InputTag("muPFIsoDepositNeutral"),
        deltaR = cms.double(0.4),
        weight = cms.string('1'),
        vetos = cms.vstring('0.01','Threshold(0.5)'),
        skipDefaultVeto = cms.bool(True),
        mode = cms.string('sum')
        )
        )
                                                 )
    
    process.muPFIsoValueGamma = cms.EDProducer("CandIsolatorFromDeposits",
                                               deposits = cms.VPSet(
        cms.PSet(
        src = cms.InputTag("muPFIsoDepositGamma"),
        deltaR = cms.double(0.4),
        weight = cms.string('1'),
        vetos = cms.vstring('0.01','Threshold(0.5)'),
        skipDefaultVeto = cms.bool(True),
        mode = cms.string('sum')
        )
        )
                                               )
    
    process.muPFIsoValuePU = cms.EDProducer("CandIsolatorFromDeposits",
                                            deposits = cms.VPSet(
        cms.PSet(
        src = cms.InputTag("muPFIsoDepositPU"),
        deltaR = cms.double(0.4),
        weight = cms.string('1'),
        vetos = cms.vstring('0.01','Threshold(0.5)'),
        skipDefaultVeto = cms.bool(True),
        mode = cms.string('sum')
        )
        )
                                            )
    
    process.muPFIsoValuePULow = cms.EDProducer("CandIsolatorFromDeposits",
                                               deposits = cms.VPSet(
        cms.PSet(
        src = cms.InputTag("muPFIsoDepositPU"),
        deltaR = cms.double(0.4),
        weight = cms.string('1'),
        vetos = cms.vstring('0.01','Threshold(0.0)'),
        skipDefaultVeto = cms.bool(True),
        mode = cms.string('sum')
        )
        )
                                               )
    
    
    process.muPFIsoValueAll03 = process.muPFIsoValueAll.clone(deltaR = cms.double(0.3))
    process.muPFIsoValueCharged03 = process.muPFIsoValueCharged.clone(deltaR = cms.double(0.3))
    process.muPFIsoValueNeutral03 = process.muPFIsoValueNeutral.clone(deltaR = cms.double(0.3))
    process.muPFIsoValueGamma03 = process.muPFIsoValueGamma.clone(deltaR = cms.double(0.3))
    process.muPFIsoValuePU03 = process.muPFIsoValuePU.clone(deltaR = cms.double(0.3))
    process.muPFIsoValuePULow03 = process.muPFIsoValuePULow.clone(deltaR = cms.double(0.3))
        
    
    process.muPFIsoValues =  cms.Sequence( process.muPFIsoValueAll
                                           * process.muPFIsoValueCharged
                                           * process.muPFIsoValueNeutral
                                           * process.muPFIsoValueGamma
                                           * process.muPFIsoValuePU
                                           * process.muPFIsoValuePULow
                                           * process.muPFIsoValueAll03
                                           * process.muPFIsoValueCharged03
                                           * process.muPFIsoValueNeutral03
                                           * process.muPFIsoValueGamma03
                                           * process.muPFIsoValuePU03
                                           * process.muPFIsoValuePULow03
                                           )
    
    process.muisolationPrePat = cms.Sequence(
        process.muPFIsoDeposits*
        process.muPFIsoValues
        )
    
        
    module.isoDeposits = cms.PSet(
        particle         = cms.InputTag("muPFIsoDepositAll"),
        pfChargedHadrons = cms.InputTag("muPFIsoDepositCharged"),
        pfNeutralHadrons = cms.InputTag("muPFIsoDepositNeutral"),
        pfPhotons        = cms.InputTag("muPFIsoDepositGamma")
        )
    
    module.isolationValues = cms.PSet(
        particle         = cms.InputTag("muPFIsoValueAll"),
        pfChargedHadrons = cms.InputTag("muPFIsoValueCharged"),
        pfNeutralHadrons = cms.InputTag("muPFIsoValueNeutral"),
        pfPhotons        = cms.InputTag("muPFIsoValueGamma"),
        user = cms.VInputTag(
        cms.InputTag("muPFIsoValuePU"),
        cms.InputTag("muPFIsoValuePULow"),
        cms.InputTag("muPFIsoValueAll03"),
        cms.InputTag("muPFIsoValueCharged03"),
        cms.InputTag("muPFIsoValueNeutral03"),
        cms.InputTag("muPFIsoValueGamma03"),
        cms.InputTag("muPFIsoValuePU03"),
        cms.InputTag("muPFIsoValuePULow03"),
        )
        
        )
    
    process.patSeq = process.patDefaultSequence
    process.patDefaultSequence = cms.Sequence(process.muonPrePFIsolationSequence * process.muisolationPrePat * process.patSeq)


#############################################################################


def addElectronPFIso(process,module):

    sourceElectrons = 'gsfElectrons'
    
    process.elPFIsoDepositCharged.src = sourceElectrons
    process.elPFIsoDepositChargedAll.src = sourceElectrons
    process.elPFIsoDepositNeutral.src = sourceElectrons
    process.elPFIsoDepositGamma.src = sourceElectrons
    process.elPFIsoDepositPU.src = sourceElectrons

    process.isoDepElectronWithCharged.src = sourceElectrons
    process.isoDepElectronWithNeutral.src = sourceElectrons
    process.isoDepElectronWithPhotons.src = sourceElectrons

    process.pfElectronIsoDepositsSequence = cms.Sequence(
        process.isoDepElectronWithCharged   +
        process.isoDepElectronWithNeutral   +
        process.isoDepElectronWithPhotons
        )

    
    
    
    process.elPFIsoValueCharged03PFId = cms.EDProducer("CandIsolatorFromDeposits",
                                               deposits = cms.VPSet(
        cms.PSet(
        src = cms.InputTag("elPFIsoDepositCharged"),
        deltaR = cms.double(0.3),
        weight = cms.string('1'),
        vetos = cms.vstring('EcalEndcaps:ConeVeto(0.015)'),
        skipDefaultVeto = cms.bool(True),
        mode = cms.string('sum'),
        PivotCoordinatesForEBEE = cms.bool(True)
        )
        )
                                               )
    
    process.elPFIsoValueChargedAll03PFId = cms.EDProducer("CandIsolatorFromDeposits",
                                                  deposits = cms.VPSet(
        cms.PSet(
        src = cms.InputTag("elPFIsoDepositChargedAll"),
        deltaR = cms.double(0.3),
        weight = cms.string('1'),
        vetos = cms.vstring('EcalEndcaps:ConeVeto(0.015)'),
        skipDefaultVeto = cms.bool(True),
        mode = cms.string('sum'),
        PivotCoordinatesForEBEE = cms.bool(True)
        )
        )
                                                  )
    
    process.elPFIsoValueGamma03PFId = cms.EDProducer("CandIsolatorFromDeposits",
                                             deposits = cms.VPSet(
        cms.PSet(
        src = cms.InputTag("elPFIsoDepositGamma"),
        deltaR = cms.double(0.3),
        weight = cms.string('1'),
        vetos = cms.vstring('EcalEndcaps:ConeVeto(0.08)'),
        skipDefaultVeto = cms.bool(True),
        mode = cms.string('sum'),
        PivotCoordinatesForEBEE = cms.bool(True)
        )
        )
                                             )
    
    process.elPFIsoValueNeutral03PFId = cms.EDProducer("CandIsolatorFromDeposits",
                                               deposits = cms.VPSet(
        cms.PSet(
        src = cms.InputTag("elPFIsoDepositNeutral"),
        deltaR = cms.double(0.3),
        weight = cms.string('1'),
        vetos = cms.vstring(),
        skipDefaultVeto = cms.bool(True),
        mode = cms.string('sum'),
        PivotCoordinatesForEBEE = cms.bool(True)
        )
        )
                                               )
    
    process.elPFIsoValuePU03PFId = cms.EDProducer("CandIsolatorFromDeposits",
                                          deposits = cms.VPSet(
        cms.PSet(
        src = cms.InputTag("elPFIsoDepositPU"),
        deltaR = cms.double(0.3),
        weight = cms.string('1'),
        vetos = cms.vstring('EcalEndcaps:ConeVeto(0.015)'),
        skipDefaultVeto = cms.bool(True),
        mode = cms.string('sum'),
        PivotCoordinatesForEBEE = cms.bool(True)
        )
        )
                                          )
    
    
    
    process.elPFIsoValueCharged04PFId = process.elPFIsoValueCharged03PFId.clone()
    process.elPFIsoValueCharged04PFId.deposits[0].deltaR = cms.double(0.4)
    
    
    process.elPFIsoValueChargedAll04PFId = process.elPFIsoValueChargedAll03PFId.clone()
    process.elPFIsoValueChargedAll04PFId.deposits[0].deltaR = cms.double(0.4)
    
    process.elPFIsoValueGamma04PFId = process.elPFIsoValueGamma03PFId.clone()
    process.elPFIsoValueGamma04PFId.deposits[0].deltaR = cms.double(0.4)
    
    
    process.elPFIsoValueNeutral04PFId = process.elPFIsoValueNeutral03PFId.clone()
    process.elPFIsoValueNeutral04PFId.deposits[0].deltaR = cms.double(0.4)
    
    process.elPFIsoValuePU04PFId = process.elPFIsoValuePU03PFId.clone()
    process.elPFIsoValuePU04PFId.deposits[0].deltaR = cms.double(0.4)
    
    process.elPFIsoValueCharged03NoPFId     =  process.elPFIsoValueCharged03PFId.clone()           
    process.elPFIsoValueChargedAll03NoPFId  =  process.elPFIsoValueChargedAll03PFId.clone()
    process.elPFIsoValueGamma03NoPFId       =  process.elPFIsoValueGamma03PFId.clone()         
    process.elPFIsoValueNeutral03NoPFId     =  process.elPFIsoValueNeutral03PFId.clone()       
    process.elPFIsoValuePU03NoPFId          =  process.elPFIsoValuePU03PFId.clone()            
    
    process.elPFIsoValueCharged04NoPFId     =  process.elPFIsoValueCharged04PFId.clone()       
    process.elPFIsoValueChargedAll04NoPFId  =  process.elPFIsoValueChargedAll04PFId.clone()    
    process.elPFIsoValueGamma04NoPFId       =  process.elPFIsoValueGamma04PFId.clone()         
    process.elPFIsoValueNeutral04NoPFId     =  process.elPFIsoValueNeutral04PFId.clone()       
    process.elPFIsoValuePU04NoPFId          =  process.elPFIsoValuePU04PFId.clone()            
    
    process.electronPFIsolationValuesSequence = cms.Sequence(
        process.elPFIsoValueCharged03PFId+
        process.elPFIsoValueChargedAll03PFId+
        process.elPFIsoValueGamma03PFId+
        process.elPFIsoValueNeutral03PFId+
        process.elPFIsoValuePU03PFId+
        ############################## 
        process.elPFIsoValueCharged04PFId+
        process.elPFIsoValueChargedAll04PFId+
        process.elPFIsoValueGamma04PFId+
        process.elPFIsoValueNeutral04PFId+
        process.elPFIsoValuePU04PFId+
        ############################## 
        process.elPFIsoValueCharged03NoPFId+
        process.elPFIsoValueChargedAll03NoPFId+
        process.elPFIsoValueGamma03NoPFId+
        process.elPFIsoValueNeutral03NoPFId+
        process.elPFIsoValuePU03NoPFId+
        ############################## 
        process.elPFIsoValueCharged04NoPFId+
        process.elPFIsoValueChargedAll04NoPFId+
        process.elPFIsoValueGamma04NoPFId+
        process.elPFIsoValueNeutral04NoPFId+
        process.elPFIsoValuePU04NoPFId
        )
    
    
    
    process.pfElectronIsolationSequence = cms.Sequence(
        process.pfElectronIsoDepositsSequence +
        process.pfElectronIsolationFromDepositsSequence +
        process.electronPFIsolationDepositsSequence +
        process.electronPFIsolationValuesSequence
        )
    

    module.isolationValues = cms.PSet(
        pfChargedHadrons = cms.InputTag("elPFIsoValueCharged04PFIdPFIso"),
        pfChargedAll = cms.InputTag("elPFIsoValueChargedAll04PFIdPFIso"),
        pfPUChargedHadrons = cms.InputTag("elPFIsoValuePU04PFIdPFIso"),
        pfNeutralHadrons = cms.InputTag("elPFIsoValueNeutral04PFIdPFIso"),
        pfPhotons = cms.InputTag("elPFIsoValueGamma04PFIdPFIso")
        )
    module.isolationValuesNoPFId = cms.PSet(
        pfChargedHadrons = cms.InputTag("elPFIsoValueCharged04NoPFIdPFIso"),
        pfChargedAll = cms.InputTag("elPFIsoValueChargedAll04NoPFIdPFIso"),
        pfPUChargedHadrons = cms.InputTag("elPFIsoValuePU04NoPFIdPFIso"),
        pfNeutralHadrons = cms.InputTag("elPFIsoValueNeutral04NoPFIdPFIso"),
        pfPhotons = cms.InputTag("elPFIsoValueGamma04NoPFIdPFIso")
        )
    
    process.pfElectronIsolationSequence.remove( process.pfElectronIsoDepositsSequence )
    process.pfElectronIsolationSequence.remove( process.pfElectronIsolationFromDepositsSequence )  
    process.patEleIsoSeq = process.patDefaultSequence
    process.patDefaultSequence = cms.Sequence(
        process.pfElectronIsoDepositsSequence *
        process.pfElectronIsolationSequence *
        process.patEleIsoSeq
        )


