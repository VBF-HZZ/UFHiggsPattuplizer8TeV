#include <memory>

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "DataFormats/MuonReco/interface/Muon.h"
#include "DataFormats/MuonReco/interface/MuonFwd.h"
#include "DataFormats/ParticleFlowCandidate/interface/PFCandidate.h"
#include "DataFormats/ParticleFlowCandidate/interface/PFCandidateFwd.h"

#include "DataFormats/Common/interface/ValueMap.h"

class MuonPFIDMapProd : public edm::EDProducer {
    public:
        explicit MuonPFIDMapProd(const edm::ParameterSet&);
        ~MuonPFIDMapProd();

    private:
        virtual void beginJob() ;
        virtual void produce(edm::Event&, const edm::EventSetup&);
        virtual void endJob() ;

        edm::InputTag muonLabel_;
        edm::InputTag pfLabel_;

};



MuonPFIDMapProd::MuonPFIDMapProd(const edm::ParameterSet& iConfig) :
    muonLabel_(iConfig.getUntrackedParameter<edm::InputTag>("muonLabel")),
    pfLabel_(iConfig.getUntrackedParameter<edm::InputTag>("pfLabel")) {

    produces<edm::ValueMap<int> >().setBranchAlias("pfMuId");
}

void MuonPFIDMapProd::produce(edm::Event& iEvent, const edm::EventSetup& iSetup) {
    edm::Handle<reco::MuonCollection> muH;
    iEvent.getByLabel(muonLabel_,muH);

    edm::Handle<reco::PFCandidateCollection> pfH;
    iEvent.getByLabel(pfLabel_,pfH);

    std::vector<int> isoV(muH->size(), 0);
    std::auto_ptr<edm::ValueMap<int> > isoM(new edm::ValueMap<int> ());
    edm::ValueMap<int>::Filler isoF(*isoM);

    for (reco::PFCandidateCollection::const_iterator it = pfH->begin(), ed = pfH->end(); it != ed; ++it) {
        const reco::MuonRef ref = it->muonRef();
        if (ref.isNonnull() && abs(it->pdgId()) == 13) {
            if (ref.id() != muH.id()) throw cms::Exception("Configuration") << "Error: PF Candidate muon ref is " << ref.id() << " while muons are " << muH.id() << "\n";
            isoV[ref.key()] = 1;
        }
    }

    isoF.insert(muH,isoV.begin(),isoV.end());

    isoF.fill();
    iEvent.put(isoM);

}

MuonPFIDMapProd::~MuonPFIDMapProd() { }
void MuonPFIDMapProd::beginJob() { }
void MuonPFIDMapProd::endJob() { }
DEFINE_FWK_MODULE(MuonPFIDMapProd);
