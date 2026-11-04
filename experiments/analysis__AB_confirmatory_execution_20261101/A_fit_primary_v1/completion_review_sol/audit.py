import json, pathlib, hashlib, collections
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[4]
P=ROOT/'analysis/AB_confirmatory_execution_20261101/A_fit_primary_v1'
def read(p): return json.loads(p.read_text())
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
stage=read(P/'run/stage_completed.json')
assert stage['payload_sha256']==digest(stage['payload'])
for n,h in stage['payload']['files'].items(): assert sha(P/'run'/n)==h,n
cfg=read(P/'config.json');docs=read(P/'corpus.json')['documents'];caps={}
for p in (P/'run/cache').glob('*.json'):
    j=read(p);assert j['payload_sha256']==digest(j['payload'])
    req=j['payload']['request']
    if req['intervention']['mode']=='native': caps[req['document']['document']['id']]=j['payload']['result']
for doc,source in cfg['imports'].items():
    r=read(ROOT/source['record'])['payload']['result'];caps[doc]=dict(r['states'],margin=r['margin'])
assert len(caps)==448
ledger=[readline for readline in map(json.loads,(P/'run/ledger.jsonl').read_text().splitlines())]
for j in ledger: assert j['sha256']==digest(j['record'])
records=[j['record'] for j in ledger];attempts=[r for r in records if r['event']=='attempt']
assert len(attempts)==482 and len(set(r['operation'] for r in attempts))==482
assert set(r['operation'] for r in attempts)==set(o['id'] for o in read(P/'operations.json')['operations'])
fit=read(P/'run/FIT_r0.json')['payload']['fit'];pp=fit['P'];w=np.array(pp['w']);intercept=np.array(pp['intercept'])
def matrices(split,frame=None):
    rows=[d for d in docs if d['split']==split and (frame is None or d['frame']==frame)]
    return [np.array([np.array(caps[d['donor']][key])-caps[d['id']][key] for d in rows]) for key in ['x','y']]
x,y=matrices('FIT_MAP');scale=np.sqrt(np.mean(x*x));z=x/scale;a=z-z.mean(0);b=y-y.mean(0)
kkt=np.linalg.norm(a.T@(a@w-b)+len(a)*.01*w)/max(1,np.linalg.norm(a.T@b))
assert kkt<1e-10 and abs(scale-pp['scale'])<1e-14
assert np.max(np.abs(intercept-(y.mean(0)-z.mean(0)@w)))<1e-10
_,du=matrices('FIT_U');target=.05*np.mean(np.sum(du*du,axis=1));assert target==fit['V_target']
checks={}
for name,frame in [('U0',None),('Uctrl','T0'),('U2','T2'),('U5','T5')]:
    d=du if frame is None else np.concatenate([du,matrices('FIT_EXT',frame)[1]])
    u=np.array(fit['U'][name]);_,s,v=np.linalg.svd(d,full_matrices=False)
    orth=float(np.max(np.abs(u.T@u-np.eye(8))))
    # Principal subspace alignment is invariant to signs and repeated singular vectors.
    align=float(np.linalg.norm(u@u.T-v[:8].T@v[:8]))
    assert orth<1e-10 and align<1e-8
    checks[name]={'orthogonality_max':orth,'projector_difference':align,'rank8_singular_value':float(s[7])}
replay=read(P/'actual_cached_replay_v1.json');assert replay['exit_code']==0 and replay['all_bytes_preserved']
for n,h in replay['before'].items(): assert sha(P/n)==h,n
summary={'manifest_files_verified':len(stage['payload']['files']),'captures':len(caps),'new_natural':447,'attempts':len(attempts),'new_full':477,'local_suffix':5,'backward':0,'ledger_events':dict(collections.Counter(r['event'] for r in records)),'ridge_kkt_relative':float(kkt),'V_target':float(target),'basis_checks':checks,'replay_files_verified':len(replay['before']),'model_calls_during_audit':0}
print(json.dumps(summary,indent=2))
(P/'completion_review_sol/offline_checks_v1.json').write_text(json.dumps(summary,indent=2)+'\n')
