"""Close actual A PILOT evidence and deterministic assembly; no model or MC."""
from pathlib import Path
from datetime import datetime
import hashlib,json
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'analysis/AB_confirmatory_execution_20261101'
STAGE=BASE/'A_pilot_ready_v1'
ASSEMBLY=BASE/'A_pilot_assembly_v1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(p,x):
    if p.exists():raise ValueError('Completion evidence exists; never overwrite')
    p.write_text(json.dumps(x,indent=2),encoding='utf-8')

def main():
    sealed=read(STAGE/'run/stage_completed.json');done=sealed['payload']
    status=read(STAGE/'run/STATUS.json');cfg=read(STAGE/'config.json')
    if status['stage']!='completed' or done['attempted_operations']!=4480:raise ValueError('PILOT not closed')
    if cfg['evaluate_cohorts']!=['r0'] or cfg['fit_cohorts']:raise ValueError('Unexpected FIT selection/refitting')
    assembly=read(ASSEMBLY/'manifest.json');receipt=read(ASSEMBLY/'assembly.json')['payload']
    if assembly['split']!='PILOT' or len(assembly['blocks'])!=32:raise ValueError('Wrong PILOT blocks')
    with np.load(ASSEMBLY/'arrays.npz',allow_pickle=False) as data:
        shapes={k:list(data[k].shape) for k in data.files}
        if not all(np.all(np.isfinite(data[k])) for k in data.files if data[k].dtype.kind in 'fci'):
            raise ValueError('Nonfinite PILOT array')
    started=datetime.fromisoformat(read(STAGE/'launch_receipt_v1.json')['started_utc'])
    finished=datetime.fromisoformat(sealed['created_utc'])
    summary=dict(blocks=32,documents=640,full_transformer=640,local_suffix=3840,backward=0,
        logical_operations=4480,new_FIT_operations=0,new_qualification_calls=0,
        imported_prior_FIT='fixed designated r0; no refit',
        reported_worker_seconds=status['elapsed_seconds'],wall_to_stage_receipt_seconds=(finished-started).total_seconds(),
        stage_receipt_utc=sealed['created_utc'],assembly_shapes=shapes,assembly_model_calls=0,
        scientific_hypothesis_tests=0,TEST_N_selected=False,independent_completion_review='pending')
    write(STAGE/'completion_summary_v1.json',summary)
    report='''# A actual PILOT acquisition and assembly completion

Completed exactly32prespecified lexical blocks/640documents,640full-transformer and
3840local suffix forward operations,0backward. The predesignated frozen r0P/U and
accepted five-group qualification were reused; no new FIT or qualification calls.
All4480scheduled operations are durable. Worker-reported execution781.0036seconds;
wall-to-stage-receipt includes canonical checks, model execution and final hashing.
The separate summary preserves this measured wall time rather than calling it CPU time.

The approved deterministic assembler produced complete A-only PILOT arrays and block
IDs with no deletion, fitting, bootstrap or model calls. Array shapes and finiteness
are recorded without selecting an observed effect. This is PILOT input for the fixed
prospective selector, not a hypothesis result, chosen TESTN or TEST execution.
No readout result was used to change hypothesis, target, threshold or frame selection.

All new raw states/cache/results/ledger, original pre-run approval, actual migration
receipt and assembly sources/outputs are hash-bound. Independent completion review
is pending. No worker replay, old natural capture, fitting or passed numerical suite
was repeated for this report. B precision failure and A's separate eligible256candidate
remain distinct; selector can still return infeasible.
'''
    (STAGE/'REPORT_COMPLETION_v1.md').write_text(report,encoding='utf-8')
    pre=read(STAGE/'pre_run_snapshot_v1.json');files=dict(pre['payload']['files'])
    for snap in [BASE/'A_remaining_preparation/maintenance_snapshot_v2.json',
        BASE/'sol_parallel_acceptance/concurrency_migration_v1/snapshot_v3.json']:
        files.update(read(snap)['payload']['files']);files[snap.relative_to(ROOT).as_posix()]=sha(snap)
    for name,h in assembly['files'].items():
        path=Path(name)
        if not path.is_absolute():path=ASSEMBLY/path
        files[path.relative_to(ROOT).as_posix()]=h
    # Bind statistical assembly identity, including sources not otherwise consumed by worker.
    def bind_identity(obj):
        if isinstance(obj,dict):
            for k,v in obj.items():
                if isinstance(v,str) and len(v)==64:
                    p=Path(k)
                    if p.is_absolute() and p.is_file():files[p.relative_to(ROOT).as_posix()]=v
                bind_identity(v)
        elif isinstance(obj,list):
            for v in obj:bind_identity(v)
    bind_identity(receipt)
    for p in [BASE/'concurrency_handover_v1.json',BASE/'astra_goals_concurrency_review/concurrency_review_v3.json']:
        files[p.relative_to(ROOT).as_posix()]=sha(p)
    for folder in [STAGE,ASSEMBLY]:
        for p in folder.rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc':
                files[p.relative_to(ROOT).as_posix()]=sha(p)
    write(STAGE/'completion_outputs_manifest_v1.json',dict(files=files))
    contract=read(STAGE/'contract.json');contract['id']='AB_A_PILOT_COMPLETION_20261101_v1'
    contract['purpose']='Completion audit of32-block actual PILOT and deterministic arrays;640full+3840local,0back; no TEST or selectedN.'
    contract['input_manifests'].append((STAGE/'completion_outputs_manifest_v1.json').relative_to(ROOT).as_posix())
    contract['tracked_files'].extend((STAGE/n).relative_to(ROOT).as_posix() for n in ['completion_summary_v1.json','REPORT_COMPLETION_v1.md'])
    write(STAGE/'completion_contract_v1.json',contract)
    print(json.dumps(summary))

if __name__=='__main__':main()
