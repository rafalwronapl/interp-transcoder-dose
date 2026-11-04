"""Independent negative-stage audit; saved arithmetic only, no MC regeneration."""
import hashlib,json,sys
from pathlib import Path
import numpy as np
from scipy.stats import beta
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from research_checks.gate import digest
BASE=ROOT/'analysis/AB_confirmatory_execution_20261101/A_stability_calibration_v1'
OUT=Path(__file__).resolve().parent/'A_stability_completion_v1'
SNAP='9421b4ba6f10e6c672068ba74c0b1b28171a5f62f0d38dd762ed2790089c4e75'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def receipt(p):
    obj=json.loads(p.read_text());assert digest(obj['payload'])==obj['payload_sha256'];return obj['payload']
def main():
    snap=json.loads((BASE/'completion_snapshot_v1.json').read_text());assert snap['snapshot_sha256']==SNAP==digest(snap['payload'])
    members=snap['payload']['files']
    def bound(p):assert members[p.relative_to(ROOT).as_posix()]==sha(p)
    run=BASE/'run';frozen=receipt(run/'frozen_spec.json');bound(run/'frozen_spec.json')
    identity=frozen['result'];spec=identity['spec'];cases=identity['cases']
    assert spec==dict(version=4,seed=2026110107,fits=16,repetitions=2000,production_draws=1999,alpha_bound=.05/18,coverage_goal=.95,physical_sd_over_goal=[.5,1.,2.],scope='pointwise population MEAN; no simultaneous four-component coverage')
    expected=[dict(n=n,fit_fraction=f,distribution=d) for n in [128,256] for f in [.1,.5,.9] for d in ['normal','t3','lognormal']];assert cases==expected
    summary=receipt(run/'summary.json');bound(run/'summary.json');assert summary['request']==identity
    rows=[];results=[]
    for i,case in enumerate(cases):
        path=run/f'{i:02d}/case.json';obj=receipt(path);bound(path);q=obj['result'];results.append(q)
        assert obj['request']==dict(identity=identity,case=case,index=i,spec=spec)
        assert q['case']==case and q['repetitions']==2000
        lower=float(beta.ppf(.05/18,q['successes'],2000-q['successes']+1)) if q['successes'] else 0.
        assert q['coverage_lower']==lower and q['passed']==(lower>=.95)
        assert len(q['artifacts'])==4000
        for name,h in q['artifacts'].items():assert members[(path.parent/name).relative_to(ROOT).as_posix()]==h
        rows.append(dict(index=i,case=case,successes=q['successes'],coverage_lower=lower,passed=q['passed']))
    assert summary['result']['cases']==results and summary['result']['all_passed'] is False
    assert sum(q['passed'] for q in rows)==14
    assert [q['index'] for q in rows if not q['passed']]==[5,8,14,17]
    decisive=results[17];folder=run/'17';request=receipt(folder/'case.json')['request'];widths=[];successes=0
    for rep in range(2000):
        dp=folder/f'{rep:04d}_data.json';sp=folder/f'{rep:04d}_statistics.json'
        data=receipt(dp);stat=receipt(sp);bound(dp);bound(sp)
        seeds=np.random.SeedSequence([spec['seed'],17,rep]).generate_state(2,dtype=np.uint64)
        req=dict(case_identity=digest(request),replicate=rep,dataset_seed=int(seeds[0]),bootstrap_seed=int(seeds[1]))
        assert data['request']==req and stat['request']==dict(**req,draws=1999)
        x=np.asarray(data['result']);assert x.shape==(16,256) and np.isfinite(x).all()
        z=stat['result'];assert np.isfinite([z['low'],z['high'],z['halfwidth']]).all() and z['low']<=z['high']
        assert z['covered']==(z['low']<=0<=z['high']) and z['halfwidth']==(z['high']-z['low'])/2
        successes+=z['covered'];widths.append(z['halfwidth'])
    assert successes==1806==decisive['successes']
    assert np.array_equal(np.quantile(widths,[0,.05,.5,.95,1]),decisive['standardized_halfwidth_quantiles'])
    assert decisive['physical_sensitivity']=={str(sd):float(np.mean(np.asarray(widths)*sd<=1)) for sd in [.5,1.,2.]}
    runtime=ROOT/'operations/concurrency_runtime_v1/launch_dd98d4ed2b4c486eb7eb6a8b54712d22.json';bound(runtime);live=json.loads(runtime.read_text());assert live['returncode']==0
    out=dict(snapshot_sha256=SNAP,case_rows=rows,all_cases_gate_passed=False,full_saved_arithmetic_cases=[17],full_saved_data_records=2000,full_saved_statistic_records=2000,other_cases_scope='Case metadata, aggregate agreement, artifact membership and CP arithmetic only; canonical verification covers all member hashes. No other raw statistic re-derivation.',runtime_returncode=0,scope='Negative multiple-FIT calibration only; additional15FIT stage not admitted. Single frozen-r0 A primary study has separate eligibility and remains unaffected.',no_model_or_bootstrap_or_data_generation=True)
    OUT.mkdir(exist_ok=True);(OUT/'audit.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    review=dict(schema_version=1,snapshot_sha256=SNAP,reviewer_id='/root/sol_parallel_acceptance',independent=True,verdict='approved',topics_checked=['design','implementation','data','cost','claims'],findings=[],limitations=['Acceptance of completed NEGATIVE calibration, not authorization for15 additionalFITs or universal interval coverage.14/18fixed scenarios passed;4lognormal cases failed.', 'All18case/spec/aggregate hashes, artifact memberships and CP bounds checked; full saved data/statistic arithmetic audited for decisive case17 only (N256/lognormal/fit_fraction.9,1806/2000,lower.8832824513676938). No claim all72kraw calculations re-derived.', 'No model, refit, SVD, dataset regeneration or bootstrap/MC replay. Native and scientific one-r0A outcomes not re-audited; independent original numerical sources inspected. Canonical full snapshot verification is recorded separately.'])
    review['limitations']=' '.join(review['limitations'])
    (BASE/'completion_review_sol_v1.json').write_text(json.dumps(review,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(cases=18,passed=14,failed=[5,8,14,17],decisive_successes=successes,decisive_lower=decisive['coverage_lower'],review=str(BASE/'completion_review_sol_v1.json'))))
if __name__=='__main__':main()
