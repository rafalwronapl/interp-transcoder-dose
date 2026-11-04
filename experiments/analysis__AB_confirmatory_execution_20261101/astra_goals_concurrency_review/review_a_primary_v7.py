"""Independent result-to-estimand audit; no bootstrap/model rerun."""
import json,hashlib,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from research_checks.gate import digest
from ab_confirmatory_20261101.analysis_ab_v4 import a_records
from ab_confirmatory_20261101.statistics import family
STAGE=ROOT/'analysis/A_estimation_v7/TEST_v1';ANALYSIS=ROOT/'analysis/A_estimation_v7/preliminary_primary_v1';OUT=Path(__file__).parent/'a_primary_v7';OUT.mkdir(exist_ok=True)
def read(p):
 raw=p.read_bytes();q=json.loads(raw);assert digest(q['payload'])==q['payload_sha256'];return q['payload'],hashlib.sha256(raw).hexdigest()
manifest,mh=read(ANALYSIS/'source_manifest.json');result,rh=read(ANALYSIS/'result.json');closure,ch=read(STAGE/'run/stage_completed.json')
cfg=json.loads((STAGE/'config.json').read_text());docs=json.loads((ROOT/cfg['corpus']).read_text())['documents'];assert len(docs)==5120 and cfg['phase']=='TEST'
blocks=sorted({d['block'] for d in docs});assert len(blocks)==256;frames=['T0','T2','T5','T6','T7'];arms=['P','U0','Uctrl','U2','U5']
L=np.full((256,5,4,5),np.nan);V=np.full_like(L,np.nan);seen=set();records={}
for doc in docs:
 p=STAGE/'run/results/r0'/(doc['id']+'.json');q,h=read(p);relative=p.relative_to(ROOT).as_posix();assert manifest['files'][relative]==h==closure['files'][p.relative_to(STAGE/'run').as_posix()]
 assert q['document']==doc and q['cohort']=='r0';coordinate=(blocks.index(doc['block']),frames.index(doc['frame']),2*doc['side']+doc['q']);assert coordinate not in seen;seen.add(coordinate);records[doc['id']]=q
 for j,arm in enumerate(arms):
  a=q['values'][arm];assert np.isfinite([a['L'],a['V'],a['prediction'],q['native_h']]).all() and a['L']>=0 and a['V']>=0
  np.testing.assert_allclose(a['L'],(a['prediction']-q['native_h'])**2,rtol=1e-12,atol=1e-12)
  L[coordinate+(j,)]=a['L'];V[coordinate+(j,)]=a['V']
assert len(seen)==5120 and np.isfinite(L).all() and np.isfinite(V).all()
lm=L.mean(2);vm=V.mean(2)
x=np.column_stack([((lm[:,3,2]-lm[:,3,3])+(lm[:,4,2]-lm[:,4,3]))/2,vm[:,2,3]-vm[:,2,4],lm[:,2,4]-lm[:,2,3],lm[:,2,1]-lm[:,2,0]])
adapter,meta=a_records(docs,records);assert not meta['missing'];np.testing.assert_array_equal(x,adapter)
np.testing.assert_allclose(result['component_means'],x.mean(0),rtol=1e-14,atol=1e-12)
components=[]
for j,c in enumerate(result['components']):
 assert c['n']==256 and c['draws']==1999 and c['seed']==20261101 and c['status']=='defined'
 np.testing.assert_allclose(c['estimate'],x[:,j].mean(),rtol=1e-14,atol=1e-12);np.testing.assert_allclose(c['se'],x[:,j].std(ddof=1)/16,rtol=1e-14,atol=1e-12)
 assert c['p_for_holm']==min(1,2*c['p_raw']);assert np.isclose(c['p_raw']*2000,round(c['p_raw']*2000))
 assert c['ci'][0]<c['ci'][1] and np.isfinite(c['ci']).all()
 components.append({k:v for k,v in c.items() if k!='component'})
assert family([[components[0]],[components[1],components[2]],[components[3]]])==result['family']
for name,h in manifest['files'].items():
 if '/results/r0/' not in name:assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h
np.savez(OUT/'verified_components.npz',components=x,block_ids=np.asarray(blocks),readout_errors=L,vector_errors=V)
proof=dict(status='FOCUSED_PRIMARY_RESULT_REVIEW_PASSED_FULL_NATIVE_CACHE_ACCEPTANCE_PENDING',result_sha256=rh,source_manifest_sha256=mh,closure_sha256=ch,documents=5120,blocks=256,components=x.mean(0).tolist(),family_status=[q['status'] for q in result['family']],holm_p=[q['p_holm'] for q in result['family']],all_three_supported=False,ci_construction='Stored frozen1999-draw bootstrap-t, nominal99percent pointwise; not rerun by reviewer.',scope='All result hashes/payloads/document coordinates/L arithmetic verified. Independent manual tensor/weights/contrasts agree exactly with frozen adapter; means/SE/safe2/IUT/Holm checked. Recorded p/CI kernel call source and fixedseed/draw metadata reviewed, no independent bootstrap regeneration. Full underlying capture/vector-target/cache audit pending; one frozen r0 conditional inference, no80percentpower/.04assurance claim.',interpretation=dict(A1='Positive Uctrl-minus-U2 readout-loss contrast on equal T6/T7 mixture; no each-frame superiority claim.',A2='Vector U2-minus-U5 positive, but readout U5-minus-U2 negative; required ranking reversal NOT supported. Opposite readout sign is not a newly predeclared alternative hypothesis.',A3='Positive U0-minus-P readout-loss contrast onT5; new-fit oracle correction harms this readout.',joint='Original three-hypothesis joint success not obtained.'),reviewer='/root/astra_goals_and_concurrency_review')
(OUT/'focused_review.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
