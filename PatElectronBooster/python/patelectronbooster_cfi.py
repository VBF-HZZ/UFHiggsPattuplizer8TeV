import FWCore.ParameterSet.Config as cms

boostedElectrons = cms.EDProducer("PatElectronBooster",
                                  electronTag = cms.InputTag("cleanPatElectrons"),
                                  trackTag = cms.InputTag("generalTracks"),
                                  vertexTag = cms.InputTag("goodPrimaryVertices"),
                                  caloTowersTag = cms.InputTag("towerMaker"),
                                  )
