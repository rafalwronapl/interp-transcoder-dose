"""Incremental immutable Llama evaluation audit; no model, fitting or bootstrap."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['MKL_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
os.environ['NUMEXPR_NUM_THREADS']='1'
if os.name=='nt':
    import ctypes
    from ctypes import wintypes
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.GetCurrentProcess.restype=wintypes.HANDLE
    kernel.SetPriorityClass.argtypes=[wintypes.HANDLE,wintypes.DWORD]
    if not kernel.SetPriorityClass(kernel.GetCurrentProcess(),0x4000):raise ctypes.WinError(ctypes.get_last_error())
    kernel.GetPriorityClass.argtypes=[wintypes.HANDLE]
    kernel.GetPriorityClass.restype=wintypes.DWORD
    assert kernel.GetPriorityClass(kernel.GetCurrentProcess())==0x4000
import argparse,hashlib,json,sys,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from research_checks.gate import digest
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def receipt(p):
    q=json.loads(p.read_text());assert digest(q['payload'])==q['payload_sha256'];return q['payload']
def audit(packet):
    stage=ROOT/packet;cfg=json.loads((stage/'config.json').read_text());run=ROOT/cfg['output']
    assert cfg['study']=='A' and cfg['model']=='llama' and cfg['phase'] in ['PILOT','TEST']
    phase=cfg['phase'];n=32 if phase=='PILOT' else 256
    docs=json.loads((ROOT/cfg['corpus']).read_text())['documents'];byid={d['id']:d for d in docs}
    assert len(docs)==8*n and len({d['block'] for d in docs})==n
    shared=json.loads((ROOT/'analysis/A_short_replication_qwen_20261101/shared_corpus_v1.json').read_text())['documents']
    assert docs==[d for d in shared if d['split']==phase and d['index']<n]
    tokens=json.loads((ROOT/cfg['tokens']).read_text());fit_path=ROOT/cfg['frozen_fits']['r0'];fit_record=receipt(fit_path);fit=fit_record['fit']
    dependency_files=['a_short_llama_20261101/'+x for x in ['__init__.py','worker.py','native.py','schedule.py','admission.py','statistics.py']]
    dependency_files+=['ab_confirmatory_20261101/'+x for x in ['__init__.py','native.py','fitting.py','runtime.py','prepare.py','eligibility_paths_v5.py','offline_io_v3.py','offline_io_v4.py','safe_statistics.py','statistics.py']]
    dependency_files+=['research_checks/'+x for x in ['__init__.py','gate.py','persistence.py','reachability.py']]
    identity=dict(model=digest(json.loads((ROOT/cfg['model_identity']).read_text())['A']),code=digest(dict(sources={name:sha(ROOT/name) for name in dependency_files},config_sha256=sha(stage/'config.json'))),corpus=sha(ROOT/cfg['corpus']),tokens=sha(ROOT/cfg['tokens']),config=packet+'/config.json',frozen_fit_hashes={name:sha(ROOT/path) for name,path in cfg['frozen_fits'].items()})
    assert receipt(run/'identity.json')==identity and fit_record['identity']['model']==identity['model']
    assert cfg['documents']==[d['id'] for d in docs] and not cfg['fit_cohorts'] and not cfg['control_documents'] and cfg['evaluate_cohorts']==['r0']
    output=Path(__file__).resolve().parent/f'Llama_{phase}_raw_v1';output.mkdir(exist_ok=True)
    ready={d['id'] for d in docs if (run/'results/r0'/(d['id']+'.json')).exists() and not (output/(d['id']+'_result.json')).exists()}
    needed=ready|{byid[name]['donor'] for name in ready}
    caps={};proofs={};operations=set()
    def operation(op,d,intervention,files):
        cp=run/'completed'/(op+'.json')
        if not cp.exists():return None
        c=receipt(cp);assert c['operation']==op
        p=run/'cache'/(c['request']+'.json');cached=receipt(p)
        req=dict(model_identity=identity['model'],code_identity=identity['code'],document=dict(document=d,tokens=tokens[d['id']]),intervention=intervention,readout=(dict(answer_ids=tokens[d['id']]['answer_ids'],orientation='is-minus-are') if intervention['mode']=='native' else dict(orientation='is-minus-are')))
        assert cached['request']==req and digest(req)==c['request']
        files[cp.relative_to(ROOT).as_posix()]=sha(cp);files[p.relative_to(ROOT).as_posix()]=sha(p)
        operations.add(op);return cached['result']
    for d in docs:
        previous=output/(d['id']+'_capture.json')
        if previous.exists() and d['id'] not in needed:
            proofs[d['id']]=json.loads(previous.read_text());assert proofs[d['id']]['identity']==identity and proofs[d['id']]['document']==d
            operations.add('capture_'+d['id']);continue
        files={};r=operation('capture_'+d['id'],d,dict(mode='native'),files)
        if r is None:continue
        assert set(r)=={'R','x','y','margin'}
        assert all(np.asarray(r[k]).shape==(2048,) and np.isfinite(r[k]).all() for k in ['R','x','y']) and np.isfinite(r['margin'])
        caps[d['id']]=r;proofs[d['id']]=dict(document=d,files=files,identity=identity)
        target=output/(d['id']+'_capture.json')
        if target.exists():assert json.loads(target.read_text())==proofs[d['id']]
        else:target.write_text(json.dumps(proofs[d['id']],indent=2)+'\n',encoding='utf-8')
    w=np.asarray(fit['P']['w'],float);intercept=np.asarray(fit['P']['intercept'],float);u=np.asarray(fit['U']['U0'],float)
    complete=[];contrasts={};max_target_error=0.
    for d in docs:
        result=run/'results/r0'/(d['id']+'.json')
        if not result.exists():continue
        previous=output/(d['id']+'_result.json')
        if previous.exists():
            old=json.loads(previous.read_text());assert old['identity']==identity and old['document']==d
            max_target_error=max(max_target_error,old['max_target_error'])
            operations.update('suffix_'+d['id']+'_'+arm for arm in ['native','r0_P','r0_U0'])
            complete.append(d['id']);continue
        if d['id'] not in caps or d['donor'] not in caps:continue
        r=caps[d['id']];donor=caps[d['donor']];delta=np.asarray(donor['y'])-r['y'];dx=np.asarray(donor['x'])-r['x']
        p=(dx/fit['P']['scale'])@w+intercept
        preds=dict(native=delta,P=p,U0=p+((delta-p)@u)@u.T);margins={};files=dict(proofs[d['id']]['files']);files.update(proofs[d['donor']]['files'])
        for arm,v in preds.items():
            saved_arm=arm if arm=='native' else 'r0_'+arm;op='suffix_'+d['id']+'_'+saved_arm;cp=receipt(run/'completed'/(op+'.json'));cache=receipt(run/'cache'/(cp['request']+'.json'))
            saved=cache['request']['intervention'];target=np.asarray(r['y'])+v
            assert saved['mode']=='suffix' and saved['arm']==saved_arm and saved['R']==r['R']
            error=float(np.max(np.abs(np.asarray(saved['M'])-target)));max_target_error=max(max_target_error,error)
            assert np.allclose(saved['M'],target,rtol=1e-10,atol=1e-10)
            value=operation(op,d,saved,files);assert np.isfinite(value);margins[arm]=value
        q=receipt(result);assert q['document']==d and q['cohort']=='r0' and set(q['values'])=={'P','U0','zero'}
        truth=margins['native'];assert q['native_h']==truth
        for arm in ['P','U0']:
            v=q['values'][arm];assert v['prediction']==margins[arm] and v['L']==(margins[arm]-truth)**2
            expected=float(np.sum((preds[arm]-delta)**2));assert np.isclose(v['V'],expected,rtol=1e-10,atol=1e-10)
        assert q['values']['zero']==dict(L=float(truth**2),prediction=0.,V=float(np.sum(delta*delta)))
        files[result.relative_to(ROOT).as_posix()]=sha(result)
        evidence=dict(document=d,files=files,identity=identity,own_fit_sha256=sha(fit_path),max_target_error=max_target_error,all_saved_loss_vector_arithmetic_passed=True)
        target=output/(d['id']+'_result.json')
        if target.exists():
            old=json.loads(target.read_text());assert old['files']==files and old['identity']==identity
        else:target.write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
        complete.append(d['id']);contrasts[d['id']]=q['values']['U0']['L']-q['values']['P']['L']
    closure=run/'stage_completed.json';sealed=closure.exists()
    if sealed and len(complete)==len(docs):
        c=receipt(closure);assert c['identity']==identity and c['scope']==phase and len(complete)==len(docs) and len(operations)==4*len(docs)
        for file in output.glob('A_shared_*_*.json'):
            for name,h in json.loads(file.read_text())['files'].items():assert c['files'][str((ROOT/name).relative_to(run)).replace('\\','/')]==h
    summary=dict(phase=phase,documents=len(docs),capture_audited=len(proofs),results_audited=len(complete),unique_operations_audited=len(operations),stage_sealed=sealed,audit_complete=sealed and len(complete)==len(docs),maximum_suffix_target_absolute_error=max_target_error,own_fit_sha256=sha(fit_path),authorship_scope='Reviewer authored shared telemetry helper only, not root genericv3 workflow or Llama numerical/FIT core; independent Astra actual pre-run approval is reused for helper scope.',new_model_fit_bootstrap_MC_calls=0,closed_result_ids=complete)
    (output/'audit_summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in summary.items() if k!='closed_result_ids'}))
    return summary
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--packet',default='analysis/A_short_replication_llama_20261101/PILOT_ready_v1');p.add_argument('--watch',action='store_true');a=p.parse_args()
    started=time.monotonic()
    while True:
        summary=audit(a.packet)
        if not a.watch or summary['audit_complete']:break
        if time.monotonic()-started>14400:raise TimeoutError('Read-only audit watcher reached4h bound; no model action taken')
        time.sleep(60)
