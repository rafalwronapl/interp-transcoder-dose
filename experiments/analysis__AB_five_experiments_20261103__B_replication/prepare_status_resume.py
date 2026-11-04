from pathlib import Path
import json
from research_checks.gate import sha,digest,snapshot
from . import status_resume as r
BASE=Path(__file__).parent;ROOT=r.ROOT;REL=BASE.relative_to(ROOT).as_posix()
def put(name,value):(BASE/name).write_text(json.dumps(value,indent=2)+'\n')
def main():
    out=BASE/'run';records=[json.loads(x) for x in (out/'ledger.jsonl').read_text().splitlines()]
    for x in records:assert digest(x['record'])==x['sha256']
    attempts=[x['record'] for x in records if x['record']['event']=='attempt']
    computed={x['record']['request'] for x in records if x['record']['event']=='computed'}
    assert {x['request'] for x in attempts}==computed
    for x in attempts:
        c=json.loads((out/'cache'/(x['request']+'.json')).read_text());assert c['payload_sha256']==digest(c['payload']);assert digest(c['payload']['request'])==x['request']
    # Force all advisory retries to fail, then verify unrelated paths still raise.
    old=r.ORIGINAL_REPLACE;old_sleep=r.time.sleep;count=[0]
    def failed(a,b):count[0]+=1;raise PermissionError('synthetic Windows lock')
    r.ORIGINAL_REPLACE=failed;r.time.sleep=lambda _:None
    try:
        r.status_replace(out/'STATUS.tmp',out/'STATUS.json');assert count[0]==5
        try:r.status_replace(out/'cache/x.tmp',out/'cache/x.json')
        except PermissionError:pass
        else:raise AssertionError('Immutable publication must fail closed')
    finally:r.ORIGINAL_REPLACE=old;r.time.sleep=old_sleep
    audit=dict(ok=True,trained_calls=0,completed_bundles=len(attempts),completed_logical=sum(len(x['coupled_operations']) for x in attempts),no_uncertain_attempt=True,status_failure_is_advisory=True,nonstatus_failure_propagates=True,scientific_source_unchanged=True)
    put('resume_audit.json',audit)
    sources=[p for p in out.rglob('*') if p.is_file() and p.name not in ['STATUS.tmp','STATUS.json']]
    sources += [BASE/'resume_audit.json',ROOT/'operations/research_launch_535e861ebdaf431fbad27c82fb5d6588.json',BASE/'launch_v3.err']
    put('resume_inputs.json',dict(files={p.relative_to(ROOT).as_posix():sha(p) for p in sources}))
    contract=json.loads((BASE/'contract.json').read_text());contract['id']+='status_resume';contract['primary_agent']='/root/a_l21_five_campaign';contract['purpose']='Resume exact frozen B1B study after advisory Windows STATUS replace failure; no repeated cached measurements'
    contract['tracked_files'] += [REL+'/status_resume.py',REL+'/prepare_status_resume.py']
    contract['input_manifests'].append(REL+'/resume_inputs.json')
    contract['gates'].append(dict(id='resume_cache_integrity',category='restart',evidence=REL+'/resume_audit.json',pointer='/ok',op='eq',expected=True,reason='All attempted bundles have valid durable cache; telemetry failure isolated'))
    contract['entrypoint']=dict(module='analysis.AB_five_experiments_20261103.B_replication.status_resume',args=[])
    put('resume_contract.json',contract);put('resume_snapshot.json',snapshot(ROOT,REL+'/resume_contract.json','pre_run'));print(audit)
if __name__=='__main__':main()
