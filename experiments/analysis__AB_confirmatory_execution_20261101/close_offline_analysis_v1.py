"""Bind already computed zero-model outputs; never execute statistics."""
import argparse, hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),
                                    ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def create(path,value):
    with path.open('x',encoding='utf-8') as stream:json.dump(value,stream,indent=2)
def main():
    parser=argparse.ArgumentParser()
    for key in ('packet','runtime-receipt','result'):parser.add_argument('--'+key,required=True)
    parser.add_argument('--review-evidence',action='append',default=[])
    args=parser.parse_args();stage=(ROOT/args.packet).resolve()
    contract=read(stage/'contract.json');pre=read(stage/'pre_run_snapshot_v1.json')
    if contract['budget']!={'forward':0,'backward':0}:raise ValueError('Zero-model analyses only')
    if read(ROOT/contract['schedule'])['operations']:raise ValueError('Nonempty model schedule')
    runtime_path=ROOT/args.runtime_receipt;runtime=read(runtime_path)
    if runtime['returncode']!=0 or runtime['snapshot_sha256']!=pre['snapshot_sha256']:
        raise ValueError('Actual matching canonical exit0 required')
    result_path=(stage/args.result).resolve()
    if not result_path.is_relative_to(stage):raise ValueError('Result scope escape')
    result=read(result_path)
    if 'payload_sha256' in result and digest(result['payload'])!=result['payload_sha256']:
        raise ValueError('Result payload corrupt')
    files=dict(pre['payload']['files'])
    for path in stage.rglob('*'):
        if path.is_file() and not path.name.startswith('completion_'):
            files[path.relative_to(ROOT).as_posix()]=sha(path)
    files[runtime_path.relative_to(ROOT).as_posix()]=sha(runtime_path)
    launch=read(stage/'launch_receipt_v1.json');command=launch['args']
    for option in ('--policy','--policy-snapshot','--policy-review'):
        path=ROOT/command[command.index(option)+1]
        files[path.relative_to(ROOT).as_posix()]=sha(path)
        if option=='--policy-snapshot':files.update(read(path)['payload']['files'])
    for name in args.review_evidence:
        path=(ROOT/name).resolve()
        if not path.is_relative_to(ROOT):raise ValueError('Review scope escape')
        files[path.relative_to(ROOT).as_posix()]=sha(path)
    source=Path(__file__).resolve();files[source.relative_to(ROOT).as_posix()]=sha(source)
    summary=dict(forward=0,backward=0,runtime_returncode=0,
                 result=result_path.relative_to(ROOT).as_posix(),result_sha256=sha(result_path),
                 new_statistical_computations_by_closure=0,independent_completion_review='pending',
                 scope='Closure of previously computed frozen analysis; no bootstrap/model/refitting/replay')
    create(stage/'completion_summary_v1.json',summary)
    path=stage/'completion_summary_v1.json';files[path.relative_to(ROOT).as_posix()]=sha(path)
    create(stage/'completion_outputs_manifest_v1.json',dict(files=files))
    contract['id']+='_COMPLETION';contract['purpose']=summary['scope']
    contract['input_manifests'].append((stage/'completion_outputs_manifest_v1.json').relative_to(ROOT).as_posix())
    create(stage/'completion_contract_v1.json',contract);print(json.dumps(summary))
if __name__=='__main__':main()
