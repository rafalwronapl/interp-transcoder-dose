"""Bind the completed failed qualification; reuse sealed per-case raw digests."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'analysis/AB_confirmatory_execution_20261101'
STAGE=BASE/'B_precision_coverage_v1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(p,obj):
    with p.open('x',encoding='utf-8') as f:json.dump(obj,f,indent=2)
def main():
    final=ROOT/'operations/research_launch_cc5d758907a9430298ff246d4243134e.json'
    runtime=read(final);pre=read(STAGE/'pre_run_snapshot.json')
    if runtime['returncode']!=0 or runtime['snapshot_sha256']!=pre['snapshot_sha256']:
        raise ValueError('Original calibration runtime mismatch')
    result=read(STAGE/'run/summary.json')['payload']['result']
    if len(result['cases'])!=8:raise ValueError('Fixed series incomplete')
    files=dict(pre['payload']['files']);rows=[]
    for i,case in enumerate(result['cases']):
        folder=STAGE/'run'/f'{i:02d}';sealed=read(folder/'case.json')['payload']['result']
        if sealed!=case or sealed['repetitions']!=2000:raise ValueError('Case/summary mismatch')
        for name,h in sealed['artifacts'].items():files[(folder/name).relative_to(ROOT).as_posix()]=h
        rows.append(dict(case=sealed['case'],passed=sealed['passed'],coverage_successes=sealed['coverage_successes'],
            production_lower=sealed['bounds']['production_lower'],reduced_lower=sealed['bounds']['reduced_lower'],
            overstatement_upper=sealed['bounds']['overstatement_upper'],undefined=sealed['undefined']))
    summary=dict(cases=8,synthetic_datasets=16000,reduced_draws=1999,paired_production_datasets=8000,
        production_draws=20000,passed=sum(r['passed'] for r in rows),failed=sum(not r['passed'] for r in rows),
        N128_precision_eligible=False,N256_precision_eligible=False,model_calls=0,runtime_returncode=0,
        completed_utc=runtime['completed_utc'],case_rows=rows,independent_completion_review='pending')
    write(STAGE/'completion_summary_v1.json',summary)
    text='''# Original B joint-precision qualification: completed negative outcome

All eight fixed cases completed once,2000datasets per case. Two passed and six failed;
each N128/256 passed only the mild lognormal035 case and failed pareto3/lognormal1/
heterogeneous. Both Ns therefore fail this method-specific qualification. It is not
a scientific B1–B3 null or evidence that all true coverage must be below95%; the frozen
joint-coverage lower-bound gate was not met. This method does not admit B PILOT/TEST.

Exactly16000synthetic datasets were generated. Each used1999reduced bootstrap draws;
the first1000per case reused the same data for20000production draws. No model call,
optional stopping, extension, changed threshold or repeated failed case occurred.
The actual canonical legacy runtime reports returncode0 at12:28:45.876555UTC.

Manifest construction reused sealed per-case artifact hashes rather than recomputing
raw data/statistics. Independent case-audit caches00–04 remain reusable; final review
must additionally cover remaining cases and the full decision. Old source/spec/data
remain unchanged. Prospective precision-v6 is a separate reviewed method/calibration,
not a relabeling of this failure and not unseen-law or distribution-free validation.
No second-order Pareto3 accuracy is claimed.
'''
    (STAGE/'REPORT_COMPLETION_v1.md').write_text(text,encoding='utf-8')
    files[final.relative_to(ROOT).as_posix()]=sha(final)
    for p in STAGE.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc':
            name=p.relative_to(ROOT).as_posix()
            if name not in files:files[name]=sha(p)
    write(STAGE/'completion_outputs_manifest_v1.json',dict(files=files))
    contract=read(STAGE/'contract.json');contract['id']='AB_B_ORIGINAL_PRECISION_COMPLETION_20261101_v1'
    contract['purpose']='Completion audit of eight fixed original B precision cases;2pass6fail;no scientific null,0models.'
    contract['input_manifests'].append((STAGE/'completion_outputs_manifest_v1.json').relative_to(ROOT).as_posix())
    contract['tracked_files'].extend((STAGE/n).relative_to(ROOT).as_posix() for n in ['completion_summary_v1.json','REPORT_COMPLETION_v1.md'])
    write(STAGE/'completion_contract_v1.json',contract)
    print(json.dumps({k:v for k,v in summary.items() if k!='case_rows'}))
if __name__=='__main__':main()
