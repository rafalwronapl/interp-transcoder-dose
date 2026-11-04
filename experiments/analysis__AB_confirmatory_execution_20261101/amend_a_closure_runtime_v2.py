"""Narrow completion-provenance addition; reuse every existing raw digest."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2]
STAGE=ROOT/'analysis/AB_confirmatory_execution_20261101/A_pilot_ready_v1'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,obj):
    with p.open('x',encoding='utf-8') as f:json.dump(obj,f,indent=2)
receipt=ROOT/'operations/concurrency_runtime_v1/launch_ed2f0be0dbd64677b7c7ea15f8ab3278.json'
r=read(receipt)
if r['returncode']!=0 or r['lane']!='model' or r['snapshot_sha256']!=read(STAGE/'pre_run_snapshot_v1.json')['snapshot_sha256']:
    raise ValueError('Actual runtime completion does not match A PILOT')
manifest=read(STAGE/'completion_outputs_manifest_v1.json')
manifest['files'][receipt.relative_to(ROOT).as_posix()]=sha(receipt)
for name in ['completion_outputs_manifest_v1.json','completion_contract_v1.json','completion_snapshot_v1.json']:
    p=STAGE/name;manifest['files'][p.relative_to(ROOT).as_posix()]=sha(p)
write(STAGE/'completion_outputs_manifest_v2.json',manifest)
contract=read(STAGE/'completion_contract_v1.json')
contract['id']='AB_A_PILOT_COMPLETION_20261101_v2'
contract['input_manifests']=[p.replace('completion_outputs_manifest_v1.json','completion_outputs_manifest_v2.json') for p in contract['input_manifests']]
contract['purpose']+=' Exact immutable canonical child exit0 receipt added; all raw arrays/science unchanged.'
write(STAGE/'completion_contract_v2.json',contract)
print(json.dumps(dict(added_runtime_receipt=str(receipt),returncode=r['returncode'],raw_recomputed=False)))
