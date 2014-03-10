// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include <DataFormats/PatCandidates/interface/Electron.h>

#include <DataFormats/Common/interface/ValueMap.h>

#include <DataFormats/VertexReco/interface/Vertex.h>
#include <DataFormats/VertexReco/interface/VertexFwd.h>


#include "TrackingTools/IPTools/interface/IPTools.h"
#include "TrackingTools/TransientTrack/interface/TransientTrack.h"
#include "TrackingTools/TransientTrack/interface/TransientTrackBuilder.h"
#include "TrackingTools/Records/interface/TransientTrackRecord.h"

#include "RecoVertex/GaussianSumVertexFit/interface/GsfVertexTrackCompatibilityEstimator.h"
#include "CommonTools/UtilAlgos/interface/MatchByDRDPt.h"

// Variables for regression
#include "DataFormats/CaloTowers/interface/CaloTowerCollection.h"
#include "DataFormats/DetId/interface/DetId.h"
#include "DataFormats/EcalRecHit/interface/EcalRecHitCollections.h"
#include "DataFormats/CaloRecHit/interface/CaloCluster.h"
#include "DataFormats/EgammaReco/interface/BasicCluster.h"
#include "DataFormats/EgammaReco/interface/SuperClusterFwd.h"
#include "DataFormats/EgammaReco/interface/SuperCluster.h"
#include "DataFormats/CaloTowers/interface/CaloTowerCollection.h"
#include "RecoEgamma/EgammaTools/interface/EcalClusterLocal.h"
#include "DataFormats/EcalDetId/interface/EBDetId.h"
#include "DataFormats/EcalDetId/interface/EEDetId.h"
#include "RecoEgamma/EgammaIsolationAlgos/interface/EgammaTowerIsolation.h"
#include "Geometry/CaloGeometry/interface/CaloGeometry.h"
#include "Geometry/CaloTopology/interface/CaloTopology.h"
#include "Geometry/Records/interface/CaloGeometryRecord.h"
#include "Geometry/CaloEventSetup/interface/CaloTopologyRecord.h"
#include "RecoEcal/EgammaCoreTools/interface/EcalClusterTools.h"
#include "RecoEcal/EgammaCoreTools/interface/EcalClusterFunctionFactory.h"
#include "RecoEcal/EgammaCoreTools/interface/EcalClusterFunctionBaseClass.h"
#include "RecoEcal/EgammaCoreTools/interface/PositionCalc.h"


#include<vector>

//for sim-reco IP bias
#include "SimTracker/Records/interface/TrackAssociatorRecord.h"
#include "SimTracker/TrackAssociation/plugins/ParametersDefinerForTPESProducer.h"

#include "Math/VectorUtil.h"
#include "DataFormats/Math/interface/deltaPhi.h"

//
// class declaration
//

class PatElectronBooster : public edm::EDProducer {
    public:
        explicit PatElectronBooster(const edm::ParameterSet&);
        ~PatElectronBooster();

    private:
        virtual void beginJob() ;
        virtual void produce(edm::Event&, const edm::EventSetup&);
        virtual void endJob() ;

        void setIPs(const pat::ElectronRef elecsRef,
		    edm::Handle<reco::VertexCollection> vertices,
		    reco::TransientTrack tt,
		    edm::Event& iEvent,
		    const edm::EventSetup& iSetup,
		    pat::Electron& clone);

        template <class T> T findClosestVertex(const double zPos, 
                const std::vector<T>& vtxs);

