"""Independent receipt-only audit; never calls a simulation or model kernel."""
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.stats import beta

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'analysis/AB_confirmatory_execution_20261101/B_precision_coverage_v1/run'
OUT = Path(__file__).resolve().parent / 'precision_cases'

def digest(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()).hexdigest()

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def receipt(p):
    q=json.loads(p.read_text(encoding='utf-8'))
    assert digest(q['payload']) == q['payload_sha256'], str(p)
    return q['payload']

def event(q):
    return not q['undefined'] and bool(np.all(np.asarray(q['low']) <= 1) and np.all(np.asarray(q['high']) >= 1))

def main():
    OUT.mkdir(exist_ok=True)
    frozen=receipt(BASE/'frozen_spec.json')['result']
    spec=frozen['spec']
    assert spec == dict(alpha_bound=.003125,bridge_repetitions=1000,coverage_goal=.95,production_draws=20000,reduced_draws=1999,repetitions=2000,seed=2026110131)
    assert frozen['sources']['runtime']['utf8_mode'] == 1
    for name,h in frozen['sources']['files'].items():
        assert sha(Path(name)) == h, name
    for i,case in enumerate(frozen['cases']):
        folder=BASE/f'{i:02d}'; p=folder/'case.json'
        if not p.exists():
            print(f'{i:02d}: unsealed; skipped');continue
        case_sha=sha(p); previous=OUT/f'{i:02d}_{case_sha}.json'
        if previous.exists():
            prior=json.loads(previous.read_text(encoding='utf-8'))
            for name,h in prior['artifacts'].items():
                assert sha(folder/name)==h, str(folder/name)
            assert sha(BASE/'frozen_spec.json')==prior['frozen_spec_sha256']
            print(f'{i:02d}: prior audit reused after exact closure rehash');continue
        q=receipt(p);request=q['request'];r=q['result']
        assert request == dict(case=case,index=i,identity=frozen,spec=spec)
        assert r['case']==case and r['repetitions']==2000
        expected={f'{rep:04d}_{kind}.json' for rep in range(2000) for kind in ['data','statistics']}
        assert set(r['artifacts'])==expected
        assert {x.name for x in folder.glob('*.json')} == expected | {'case.json'}
        successes=discordances=undefined=0
        for rep in range(2000):
            seeds=np.random.SeedSequence([spec['seed'],i,rep]).generate_state(2,dtype=np.uint64)
            req=dict(case_identity=digest(request),replicate=rep,dataset_seed=int(seeds[0]),bootstrap_seed=int(seeds[1]))
            values={}
            for kind in ['data','statistics']:
                name=f'{rep:04d}_{kind}.json';file=folder/name
                assert sha(file)==r['artifacts'][name], str(file)
                item=receipt(file)
                counts=[1999,20000] if rep<1000 else [1999]
                assert item['request']==(req if kind=='data' else dict(**req,draw_counts=counts))
                values[kind]=item['result']
            data=np.asarray(values['data'])
            assert data.shape==(case['n'],2,2,2) and np.isfinite(data).all() and (data>0).all()
            statistics=values['statistics']; assert set(statistics)==set(map(str,counts))
            for statistic in statistics.values():
                assert isinstance(statistic['undefined'],bool)
                if not statistic['undefined']:
                    for field in ['low','high','estimates','halfwidth']:
                        array=np.asarray(statistic[field]);assert array.shape==(2,3,2) and np.isfinite(array).all()
                    assert (np.asarray(statistic['low'])<=np.asarray(statistic['high'])).all()
            small=statistics['1999']; successes+=event(small);undefined+=small['undefined']
            if rep<1000:discordances+=event(small) and not event(statistics['20000'])
        lower=0. if successes==0 else float(beta.ppf(.003125,successes,2001-successes))
        upper=1. if discordances==1000 else float(beta.ppf(1-.003125,discordances+1,1000-discordances))
        bounds=dict(reduced_lower=lower,overstatement_upper=upper,production_lower=max(0.,lower-upper))
        assert (successes,discordances,undefined)==(r['coverage_successes'],r['production_only_failures'],r['undefined'])
        assert bounds==r['bounds'] and r['passed']==(bounds['production_lower']>=.95)
        assert r['truth']==np.ones((2,3,2)).tolist()
        audit=dict(reviewer='/root/sol_parallel_acceptance',case=case,case_sha256=case_sha,
                   artifacts=r['artifacts'],counts=dict(successes=successes,discordances=discordances,undefined=undefined),
                   bounds=bounds,passed=r['passed'],frozen_spec_sha256=sha(BASE/'frozen_spec.json'),
                   scope='Every subordinate hash/payload/seed/request/shape checked; saved decisions and beta bounds independently recounted. No bootstrap or dataset regenerated. Incremental audit, not final stage approval.')
        previous.write_text(json.dumps(audit,sort_keys=True,indent=2)+'\n',encoding='utf-8')
        print(f'{i:02d}: audited 4000 records, passed={r["passed"]}, lower={bounds["production_lower"]:.8f}')

if __name__=='__main__':main()
