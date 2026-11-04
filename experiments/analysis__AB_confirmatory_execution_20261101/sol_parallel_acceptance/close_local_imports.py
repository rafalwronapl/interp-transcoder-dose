"""Metadata-only CLI reusing the exact actual PILOT local-import closure."""
import argparse,hashlib,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'analysis/AB_confirmatory_execution_20261101/close_short_pilot_imports_v1.py'
spec=importlib.util.spec_from_file_location('accepted_pilot_closure',SOURCE)
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)

def close(contract_path):
    path=(ROOT/contract_path).resolve()
    if not path.is_relative_to(ROOT):raise ValueError('Contract outside workspace')
    if any(path.parent.glob('*snapshot*.json')):raise ValueError('Refuse already frozen packet')
    backup=path.parent/'contract_builder_v1.json';receipt=path.parent/'source_closure_addition_v1.json'
    if backup.exists() or receipt.exists():raise ValueError('Existing closure evidence; do not repeat')
    original=path.read_bytes();contract=json.loads(original)
    bound=helper.closure(contract['tracked_files'])
    additions=sorted(set(bound)-set(contract['tracked_files']))
    contract['tracked_files']+=additions
    updated=(json.dumps(contract,indent=2)+'\n').encode('utf-8')
    if path.read_bytes()!=original:raise ValueError('Concurrent contract mutation')
    backup.write_bytes(original);path.write_bytes(updated)
    digest=lambda value:hashlib.sha256(value).hexdigest()
    result=dict(kind='metadata_only_static_local_import_closure',original_contract_sha256=digest(original),updated_contract_sha256=digest(updated),added_files={n:bound[n] for n in additions},closure_helper_sha256=digest(SOURCE.read_bytes()),scientific_source_edits=0,config_or_corpus_or_schedule_edits=0,new_model_calls=0)
    receipt.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--contract',required=True)
    args=parser.parse_args();print(json.dumps(close(args.contract),indent=2))
