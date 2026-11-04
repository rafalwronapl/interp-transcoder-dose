"""Assemble completion evidence from closed saved records; no model or refitting."""
from pathlib import Path
import json, hashlib

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'analysis/AB_confirmatory_execution_20261101'
STAGE=BASE/'B_tail_qualification_v1'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,x):
    if p.exists(): raise ValueError('Never overwrite completion evidence: '+str(p))
    p.write_text(json.dumps(x,indent=2),encoding='utf-8')
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    done=read(STAGE/'run/stage_completed.json')['payload']
    status=read(STAGE/'run/STATUS.json')
    if status['stage']!='completed' or done['attempted_operations']!=160: raise ValueError('Stage not closed')
    qualification=read(STAGE/'run/qualification.json')['payload']
    results=[read(p)['payload'] for p in sorted((STAGE/'run/results').rglob('*.json'))]
    if len(results)!=16:raise ValueError('Incomplete endpoint cells')
    summary=dict(documents=4,endpoint_cells=16,full_transformer=56,native_tail=52,local_native=16,
        local_TC=20,local_JVP=8,forward=152,backward=8,total_logical=160,
        elapsed_worker_seconds=status['elapsed_seconds'],qualification_passed=qualification['passed'],
        max_tail_margin_parity=max(r['tail_parity_max'] for r in results),
        max_natural_margin_parity=max(r['base_parity'] for r in qualification['records']),
        max_gradient_absolute=max(r['gradient_absolute'] for r in qualification['records']),
        max_gradient_relative=max(r['gradient_relative'] for r in qualification['records']),
        max_branch_relative=max(r['anchors']['branch_relative'] for r in results),
        new_unused_FIT_transfer_only=True,scientific_hypothesis_result=False)
    write(STAGE/'completion_summary_v1.json',summary)
    report='''# B native-tail technical completion

Completed four previously unused FIT-transfer recipients, full/projected operators
at doses .05 and2. All16 endpoint comparisons and all four natural/gradient controls
passed the unchanged gates. Saved full-versus-tail margins and gradient diagnostics
are exactly0; summary preserves native/captured branch relative discrepancy separately.

Actual cost:152forward/8backward, comprising56full transformer,52native-tail,
16local native,20TC and8JVP forward operations. Worker time20.0003seconds;
160unique scheduled operations completed. No old FIT capture or fitting repeated.
This is operator qualification on a tiny fixed technical set, not PILOT/TEST, power
evidence or support for B1–B3. No general full-generation equivalence is established.

The original pre-run review and independently reviewed concurrency migration remain
bound. Existing CPU stages and legacylock were preserved; handover retired only idle
queue processes. A PILOT is independent and started after this model process ended.
Completion review remains pending; no model/tests/bootstrap rerun for this report.
'''
    (STAGE/'REPORT_COMPLETION_v1.md').write_text(report,encoding='utf-8')
    pre=read(STAGE/'pre_run_snapshot_v1.json')
    migration=BASE/'sol_parallel_acceptance/concurrency_migration_v1/snapshot_v3.json'
    files=dict(pre['payload']['files'])
    files.update(read(migration)['payload']['files'])
    extras=[migration,BASE/'astra_goals_concurrency_review/concurrency_review_v3.json',BASE/'concurrency_handover_v1.json']
    for p in extras:files[p.relative_to(ROOT).as_posix()]=sha(p)
    for p in STAGE.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc':
            files[p.relative_to(ROOT).as_posix()]=sha(p)
    write(STAGE/'completion_outputs_manifest_v1.json',dict(files=files))
    contract=read(STAGE/'contract.json')
    contract['id']='AB_B_TAIL_COMPLETION_20261101_v1'
    contract['purpose']='Completion audit of four technical FIT native-tail recipients;152F/8B; no PILOT/TEST/hypothesis result.'
    contract['input_manifests'].append((STAGE/'completion_outputs_manifest_v1.json').relative_to(ROOT).as_posix())
    contract['tracked_files'].extend((STAGE/n).relative_to(ROOT).as_posix() for n in ['completion_summary_v1.json','REPORT_COMPLETION_v1.md'])
    write(STAGE/'completion_contract_v1.json',contract)
    print(json.dumps(summary))

if __name__=='__main__':main()
