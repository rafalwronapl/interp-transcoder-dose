"""Close observed selector decision; never extend or repeat the MC campaign."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'analysis/AB_confirmatory_execution_20261101'
STAGE=BASE/'A_selector_ready_v1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(p,obj):
    with p.open('x',encoding='utf-8') as f:json.dump(obj,f,indent=2)
def main():
    selected=read(STAGE/'run/selection.json')['payload']['result']
    final=ROOT/'operations/concurrency_runtime_v1/launch_470c95e39f6a4b1f8a2189c50429dcb8.json'
    runtime=read(final)
    if runtime['returncode']!=0 or runtime['snapshot_sha256']!=read(STAGE/'pre_run_snapshot_v1.json')['snapshot_sha256']:
        raise ValueError('Selector runtime receipt mismatch')
    rows=[]
    for case in selected['cases']:
        result=case['result']
        rows.append(dict(case=case['case'],status=result['status'],passed=result['passed'],
            completed=result.get('completed',0),remaining=result.get('remaining'),successes=result.get('successes'),
            optimistic_final_bound=result.get('optimistic_final_bound'),proof=result.get('proof')))
    summary=dict(selected=selected['selected'],case_slots=len(rows),cases=rows,
        synthetic_replicates=sum(r['completed'] for r in rows),model_calls=0,TEST_started=False,
        runtime_returncode=0,runtime_started=runtime['started_utc'],runtime_completed=runtime['completed_utc'],
        independent_completion_review='pending',interpretation='Frozen power/cap decision; no scientific null or effect confirmation.')
    write(STAGE/'completion_summary_v1.json',summary)
    report='''# A prospective selector completion: infeasible under frozen cap

The fixed A-only selector returned INFEASIBLE_UNDER_FROZEN_CAP. Both128cases remain
ineligible from independently accepted family calibration. At256, both prescribed
dispersion scenarios1.0/1.5 failed the frozen joint-power rule. After368/352simulations,
respectively, the predeclared deterministic impossible-pass bound triggered: even
all remaining successes with no new overstatement yield final lower bound.79960905,
below the required.8. Exactly720new synthetic datasets were evaluated; there was no
optional extension or rerun, and no model call. The remaining simulations are not
missing-at-random data; this is the frozen exact rejection rule, not a final numerical
estimate of population power from a completed2000simulation sample.

No TESTN was selected, TEST was not collected, and hypotheses remain untested.
This is a planning-power/cap outcome conditional on accepted PILOT dispersion and
fixed scientific targets. It does not establish a scientific null or refute historical
results. Targets, hypotheses, frames, fits, calibration and the cap were unchanged.
No larger convenient N is admitted. Dependent TEST/shared-TEST stages remain gated.

The actual final canonical runtime receipt reports returncode0. All accepted inputs,
selector seeds/indices/alpha, immutable dataset/statistics records and final decision
are bound. Independent completion review is pending. A ended12:45:48UTC before the
new B launcher began12:46:35; two-CPU capacity was enabled but these two computations
did not overlap. B and grandfather family calibration now continue separately.
'''
    (STAGE/'REPORT_COMPLETION_v1.md').write_text(report,encoding='utf-8')
    files=dict(read(STAGE/'pre_run_snapshot_v1.json')['payload']['files'])
    files[final.relative_to(ROOT).as_posix()]=sha(final)
    for p in STAGE.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc':files[p.relative_to(ROOT).as_posix()]=sha(p)
    write(STAGE/'completion_outputs_manifest_v1.json',dict(files=files))
    contract=read(STAGE/'contract.json');contract['id']='AB_A_SELECTOR_COMPLETION_20261101_v1'
    contract['purpose']='Completion audit of frozen A selector infeasibility;720synthetic repetitions,0models,noTEST.'
    contract['input_manifests'].append((STAGE/'completion_outputs_manifest_v1.json').relative_to(ROOT).as_posix())
    contract['tracked_files'].extend((STAGE/n).relative_to(ROOT).as_posix() for n in ['completion_summary_v1.json','REPORT_COMPLETION_v1.md'])
    write(STAGE/'completion_contract_v1.json',contract)
    print(json.dumps(summary))
if __name__=='__main__':main()
