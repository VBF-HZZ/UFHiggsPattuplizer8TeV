// -*- C++ -*-
//
// Package:    FSRPhotonProducer
// Class:      FSRPhotonProducer
// 
/**\class FSRPhotonProducer FSRPhotonProducer.cc WWAnalysis/FSRPhotonProducer/src/FSRPhotonProducer.cc

Description: [one line class summary]

Implementation:
[Notes on implementation]
 */
//
// Original Author:  
//         Created:  Mon Jun 13 00:56:48 CEST 2011
// $Id: FSRPhotonProducer.cc,v 1.1 2012/10/04 15:18:23 snowball Exp $
//
//


// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "DataFormats/Candidate/interface/Candidate.h"
#include "DataFormats/ParticleFlowCandidate/interface/PFCandidate.h"
#include "DataFormats/ParticleFlowCandidate/interface/PFCandidateFwd.h"

#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include <DataFormats/MuonReco/interface/Muon.h>
#include <DataFormats/GsfTrackReco/interface/GsfTrack.h>

namespace reco { typedef std::vector<reco::PFCandidate> PFCandidateCollection; }
//
// class declaration
//

class FSRPhotonProducer : public edm::EDProducer {
    public:
        explicit FSRPhotonProducer(const edm::ParameterSet&);
        ~FSRPhotonProducer();

    private:
        virtual void produce(edm::Event&, const edm::EventSetup&);
        // ----------member data ---------------------------
        edm::InputTag srcCands_;
        double ptThresh_;
        bool   extractMuonFSR_;
};

//
// constants, enums and typedefs
//


//
// static data member definitions
//

//
// constructors and destructor
//
FSRPhotonProducer::FSRPhotonProducer(const edm::ParameterSet& iConfig):
    srcCands_( iConfig.getParameter<edm::InputTag>("srcCands") ),
    ptThresh_( iConfig.getParameter<double>("ptThresh") ),
    extractMuonFSR_(iConfig.getParameter<bool>("extractMuonFSR"))
{
    using namespace reco;
    produces<PFCandidateCollection>(); 
}


FSRPhotonProducer::~FSRPhotonProducer()
{
}


//
// member functions
//

// ------------ method called to produce the data  ------------
    void
FSRPhotonProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    using namespace edm;
    using namespace std;
    using namespace reco; 
    std::auto_ptr<PFCandidateCollection> comp( new PFCandidateCollection );

    Handle<PFCandidateCollection>   cands;
    iEvent.getByLabel( srcCands_, cands );

    for( PFCandidateCollection::const_iterator c = cands->begin(); c != cands->end(); ++c ) {
        if (c->charge()==0 && c->pdgId() == 22 && c->pt() > ptThresh_)  {
            //std::auto_ptr<Candidate> cand( new PFCandidate( * c ) );
            //comp->push_back( cand.release() );
            comp->push_back( *c );
            comp->back().setStatus(0);
        }
        if (extractMuonFSR_ && abs(c->pdgId()) == 13) {
            if (c->ecalEnergy() > 0) { 
               // Proper version, with massless photons (but still using the muon direction)
               Particle::PolarLorentzVector p4(c->ecalEnergy() * c->pt()/c->p(), c->eta(), c->phi(), 0.);
               // Improper version below, with massive photons (precise copy of Patrick's code)
               // reco::Particle::LorentzVector p4 = c->p4(); p4 *= c->ecalEnergy()/c->energy();
               if (p4.pt() > ptThresh_) {
                   comp->push_back( PFCandidate(0, Particle::LorentzVector(p4), PFCandidate::gamma) );
               }
            }
        }
    }

    iEvent.put( comp );
}


//define this as a plug-in
DEFINE_FWK_MODULE(FSRPhotonProducer);
