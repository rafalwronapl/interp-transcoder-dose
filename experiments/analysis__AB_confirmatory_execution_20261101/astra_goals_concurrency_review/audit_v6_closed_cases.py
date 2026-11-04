"""Incremental read-only receipt audit. Never regenerates datasets/bootstrap draws."""
import json,hashlib,sys
from pathlib import Path
import numpy as np
from scipy.stats import beta
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from research_checks.gate import digest
RUN=ROOT/'analysis/AB_confirmatory_execution_20261101/B_precision_v6_calibration_v1/run'
OUT=Path(__file__).parent/'v6_closed_cases'
OUT.mkdir(exist_ok=True)
def read(p,expected=None):
    raw=p.read_bytes();h=hashlib.sha256(raw).hexdigest()
    if expected is not None:assert h==expected,p
    obj=json.loads(raw);assert digest(obj['payload'])==obj['payload_sha256'],p
    return obj['payload'],h
frozen,fh=read(RUN/'frozen_spec.json');f=frozen['result'];assert f==frozen['request']
assert f['spec']==dict(version=6,seed=2026110161,repetitions=2000,draws=1999,alpha_bound=.05/8,coverage_goal=.95,construction_confidence=.99)
method=f['identity']['method']
for index,case in enumerate(f['cases']):
    folder=RUN/f'{index:02d}';path=folder/'case.json';out=OUT/f'case_{index:02d}.json'
    if not path.exists():continue
    if out.exists():
        saved=json.loads(out.read_text());assert hashlib.sha256(path.read_bytes()).hexdigest()==saved['case_sha256'];continue
    payload,ch=read(path);request=dict(identity=f,case=case,index=index,spec=f['spec']);assert payload['request']==request
    result=payload['result'];artifacts=result['artifacts']
    assert set(artifacts)=={f'{r:04d}_{kind}.json' for r in range(2000) for kind in ['data','statistics']}
    covered=undefined=0
    for r in range(2000):
        seeds=np.random.SeedSequence([2026110161,index,r]).generate_state(2,dtype=np.uint64)
        req=dict(case_identity=digest(request),replicate=r,dataset_seed=int(seeds[0]),bootstrap_seed=int(seeds[1]))
        data,_=read(folder/f'{r:04d}_data.json',artifacts[f'{r:04d}_data.json']);assert data['request']==req
        x=np.asarray(data['result']);assert x.shape==(case['n'],2,2,2) and np.isfinite(x).all() and (x>=0).all()
        stat,_=read(folder/f'{r:04d}_statistics.json',artifacts[f'{r:04d}_statistics.json']);assert stat['request']==dict(**req,draws=1999,method=method)
        q=stat['result'];undefined+=q['undefined']
        if q['undefined']:assert q['coverage'] is False and q['reason'];continue
        v=q['intervals'];assert v['draws']==1999 and v['seed']==int(seeds[1]) and v['critical_order_rank']==1980
        low,high,est,width=[np.asarray(v[k]) for k in ['low','high','estimates','halfwidth']]
        assert all(z.shape==(2,3,2) and np.isfinite(z).all() for z in [low,high,est,width])
        assert (low>0).all() and (low<=est).all() and (est<=high).all()
        np.testing.assert_allclose(width,(high-low)/2,rtol=0,atol=0)
        mixture=np.concatenate([x,x.mean(axis=2,keepdims=True)],axis=2);means=mixture.mean(axis=0)
        theta=np.stack([.5*np.log(means[...,0]),.5*(np.log(means[...,0])-np.log(means[...,1]))],axis=-1)
        np.testing.assert_allclose(est,np.exp(theta),rtol=1e-13)
        coverage=bool((low<=1).all() and (high>=1).all());assert q['coverage'] is coverage
        assert v['simultaneous_target_met'] is bool((width<=np.array([.10,.02])).all())
        covered+=coverage
    lower=float(beta.ppf(.05/8,covered,2000-covered+1)) if covered else 0.
    assert result['coverage_successes']==covered and result['undefined']==undefined and result['coverage_lower']==lower
    assert result['passed'] is (lower>=.95) and result['method']==method and result['repetitions']==2000
    report=dict(case=case,index=index,case_sha256=ch,frozen_spec_sha256=fh,artifacts_checked=4000,datasets_checked=2000,coverage_successes=covered,undefined=undefined,coverage_lower=lower,passed=result['passed'],reviewer='/root/astra_goals_and_concurrency_review',scope='All sealed file/payload hashes, request and seed identities, data shape/finiteness, stored interval/estimate/width/coverage arithmetic and independent beta CP checked. No bootstrap or dataset regeneration. Preliminary case audit, not final completion acceptance.')
    out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
