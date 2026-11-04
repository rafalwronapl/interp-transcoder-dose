"""Close actual v6 qualification using sealed raw digests; no recalibration."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'analysis/AB_confirmatory_execution_20261101'
STAGE=BASE/'B_precision_v6_calibration_v1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(p,obj):
    with p.open('x',encoding='utf-8') as f:json.dump(obj,f,indent=2)
def main():
    runtime_path=ROOT/'operations/concurrency_runtime_v1/launch_e6e89d1b525b48e7ae77956740c3ea4a.json'
    runtime=read(runtime_path);pre=read(STAGE/'pre_run_snapshot_v3.json')
    if runtime['returncode']!=0 or runtime['snapshot_sha256']!=pre['snapshot_sha256']:
        raise ValueError('Qualification runtime mismatch')
    result=read(STAGE/'run/summary.json')['payload']['result']
    if len(result['cases'])!=8:raise ValueError('Qualification incomplete')
    files=dict(pre['payload']['files']);rows=[]
    for i,case in enumerate(result['cases']):
        folder=STAGE/'run'/f'{i:02d}';sealed=read(folder/'case.json')['payload']['result']
        if sealed!=case:raise ValueError('Sealed case/aggregate mismatch')
        for name,h in sealed['artifacts'].items():files[(folder/name).relative_to(ROOT).as_posix()]=h
        rows.append(dict(case=sealed['case'],passed=sealed['passed'],coverage_lower=sealed['coverage_lower'],
            coverage_successes=sealed.get('coverage_successes'),undefined=sealed.get('undefined')))
    summary=dict(cases=8,passed=sum(x['passed'] for x in rows),synthetic_datasets=16000,production_draws=1999,
        bridge_draws=0,model_calls=0,precision_eligible_by_n=result['eligible_by_n'],
        primary_family_eligibility='Separate: B128 failed primary family; B256 full family pending at closure preparation.',
        case_rows=rows,actual_runtime_returncode=0,runtime_completed=runtime['completed_utc'],
        independent_completion_review='pending',scope=result.get('scope'))
    write(STAGE/'completion_summary_v1.json',summary)
    text='''# B precision v6 qualification completion

All8fixed cases completed once,2000datasets/case and1999production draws. All8 passed
the fixed joint12coverage lower-bound requirement>=.95. The same4laws x2Ns used fresh
frozen seeds; this is finite-scenario qualification, not unseen-law/distribution-free
validation or a second-order Pareto3 guarantee. No20kbridge, optional extension, retry,
threshold change or model call occurred. Undefined intervals count failure.

Both Ns pass this method-specific precision qualification. This alone does not admit
B native acquisition: B128 failed the separate original primary-family requirement,
and B256 still needs its complete family evidence. Scientific B1–B3 are untested.
The original method's2pass/6fail negative qualification remains independently accepted
and unchanged. Its datasets/results were not relabeled or repeated as v6 successes.

The actual reviewed runtime completed with returncode0 at13:59:54.815721UTC. Sealed
case artifact hashes are reused in this manifest; no raw statistics/bootstrap/model
were regenerated for closure. Independent incremental case audits are reused by the
final reviewer. Acceptance is pending exact completion-snapshot review.
'''
    (STAGE/'REPORT_COMPLETION_v1.md').write_text(text,encoding='utf-8')
    files[runtime_path.relative_to(ROOT).as_posix()]=sha(runtime_path)
    for p in STAGE.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc':
            name=p.relative_to(ROOT).as_posix()
            if name not in files:files[name]=sha(p)
    write(STAGE/'completion_outputs_manifest_v1.json',dict(files=files))
    contract=read(STAGE/'contract_v3.json');contract['id']='AB_B_V6_PRECISION_COMPLETION_20261101_v1'
    contract['purpose']='Completion audit of8/8passed v6 precision cases;16000datasets,1999draws,0models; separate family eligibility still required.'
    contract['input_manifests'].append((STAGE/'completion_outputs_manifest_v1.json').relative_to(ROOT).as_posix())
    contract['tracked_files'].extend((STAGE/n).relative_to(ROOT).as_posix() for n in ['completion_summary_v1.json','REPORT_COMPLETION_v1.md'])
    write(STAGE/'completion_contract_v1.json',contract)
    print(json.dumps({k:v for k,v in summary.items() if k!='case_rows'}))
if __name__=='__main__':main()
