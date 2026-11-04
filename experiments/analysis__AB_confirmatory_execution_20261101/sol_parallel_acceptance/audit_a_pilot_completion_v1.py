"""Receipt/array acceptance only: no model, worker replay, fitting or bootstrap."""
import hashlib,json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'analysis/AB_confirmatory_execution_20261101'
PACKET=BASE/'A_pilot_ready_v1';RUN=PACKET/'run';ASSEMBLY=BASE/'A_pilot_assembly_v1'
OUT=Path(__file__).resolve().parent/'A_pilot_completion_v1'
def digest(q):return hashlib.sha256(json.dumps(q,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def receipt(p):
    q=json.loads(p.read_text(encoding='utf-8'));assert digest(q['payload'])==q['payload_sha256'],str(p)
    return q['payload']
def main():
    OUT.mkdir(exist_ok=True)
    cfg=json.loads((PACKET/'config.json').read_text());corpus=json.loads((ROOT/cfg['corpus']).read_text())['documents'];tokens=json.loads((ROOT/cfg['tokens']).read_text())
    docs={d['id']:d for d in corpus};selected=[docs[x] for x in cfg['documents']]
    assert len(selected)==640 and len(set(cfg['documents']))==640
    assert cfg['fit_cohorts']==[] and cfg['control_documents']==[] and cfg['evaluate_cohorts']==['r0']
    assert cfg['reuse_stages']=={} and cfg['reuse_operations']=={} and not cfg.get('imports')
    blocks=sorted({d['block'] for d in selected});assert len(blocks)==32
    assert all(d['split']=='PILOT' and d['study']=='A' and d['donor'] in cfg['documents'] for d in selected)
    arms=['P','U0','Uctrl','U2','U5'];frames=['T0','T2','T5','T6','T7']
    expected={f'capture_{d["id"]}' for d in selected}|{f'suffix_{d["id"]}_native' for d in selected}|{f'suffix_{d["id"]}_r0_{a}' for d in selected for a in arms}
    scheduled=json.loads((ROOT/cfg['schedule']).read_text())['operations']
    assert len(scheduled)==4480 and {q['id'] for q in scheduled}==expected and all(q['kind']=='forward' for q in scheduled)
    closure=receipt(RUN/'stage_completed.json');identity=receipt(RUN/'identity.json')
    assert closure['identity']==identity and closure['scope']=='PILOT' and closure['attempted_operations']==4480
    actual={p.relative_to(RUN).as_posix() for p in RUN.rglob('*') if p.is_file() and p.name!='stage_completed.json'}
    assert set(closure['files'])==actual
    for name,h in closure['files'].items():assert sha(RUN/name)==h,name
    assert receipt(RUN/'controls.json')==[] and not list(RUN.glob('FIT_*.json'))
    ledger=[json.loads(l) for l in (RUN/'ledger.jsonl').read_text().splitlines()]
    for line in ledger:assert line['sha256']==digest(line['record'])
    attempts=[q['record'] for q in ledger if q['record']['event']=='attempt'];computed=[q['record'] for q in ledger if q['record']['event']=='computed']
    assert len(ledger)==8960 and len(attempts)==len(computed)==4480
    assert {x['operation'] for x in attempts}==expected and {x['operation'] for x in computed}==expected
    attempt={x['operation']:x for x in attempts};done={x['operation']:x for x in computed}
    assert len(list((RUN/'completed').glob('*.json')))==4480
    assert len(list((RUN/'cache').glob('*.json')))==4480
    cache={}
    for operation in expected:
        completed=receipt(RUN/'completed'/f'{operation}.json');key=completed['request']
        assert completed['operation']==operation and attempt[operation]['request']==done[operation]['request']==key
        assert attempt[operation]['kind']=='forward' and done[operation]['coupled_operations']==[operation]
        raw=receipt(RUN/'cache'/f'{key}.json');request=raw['request']
        assert digest(request)==key and set(request)=={'model_identity','code_identity','document','intervention','readout'}
        assert request['model_identity']==identity['model'] and request['code_identity']==identity['code']
        cache[operation]=raw
    errors={k:np.full((32,5,4,5),np.nan) for k in ['L','V']};seen=set();max_vector_relative=0.
    results=list((RUN/'results/r0').glob('*.json'));assert len(results)==640
    for d in selected:
        i=d['id'];cap=cache['capture_'+i];natural=cap['result'];donor=cache['capture_'+d['donor']]['result']
        assert cap['request']['document']==dict(document=d,tokens=tokens[i])
        assert cap['request']['intervention']==dict(mode='native')
        y=np.asarray(natural['y']);dy=np.asarray(donor['y'])-y
        record=receipt(RUN/'results/r0'/f'{i}.json');assert record['document']==d and record['cohort']=='r0'
        # worker's suffix lambda stores the change from natural margin already.
        h=cache[f'suffix_{i}_native']['result'];assert record['native_h']==h
        coordinate=(blocks.index(d['block']),frames.index(d['frame']),2*d['side']+d['q']);assert coordinate not in seen;seen.add(coordinate)
        for name in arms:
            suffix=cache[f'suffix_{i}_r0_{name}'];req=suffix['request']
            assert req['document']==dict(document=d,tokens=tokens[i]) and req['readout']==dict(orientation='is-minus-are')
            assert req['intervention']['mode']=='suffix' and req['intervention']['arm']=='r0_'+name
            assert req['intervention']['R']==natural['R']
            pred=suffix['result'];value=record['values'][name]
            assert value['prediction']==pred and value['L']==(pred-h)**2
            vector=np.asarray(req['intervention']['M'])-np.asarray(donor['y'])
            v=float(vector@vector);relative=abs(v-value['V'])/max(1.,value['V']);max_vector_relative=max(max_vector_relative,relative)
            assert relative<1e-12
            for metric in errors:errors[metric][coordinate+(arms.index(name),)]=value[metric]
        zero=record['values']['zero'];assert zero['prediction']==0 and zero['L']==h*h
        assert np.isclose(zero['V'],dy@dy,rtol=1e-12,atol=1e-9)
    assert len(seen)==640
    assembled=receipt(ASSEMBLY/'assembly.json');manifest=json.loads((ASSEMBLY/'manifest.json').read_text())
    assert assembled['blocks']==32 and assembled['cohorts']==1 and assembled['new_model_calls']==0
    assert manifest['study']=='A' and manifest['split']=='PILOT' and manifest['cohorts']==['r0'] and manifest['blocks']==blocks
    for name,h in assembled['files'].items():assert sha(ASSEMBLY/name)==h
    for name,h in manifest['files'].items():assert sha(Path(name))==h,name
    for name,h in assembled['request']['sources'].items():assert sha(Path(name))==h,name
    with np.load(ASSEMBLY/'arrays.npz',allow_pickle=False) as arrays:
        assert set(arrays.files)=={'readout_errors','vector_errors','A_power','block_ids'}
        for key,metric in [('readout_errors','L'),('vector_errors','V')]:assert np.array_equal(arrays[key],errors[metric]) and np.isfinite(arrays[key]).all()
        l=errors['L'].mean(2);v=errors['V'].mean(2)
        independent=np.stack([(l[:,3:,2]-l[:,3:,3]).mean(1),v[:,2,3]-v[:,2,4],l[:,2,4]-l[:,2,3],l[:,2,1]-l[:,2,0]],axis=1)
        assert np.array_equal(arrays['A_power'],independent) and np.array_equal(arrays['block_ids'],blocks)
        assert np.isfinite(arrays['A_power']).all()
    result=dict(ok=True,blocks=32,documents=640,full_forwards=640,local_forwards=3840,backward=0,
                unique_attempts=4480,unique_computed=4480,closed_files=len(closure['files']),
                stage_receipt_sha256=sha(RUN/'stage_completed.json'),assembly_receipt_sha256=sha(ASSEMBLY/'assembly.json'),
                max_vector_error_reconstruction_relative=max_vector_relative,
                arrays_independently_reconstructed=True,no_model_calls=True,no_worker_replay=True,no_bootstrap=True,
                limits='Verifies saved outputs and acquisition/assembly consistency; no independent model rerun and no hypothesis, chosen TEST N, power or population claim.')
    (OUT/'audit_result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
