import FWCore.ParameterSet.Config as cms

pfMuId = cms.EDProducer('MuonPFIDMapProd',
    muonLabel = cms.untracked.InputTag("muons"),
    pfLabel = cms.untracked.InputTag("particleFlow"),
)

