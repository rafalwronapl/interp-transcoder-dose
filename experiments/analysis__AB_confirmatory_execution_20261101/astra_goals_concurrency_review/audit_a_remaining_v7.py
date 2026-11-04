"""Incremental immutable A TEST arithmetic audit; never reads live telemetry.

Author owns admission/telemetry wrappers, not the frozen numerical worker.
No forward, replay, fit, bootstrap, hypothesis calculation or mutable ledger read.
"""
import hashlib,json
from functools import lru_cache
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
PACKET=ROOT/'analysis/A_estimation_v7/TEST_v1';RUN=PACKET/'run'
OUT=Path(__file__).resolve().parent/'a_raw_remaining_v7'
REUSED=ROOT/'analysis/AB_confirmatory_execution_20261101/sol_parallel_acceptance/A_TEST_raw_v7'
def digest(q):return hashlib.sha256(json.dumps(q,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def read(path):
    data=path.read_bytes();q=json.loads(data)
    assert digest(q['payload'])==q['payload_sha256'],str(path)
    return q['payload'],hashlib.sha256(data).hexdigest()

def main():
    OUT.mkdir(exist_ok=True);cfg=json.loads((PACKET/'config.json').read_text())
    corpus=json.loads((ROOT/cfg['corpus']).read_text())['documents'];docs={d['id']:d for d in corpus};selected=[docs[i] for i in cfg['documents']]
    assert len(selected)==5120 and len(docs)==5120 and cfg['fit_cohorts']==cfg['control_documents']==[] and cfg['evaluate_cohorts']==['r0']
    assert not cfg['imports'] and not cfg['reuse_operations'] and not cfg['reuse_stages']
    blocks=sorted({d['block'] for d in selected});assert len(blocks)==256
    assert all(d['study']=='A' and d['split']=='TEST' and d['donor'] in docs for d in selected)
    arms=['P','U0','Uctrl','U2','U5'];frames=['T0','T2','T5','T6','T7']
    operations={f'capture_{d["id"]}' for d in selected}|{f'suffix_{d["id"]}_native' for d in selected}|{f'suffix_{d["id"]}_r0_{a}' for d in selected for a in arms}
    scheduled=json.loads((ROOT/cfg['schedule']).read_text())['operations']
    assert len(scheduled)==35840 and {q['id'] for q in scheduled}==operations and all(q['kind']=='forward' for q in scheduled)
    assert {p.stem for p in (RUN/'completed').glob('*.json')}==operations
    assert len(list((RUN/'cache').glob('*.json')))==35840 and len(list((RUN/'results/r0').glob('*.json')))==5120
    identity,_=read(RUN/'identity.json');assert read(RUN/'controls.json')[0]==[] and not list(RUN.glob('FIT_*.json'))
    model=json.loads((ROOT/cfg['model_identity']).read_text())['A'];assert identity['model']==digest(model)
    dependencies=['ab_confirmatory_20261101/'+n for n in ['__init__.py','worker_a.py','prepare.py','native.py','fitting.py','runtime.py']]+['research_checks/'+n for n in ['__init__.py','gate.py','persistence.py','reachability.py']]
    sources={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in dependencies}
    cfg_hash=hashlib.sha256((PACKET/'config.json').read_bytes()).hexdigest()
    assert identity['code']==digest(dict(sources=sources,config_sha256=cfg_hash))
    verified=np.load(Path(__file__).parent/'a_primary_v7/verified_components.npz',allow_pickle=False)
    errors={'L':verified['readout_errors'].copy(),'V':verified['vector_errors'].copy()};seen=set();all_files={};max_relative=0.
    tokens=json.loads((ROOT/cfg['tokens']).read_text())
    @lru_cache(maxsize=64)
    def cached(operation):
        cp=RUN/'completed'/f'{operation}.json';completed,cp_hash=read(cp);assert completed['operation']==operation
        key=completed['request'];path=RUN/'cache'/f'{key}.json';raw,raw_hash=read(path);r=raw['request']
        assert set(r)=={'model_identity','code_identity','document','intervention','readout'} and digest(r)==key
        assert r['model_identity']==identity['model'] and r['code_identity']==identity['code']
        return raw,{cp.relative_to(RUN).as_posix():cp_hash,path.relative_to(RUN).as_posix():raw_hash}
    for bi,block in enumerate(blocks):
        files={};max_block=0.;block_docs=[d for d in selected if d['block']==block];assert len(block_docs)==20
        cached_path=(REUSED if bi<39 else OUT)/f'block_{bi:03d}.json'
        if cached_path.exists():
            prior=json.loads(cached_path.read_text());assert prior['block']==block and prior['config_sha256']==cfg_hash and prior['original_scientific_identity']==identity and len(prior['files'])==300
            all_files.update(prior['files']);max_relative=max(max_relative,prior['max_vector_relative'])
            for d in block_docs:seen.add((bi,frames.index(d['frame']),2*d['side']+d['q']))
            continue
        for d in block_docs:
            i=d['id'];cap,hashes=cached('capture_'+i);files.update(hashes);donor,hashes=cached('capture_'+d['donor']);files.update(hashes)
            assert cap['request']['document']==dict(document=d,tokens=tokens[i]) and cap['request']['intervention']==dict(mode='native')
            natural=cap['result'];other=donor['result'];dy=np.asarray(other['y'])-np.asarray(natural['y'])
            record,h=read(RUN/'results/r0'/f'{i}.json');files[f'results/r0/{i}.json']=h
            assert record['document']==d and record['cohort']=='r0'
            native,hashes=cached(f'suffix_{i}_native');files.update(hashes);h=native['result'];assert record['native_h']==h
            assert native['request']['intervention']['R']==natural['R'] and native['request']['intervention']['arm']=='native'
            assert np.array_equal(np.asarray(native['request']['intervention']['M']),np.asarray(natural['y'])+dy)
            coordinate=(bi,frames.index(d['frame']),2*d['side']+d['q']);assert coordinate not in seen;seen.add(coordinate)
            for ai,arm in enumerate(arms):
                raw,hashes=cached(f'suffix_{i}_r0_{arm}');files.update(hashes);request=raw['request']
                assert request['document']==dict(document=d,tokens=tokens[i]) and request['readout']==dict(orientation='is-minus-are')
                assert request['intervention']['mode']=='suffix' and request['intervention']['arm']=='r0_'+arm and request['intervention']['R']==natural['R']
                value=record['values'][arm];assert value['prediction']==raw['result'] and value['L']==(raw['result']-h)**2
                residual=np.asarray(request['intervention']['M'])-np.asarray(other['y']);v=float(residual@residual)
                relative=abs(v-value['V'])/max(1.,value['V']);assert relative<1e-12;max_block=max(max_block,relative)
                for metric in errors:errors[metric][coordinate+(ai,)]=value[metric]
            zero=record['values']['zero'];assert zero['prediction']==0 and zero['L']==h*h and np.isclose(zero['V'],dy@dy,rtol=1e-12,atol=1e-9)
        assert len(files)==300;all_files.update(files);max_relative=max(max_relative,max_block)
        report=dict(block=block,documents=20,files=files,max_vector_relative=max_block,original_scientific_identity=identity,config_sha256=cfg_hash)
        path=OUT/f'block_{bi:03d}.json'
        if path.exists():assert json.loads(path.read_text())==report
        else:path.write_text(json.dumps(report,sort_keys=True)+'\n')
        if (bi+1)%16==0:print(f'A raw arithmetic audited {bi+1}/256 blocks',flush=True)
    assert len(seen)==5120 and len(all_files)==76800 and all(np.isfinite(v).all() and (v>=0).all() for v in errors.values())
    np.savez(OUT/'reconstructed_error_tensors.npz',readout_errors=errors['L'],vector_errors=errors['V'],block_ids=np.asarray(blocks))
    result=dict(ok=True,blocks=256,documents=5120,operations=35840,immutable_scientific_files=76800,max_vector_error_relative=max_relative,
        file_hashes=all_files,model_calls=0,replay_calls=0,bootstrap_calls=0,live_STATUS_or_ledger_read=False,
        scope='Original numerical worker outputs audited: first39blocks reuse separately hash-verified Sol receipts, remaining217 audited by Astra. No model/replay/bootstrap or live STATUS/ledger reads. Separate focused primary tensor review already complete; final closure/ledger acceptance pending.')
    (OUT/'audit_result.json').write_text(json.dumps(result,sort_keys=True)+'\n');print('A raw arithmetic audit COMPLETE',flush=True)
if __name__=='__main__':main()
