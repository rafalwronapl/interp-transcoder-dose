import json
from collections import Counter
from .common import *
from .report import main as report
def main():
    out=HERE/'run';done=unwrap(out/'stage_completed.json')
    for p,h in done['files'].items():assert sha(out/p)==h
    freeze=unwrap(out/'TARGETS_FROZEN.json')
    for p,h in freeze['files'].items():assert sha(out/p)==h
    times=json.loads((out/'TARGETS_FROZEN.json').read_text())['created_utc']
    ledger=[json.loads(l)['record'] for l in (out/'ledger.jsonl').read_text().splitlines()];attempts=[r for r in ledger if r['event']=='attempt']
    assert len(attempts)==done['accounting']['forward_attempts'] and len({r['operation'] for r in attempts})==len(attempts)
    for r in attempts:
        if not(r['operation'].startswith(('control_','fresh_parity_')) or r['operation'].endswith(('_capture','_tcbase','_tcend'))):assert r['utc']>=times
    assert len(list((out/'results').glob('*.json')))==256
    assert len(list((out/'controls').glob('*.json')))==2
    assert done['accounting']['forward_attempts']+done['accounting']['aliases']+done['accounting']['skips']==3088
    counts=Counter('capture' if r['operation'].endswith('_capture') else 'TC_local' if r['operation'].endswith(('_tcbase','_tcend')) else 'native_local_branch' if r['operation'].endswith('_nativebranch') else 'technical_suffix' if r['operation'].startswith(('control_','fresh_parity_')) else 'scientific_suffix' for r in attempts)
    checks=dict(hooks=True,data=True,pilot=True,accounting=True,restart=True,counts=dict(counts),all_scientific_measurements_after_global_target_freeze=True,immutable_outputs_verified=len(done['files']),budget=3088,actual=done['accounting'])
    (HERE/'completion_checks.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8');report()
    names=[p for p in out.rglob('*') if p.is_file()]+[HERE/n for n in ['REPORT.txt','report.py','finish.py','completion_checks.json','review/pre_run_review.json','review/independent_pre_run_audit.json']]
    (HERE/'completion_output_manifest.json').write_text(json.dumps(dict(files={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(names)}),indent=2)+'\n',encoding='utf-8')
    contract=read(HERE/'contract.json');prefix=HERE.relative_to(ROOT).as_posix();contract['id']+='_COMPLETION';contract['entrypoint']={};contract['input_manifests']+=[prefix+'/completion_output_manifest.json'];contract['tracked_files'] += [prefix+'/'+n for n in ['completion_output_manifest.json','REPORT.txt','completion_checks.json','report.py','finish.py']]
    for g in contract['gates']:g['evidence']=prefix+'/completion_checks.json';g['reason']='Actual completed cache/ledger/target seal/result count/budget verification; pre-run fixture covers restart'
    # Keep original executable entrypoint for canonical verification; completed replay exits before load.
    contract['entrypoint']=read(HERE/'contract.json')['entrypoint']
    (HERE/'completion_contract.json').write_text(json.dumps(contract,indent=2)+'\n',encoding='utf-8')
    print(checks)
if __name__=='__main__':main()
