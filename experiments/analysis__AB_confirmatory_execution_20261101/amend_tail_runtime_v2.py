"""Add final execution receipt without changing or recomputing accepted raw data."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2]
STAGE=ROOT/'analysis/AB_confirmatory_execution_20261101/B_tail_qualification_v1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(p,obj):
    with p.open('x',encoding='utf-8') as f:json.dump(obj,f,indent=2)
receipt=ROOT/'operations/concurrency_runtime_v1/launch_4955312abd834036a9ab017dd7b991d9.json'
actual=read(receipt)
if actual['returncode']!=0 or actual['snapshot_sha256']!=read(STAGE/'pre_run_snapshot_v1.json')['snapshot_sha256']:
    raise ValueError('Runtime completion does not match accepted tail')
amendment=STAGE/'runtime_provenance_amendment_v2.json'
write(amendment,dict(scope='Narrow additive execution provenance only; original accepted b3a snapshot preserved.',
    raw_recomputed=False,scientific_sources_changed=False,thresholds_changed=False,new_model_calls=0,
    actual_runtime_receipt=receipt.relative_to(ROOT).as_posix(),returncode=0,
    prior_approval='completion_review_astra_v1.json'))
manifest=read(STAGE/'completion_outputs_manifest_v1.json')
for p in [receipt,amendment]+[STAGE/n for n in ['completion_outputs_manifest_v1.json','completion_contract_v1.json',
    'completion_snapshot_v1.json','completion_review_astra_v1.json','completion_canonical_verify_astra_v1.json']]:
    manifest['files'][p.relative_to(ROOT).as_posix()]=sha(p)
write(STAGE/'completion_outputs_manifest_v2.json',manifest)
contract=read(STAGE/'completion_contract_v1.json');contract['id']='AB_B_TAIL_COMPLETION_20261101_v2'
contract['purpose']+=' Additive final canonical child exit0 receipt; original scientific acceptance and raw data unchanged.'
contract['input_manifests']=[p.replace('completion_outputs_manifest_v1.json','completion_outputs_manifest_v2.json') for p in contract['input_manifests']]
write(STAGE/'completion_contract_v2.json',contract)
print(json.dumps(dict(receipt=str(receipt),returncode=0,raw_recomputed=False)))
