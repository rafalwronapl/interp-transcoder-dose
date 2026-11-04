"""Portable saved-metadata/report inspection only: stdlib, no inference imports."""
import argparse,hashlib,json
from pathlib import Path
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['metadata','saved-report']);p.add_argument('--root',default='.');a=p.parse_args()
    root=Path(a.root).resolve();table=json.loads((Path(__file__).parent/'artifact_reproducibility_table.json').read_text(encoding='utf-8'))
    if a.mode=='metadata':
        missing=[]
        for name,h in table['source_files_sha256'].items():
            f=root/name
            if not f.exists():missing.append(name);continue
            if f.suffix.lower() in ['.safetensors','.bin','.pt','.pth'] or f.stat().st_size>16777216:raise ValueError('Refuse weight/large raw file')
            if hashlib.sha256(f.read_bytes()).hexdigest()!=h:raise ValueError('Changed supplied metadata/source: '+name)
        print(json.dumps(dict(metadata_verified=len(table['source_files_sha256'])-len(missing),missing=missing,weights_required=False,result_status=table['final_analysis']['status'],recorded_gaps=[g['id'] for g in table['gaps']]),indent=2))
        return 2 if missing else 0
    info=table['final_analysis'];f=root/info['result']
    if info['result_sha256'] is None or not f.exists():print('Final saved B report not yet published/bound; this command never generates it.');return 2
    raw=f.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=info['result_sha256']:raise ValueError('Saved final report hash changed')
    obj=json.loads(raw)
    if digest(obj['payload'])!=obj['payload_sha256']:raise ValueError('Saved report payload checksum changed')
    result=obj['payload']['result']
    if result['primary_inference_authorized'] is not False or result['original_family_eligibility'] is not False:raise ValueError('Changed descriptive-only scope')
    print(json.dumps(dict(status=result['status'],blocks=result.get('blocks'),cells=len(result.get('cells',[])),finite_corpus_contrasts=result.get('finite_corpus_contrasts'),qualified_interval_scope=result.get('qualified_interval_scope'),statistical_or_model_calls=0),indent=2))
    return 0
if __name__=='__main__':raise SystemExit(main())