        // ----------member data ---------------------------
        edm::InputTag electronTag_;
        edm::InputTag trackTag_;
        edm::InputTag vertexTag_;
        edm::InputTag caloTowersTag_;
        edm::InputTag ecalBarrelRecHitProducer_;
        edm::InputTag ecalEndcapRecHitProducer_;

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
PatElectronBooster::PatElectronBooster(const edm::ParameterSet& iConfig) :
        electronTag_(iConfig.getParameter<edm::InputTag>("electronTag")),
        trackTag_(iConfig.getParameter<edm::InputTag>("trackTag")),
        vertexTag_(iConfig.getParameter<edm::InputTag>("vertexTag")),
        caloTowersTag_(iConfig.getParameter<edm::InputTag>("caloTowersTag")),
        ecalBarrelRecHitProducer_(iConfig.getUntrackedParameter<edm::InputTag>("barrelHits",edm::InputTag("reducedEcalRecHitsEB"))),
        ecalEndcapRecHitProducer_(iConfig.getUntrackedParameter<edm::InputTag>("endcapHits",edm::InputTag("reducedEcalRecHitsEE")))
{
  produces<pat::ElectronCollection>();  

}


PatElectronBooster::~PatElectronBooster() {

}


void PatElectronBooster::produce(edm::Event& iEvent, const edm::EventSetup& iSetup) {
    using namespace edm;
    using namespace std;


    ESHandle<TransientTrackBuilder> theTTBuilder;
    iSetup.get<TransientTrackRecord>().get("TransientTrackBuilder",theTTBuilder);

    edm::Handle<reco::TrackCollection > tkH;
    iEvent.getByLabel(trackTag_,tkH);

    edm::Handle<edm::View<reco::Candidate> > electrons;
    iEvent.getByLabel(electronTag_,electrons);

    edm::Handle<reco::VertexCollection> vertices;
    iEvent.getByLabel(vertexTag_,vertices);

    edm::Handle<CaloTowerCollection> calotowersH;
    iEvent.getByLabel(caloTowersTag_, calotowersH);


    edm::ESHandle<CaloTopology> pTopology;
    iSetup.get<CaloTopologyRecord>().get(pTopology);
    const CaloTopology *topology = pTopology.product();

    edm::ESHandle<CaloGeometry> pGeometry;
    iSetup.get<CaloGeometryRecord>().get(pGeometry);

    // Next get Ecal hits barrel
    edm::Handle<EcalRecHitCollection> ecalBarrelRecHitHandle; 
    iEvent.getByLabel(ecalBarrelRecHitProducer_,ecalBarrelRecHitHandle);
    edm::Handle<EcalRecHitCollection> ecalEndcapRecHitHandle;
    iEvent.getByLabel(ecalEndcapRecHitProducer_,ecalEndcapRecHitHandle);


    std::auto_ptr<pat::ElectronCollection> pOut(new pat::ElectronCollection);



    // ----- here is the real loop over the electrons ----
    for(edm::View<reco::Candidate>::const_iterator ele=electrons->begin(); ele!=electrons->end(); ++ele){    
        const pat::ElectronRef elecsRef = edm::RefToBase<reco::Candidate>(electrons,ele-electrons->begin()).castTo<pat::ElectronRef>();
        pat::Electron clone = *edm::RefToBase<reco::Candidate>(electrons,ele-electrons->begin()).castTo<pat::ElectronRef>();
        reco::TransientTrack tt = theTTBuilder->build(elecsRef->gsfTrack());

	setIPs(elecsRef,vertices,tt,iEvent,iSetup,clone);


	// -----------

        const reco::CandidateBaseRef elecsRef2(electrons,ele-electrons->begin());


        float num0003 = 0, num0004 = 0, num0703 = 0, num0704 = 0;
        float den0003 = 0, den0004 = 0, den0703 = 0, den0704 = 0;
        for(size_t k=0;k<tkH->size();++k) {
            reco::TrackRef tk(tkH,k);
            if( fabs(tk->eta()-elecsRef->gsfTrack()->eta()) < 0.015) 
                continue;
            //All tracks 0.3
            if( ROOT::Math::VectorUtil::DeltaR(tk->momentum(),elecsRef->gsfTrack()->momentum()) < 0.3 ) {
                den0003 += tk->pt();
                if( fabs( elecsRef->gsfTrack()->dz(tk->vertex()) ) < 0.2 ) 
                    num0003 += tk->pt();
            }
            //All tracks 0.4
            if( ROOT::Math::VectorUtil::DeltaR(tk->momentum(),elecsRef->gsfTrack()->momentum()) < 0.4 ) {
                den0004 += tk->pt();
                if( fabs( elecsRef->gsfTrack()->dz(tk->vertex()) ) < 0.2 ) 
                    num0004 += tk->pt();
            }
            if(tk->pt() < 0.7) continue;
            //pt>0.7 tracks 0.3
            if( ROOT::Math::VectorUtil::DeltaR(tk->momentum(),elecsRef->gsfTrack()->momentum()) < 0.3 ) {
                den0703 += tk->pt();
                if( fabs( elecsRef->gsfTrack()->dz(tk->vertex()) ) < 0.2 ) 
                    num0703 += tk->pt();
            }
            //pt>0.7 tracks 0.4
            if( ROOT::Math::VectorUtil::DeltaR(tk->momentum(),elecsRef->gsfTrack()->momentum()) < 0.4 ) {
                den0704 += tk->pt();
                if( fabs( elecsRef->gsfTrack()->dz(tk->vertex()) ) < 0.2 ) 
                    num0704 += tk->pt();
            }
        }
        //std::cout << num0003 << " " << den0003 << " " << num0003/den0003 << std::endl;
        clone.addUserFloat("beta0003",((den0003==0)?1:num0003/den0003));
        clone.addUserFloat("beta0004",((den0004==0)?1:num0004/den0004));
        clone.addUserFloat("beta0703",((den0703==0)?1:num0703/den0703));
        clone.addUserFloat("beta0704",((den0704==0)?1:num0704/den0704));

        float iphiiphi;
        if( fabs(clone.eta()) < 1.479 ) 
            iphiiphi = EcalClusterTools::localCovariances(*clone.superCluster()->seed(),&(*ecalBarrelRecHitHandle.product()),topology)[2];
        else
            iphiiphi = EcalClusterTools::localCovariances(*clone.superCluster()->seed(),&(*ecalEndcapRecHitHandle.product()),topology)[2];
            
        clone.addUserFloat("sigmaIphiIphi",sqrt(iphiiphi));


    // Variables for regression
    // Code adapted from /UserCode/HiggsAnalysis/HiggsToWW2e/src/CmsSuperClusterFiller.cc

    clone.addUserInt("nBC", (int)clone.superCluster()->clustersSize());
    clone.addUserInt("nCrystals", (int)clone.superCluster()->hitsAndFractions().size());
    clone.addUserFloat("rawEnergy", (float)clone.superCluster()->rawEnergy());
    clone.addUserFloat("seedClusterEnergy", (float)clone.superCluster()->seed()->energy());
    clone.addUserFloat("seedClusterEta", (float)clone.superCluster()->seed()->eta());
    clone.addUserFloat("seedClusterPhi", (float)clone.superCluster()->seed()->phi());
    clone.addUserFloat("energy", (float)clone.superCluster()->energy());
    clone.addUserFloat("esEnergy", (float)clone.superCluster()->preshowerEnergy());
    clone.addUserFloat("phiWidth", (float)clone.superCluster()->phiWidth());
    clone.addUserFloat("etaWidth", (float)clone.superCluster()->etaWidth());
    clone.addUserFloat("eta", (float)clone.superCluster()->position().eta());
    clone.addUserFloat("theta", (float)clone.superCluster()->position().theta());
    clone.addUserFloat("phi", (float)clone.superCluster()->position().phi());

      const EcalRecHitCollection *rechits = 0;

      // seed crystal properties
      const Ptr<reco::CaloCluster> theSeed = clone.superCluster()->seed();

      float seedEta = theSeed->position().eta();

      if( fabs(seedEta) < 1.479 ) rechits = &(*ecalBarrelRecHitHandle);
      else rechits = &(*ecalEndcapRecHitHandle);

      clone.addUserFloat("eMax", EcalClusterTools::eMax( *theSeed, &(*rechits) ));
      clone.addUserFloat("e3x3", EcalClusterTools::e3x3( *theSeed, &(*rechits), topology ));
      clone.addUserFloat("e5x5", EcalClusterTools::e5x5( *theSeed, &(*rechits), topology ));
      clone.addUserFloat("e2x2", EcalClusterTools::e2x2( *theSeed, &(*rechits), topology ));
      clone.addUserFloat("e2nd", EcalClusterTools::e2nd( *theSeed, &(*rechits) ));
      clone.addUserFloat("e1x5", EcalClusterTools::e1x5( *theSeed, &(*rechits), topology ));
      clone.addUserFloat("e2x5Max", EcalClusterTools::e2x5Max( *theSeed, &(*rechits), topology ));
      clone.addUserFloat("e2x5Left", EcalClusterTools::e2x5Left( *theSeed, &(*rechits), topology ));
      clone.addUserFloat("e2x5Right", EcalClusterTools::e2x5Right( *theSeed, &(*rechits), topology ));
      clone.addUserFloat("e2x5Top", EcalClusterTools::e2x5Top( *theSeed, &(*rechits), topology ));
      clone.addUserFloat("e2x5Bottom", EcalClusterTools::e2x5Bottom( *theSeed, &(*rechits), topology ));
      clone.addUserFloat("eLeft", EcalClusterTools::eLeft( *theSeed, &(*rechits), topology ));
      clone.addUserFloat("eRight", EcalClusterTools::eRight( *theSeed, &(*rechits), topology ));
      clone.addUserFloat("eTop", EcalClusterTools::eTop( *theSeed, &(*rechits), topology ));
      clone.addUserFloat("eBottom", EcalClusterTools::eBottom( *theSeed, &(*rechits), topology ));
      clone.addUserFloat("e4SwissCross", ( EcalClusterTools::eLeft( *theSeed, &(*rechits), topology ) +
                             EcalClusterTools::eRight( *theSeed, &(*rechits), topology ) +
                               EcalClusterTools::eTop( *theSeed, &(*rechits), topology ) +
                               EcalClusterTools::eBottom( *theSeed, &(*rechits), topology ) ));

      // local covariances: instead of using absolute eta/phi it counts crystals normalised
      std::vector<float> vLocCov = EcalClusterTools::localCovariances( *theSeed, &(*rechits), topology );

      float covIEtaIEta = vLocCov[0];
      float covIEtaIPhi = vLocCov[1];
      float covIPhiIPhi = vLocCov[2];

      clone.addUserFloat("covIEtaIEta", covIEtaIEta);
      clone.addUserFloat("covIEtaIPhi", covIEtaIPhi);
      clone.addUserFloat("covIPhiIPhi", covIPhiIPhi);

      // seed second moments wrt principal axes:
      Cluster2ndMoments moments = EcalClusterTools::cluster2ndMoments(*theSeed, *rechits );
      clone.addUserFloat("sMaj", moments.sMaj);
      clone.addUserFloat("sMin", moments.sMin);
      // angle between sMaj and phi direction:
      clone.addUserFloat("alpha", moments.alpha);

      std::pair<DetId, float> maxRH = EcalClusterTools::getMaximum( *theSeed, &(*rechits) );
      DetId seedCrystalId = maxRH.first;
      EcalRecHitCollection::const_iterator seedRH = rechits->find(seedCrystalId);

      clone.addUserFloat("time", (float)seedRH->time());
      clone.addUserFloat("chi2", (float)seedRH->chi2());
      clone.addUserFloat("recoFlag", (int)seedRH->recoFlag());
      clone.addUserFloat("seedEnergy", (float)maxRH.second);

      EcalClusterLocal local;  
      if(clone.superCluster()->seed()->hitsAndFractions().at(0).first.subdetId()==EcalBarrel) {
        float etacry, phicry, thetatilt, phitilt;
        int ieta, iphi;
        local.localCoordsEB(*clone.superCluster()->seed(),iSetup,etacry,phicry,ieta,iphi,thetatilt,phitilt);

        clone.addUserFloat("seedieta", ieta);
        clone.addUserFloat("seediphi", iphi);
        clone.addUserFloat("etacryseed", etacry);
        clone.addUserFloat("phicryseed", phicry);

      } else {
        float xcry, ycry, thetatilt, phitilt;
        int ix, iy;
        local.localCoordsEE(*clone.superCluster()->seed(),iSetup,xcry,ycry,ix,iy,thetatilt,phitilt);

        clone.addUserFloat("seedieta", ix);
        clone.addUserFloat("seediphi", iy);
        clone.addUserFloat("etacryseed", xcry);
        clone.addUserFloat("phicryseed", ycry);
      }

      // calculate H/E
      float hOverEConeSize = 0.15;
      float hOverEPtMin = 0.;
      EgammaTowerIsolation *towerIso1 = new EgammaTowerIsolation(hOverEConeSize,0.,hOverEPtMin,1,calotowersH.product()) ;
      EgammaTowerIsolation *towerIso2 = new EgammaTowerIsolation(hOverEConeSize,0.,hOverEPtMin,2,calotowersH.product()) ;

      float TowerHcalESum1 = towerIso1->getTowerESum(&(*clone.superCluster()));
      float TowerHcalESum2 = towerIso2->getTowerESum(&(*clone.superCluster()));
      float hcalESum = TowerHcalESum1 + TowerHcalESum2;

      clone.addUserFloat("hOverE", hcalESum/(clone.superCluster())->energy());
      delete towerIso1;
      delete towerIso2;


      if (clone.closestCtfTrackRef().isNull()) {
        clone.addUserInt("ctfHits", -1.0);
        clone.addUserFloat("ctfChi2", 0.0);
      }
      else {
        clone.addUserInt("ctfHits", clone.closestCtfTrackRef()->hitPattern().trackerLayersWithMeasurement());
        clone.addUserFloat("ctfChi2", clone.closestCtfTrackRef()->normalizedChi2());
      }

      if (!clone.pflowSuperCluster().isNull()) {
        clone.addUserInt("nPFClusters", clone.pflowSuperCluster()->clustersSize());
        clone.addUserFloat("eSeedPF", clone.pflowSuperCluster()->seed()->energy());
        clone.addUserFloat("eSCPF", clone.pflowSuperCluster()->energy());
        clone.addUserFloat("eESPF", clone.pflowSuperCluster()->preshowerEnergy());
      }
      else {
        clone.addUserInt("nPFClusters", -1.0);
        clone.addUserFloat("eSeedPF", -1.0);
        clone.addUserFloat("eSCPF", -1.0);
        clone.addUserFloat("eESPF", -1.0);
      }
      clone.addUserFloat("eES", clone.superCluster()->preshowerEnergy());

      pOut->push_back(clone);

    }
    iEvent.put(pOut);
}

// ------------ method called once each job just before starting event loop  ------------
void PatElectronBooster::beginJob() { }

// ------------ method called once each job just after ending the event loop  ------------
void PatElectronBooster::endJob() { }



void PatElectronBooster::setIPs(const pat::ElectronRef elecsRef,
				edm::Handle<reco::VertexCollection> vertices,
				reco::TransientTrack tt,
				edm::Event& iEvent,
				const edm::EventSetup& iSetup,
				pat::Electron& clone){

  using namespace edm;
  using namespace std;

  edm::Handle<reco::BeamSpot> bs;
  iEvent.getByLabel(edm::InputTag("offlineBeamSpot"),bs);


  // here I set the biased PV 
  reco::Vertex vertexYesB;
  if(vertices->empty()) 
    vertexYesB = reco::Vertex(reco::Vertex::Point(bs->position().x(),bs->position().y(),bs->position().z()),
			      reco::Vertex::Error());
  else
    vertexYesB = vertices->front(); //take the first in the list


  edm::Handle<reco::VertexCollection> unfilteredVertices;
  iEvent.getByLabel("offlinePrimaryVertices",unfilteredVertices);

  Handle<reco::BeamSpot>        pvbeamspot; 

  // -- add info wrt YesBias vertex
  Measurement1D ip = IPTools::absoluteTransverseImpactParameter(tt,vertexYesB).second;
  Measurement1D ip3D = IPTools::absoluteImpactParameter3D(tt,vertexYesB).second;
  clone.addUserFloat(std::string("tip"),ip.value());
  clone.addUserFloat(std::string("tipErr"),ip.error());
  clone.addUserFloat(std::string("ip"),ip3D.value());
  clone.addUserFloat(std::string("ipErr"),ip3D.error());


  /*
  // ------- add info wrt NoBias vertex
  reco::TrackCollection newTkCollection;
  bool foundMatch(false);
  for(reco::Vertex::trackRef_iterator itk = vertexYesB.tracks_begin(); itk!= vertexYesB.tracks_end(); itk++){
    bool refMatching;
    if(elecsRef->closestCtfTrack().ctfTrack.isNonnull())
      refMatching = (itk->get() == &*(elecsRef->closestCtfTrack().ctfTrack) );
    else
      refMatching = false;	
    float shFraction = elecsRef->closestCtfTrack().shFracInnerHits;
    if(refMatching && shFraction > 0.5){
      foundMatch = true;
    }else{
      newTkCollection.push_back(*itk->get());
    }
  }//track collection for vertexNoB is set
  
  //cout << "checking ele matching" << endl;
  //if(!foundMatch) {
  //cout << "WARNING: no ele matching found" << endl;
  //  vertexNoB = vertexYesB;
  //}else{      

  reco::Vertex vertexNoB;
  vector<TransientVertex> pvs = revertex.makeVertices(newTkCollection, *pvbeamspot, iSetup) ; //use BS constraint 
  if(pvs.empty()) 
    vertexNoB = reco::Vertex(reco::Vertex::Point(bs->position().x(),bs->position().y(),bs->position().z()),
			     reco::Vertex::Error());
  else   vertexNoB = pvs.front(); //take the first in the list

  
  reco::Vertex vertexNoBNoBS;
  vector<TransientVertex> pvs2 = revertexForceNoBS.makeVertices(newTkCollection, *pvbeamspot, iSetup) ; 
  if(pvs2.empty()) 
    vertexNoBNoBS = reco::Vertex(reco::Vertex::Point(bs->position().x(),bs->position().y(),bs->position().z()),
			     reco::Vertex::Error());
  else   vertexNoBNoBS = pvs2.front(); //take the first in the list


  

  Measurement1D ip_2 = IPTools::absoluteTransverseImpactParameter(tt,vertexNoB).second;
  Measurement1D ip3D_2 = IPTools::absoluteImpactParameter3D(tt,vertexNoB).second;
  clone.addUserFloat(std::string("tip2"),ip_2.value());
  clone.addUserFloat(std::string("tipErr2"),ip_2.error());
  clone.addUserFloat(std::string("ip2"),ip3D_2.value());
  clone.addUserFloat(std::string("ipErr2"),ip3D_2.error());

  Measurement1D ip_3 = IPTools::absoluteTransverseImpactParameter(tt,vertexNoBNoBS).second;
  Measurement1D ip3D_3 = IPTools::absoluteImpactParameter3D(tt,vertexNoBNoBS).second;
  clone.addUserFloat(std::string("tip3"),ip_3.value());
  clone.addUserFloat(std::string("tipErr3"),ip_3.error());
  clone.addUserFloat(std::string("ip3"),ip3D_3.value());
  clone.addUserFloat(std::string("ipErr3"),ip3D_3.error());
  */

  // ------- OLD style information (for backward compatibility)
  clone.addUserFloat( "dxyPV",clone.gsfTrack()->dxy(vertexYesB.position()) );
  clone.addUserFloat( "dzPV",clone.gsfTrack()->dz(vertexYesB.position()) );
  //clone.addUserFloat( "dxyPV2",clone.gsfTrack()->dxy(vertexNoB.position()) );
  //clone.addUserFloat( "dzPV2",clone.gsfTrack()->dz(vertexNoB.position()) );
  //clone.addUserFloat( "dxyPV3",clone.gsfTrack()->dxy(vertexNoBNoBS.position()) );
  //clone.addUserFloat( "dzPV3",clone.gsfTrack()->dz(vertexNoBNoBS.position()) );


}



template <class T> T PatElectronBooster::findClosestVertex(const double zPos, 
							   const std::vector<T>& vtxs){
    double dist(99999);
    T returnVertex;
    //unsigned int size = vtxs.size();
    typename std::vector<T>::const_iterator vtx;
    for(vtx = vtxs.begin(); vtx != vtxs.end(); vtx++){
        double tmpDist = fabs(zPos-vtx->position().z()); 
        if(tmpDist<dist){
            dist=tmpDist;
            returnVertex = *vtx;
        }
    }
    return returnVertex;
}


//define this as a plug-in
DEFINE_FWK_MODULE(PatElectronBooster);
