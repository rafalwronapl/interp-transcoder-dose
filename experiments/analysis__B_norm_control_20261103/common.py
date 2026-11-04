"""Auditable cache algebra; imports no pretrained runtime."""
import hashlib,json
from pathlib import Path
import numpy as np
from research_checks.persistence import immutable

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def unwrap(p):
    v=read(p)
    if 'payload' in v:
        assert digest(v['payload'])==v['payload_sha256'],'Corrupt envelope '+str(p)
        return v['payload']
    return v
def put(p,x):return immutable(p,x)['payload']
def source(e):
    p=ROOT/e['cache'];v=unwrap(p);receipt=unwrap(ROOT/e['receipt'])
    assert digest(v['request'])==p.stem==receipt['request'],'Cache provenance mismatch'
    return v
def operation(run,op):
    alias=run/'aliases'/(op+'.json')
    if alias.exists():
        a=unwrap(alias);assert a['operation']==op
        return dict(a['adopted']),[alias]
    receipt=run/'completed'/(op+'.json');r=unwrap(receipt);assert r['operation']==op
    return dict(cache=(run/'cache'/(r['request']+'.json')).relative_to(ROOT).as_posix(),receipt=receipt.relative_to(ROOT).as_posix()),[]
def verify_manifest(path):
    for name,h in read(path)['files'].items():assert sha(ROOT/name)==h,'Changed input '+name
def group_vector(pre0,pre1,threshold,decoder,features):
    a=np.asarray(pre0,float)[features];b=np.asarray(pre1,float)[features];t=np.asarray(threshold,float)[features]
    coef=np.maximum(b,0)*((b>t).astype(float)-(a>t).astype(float))
    return coef@np.asarray(decoder,float)[features]
def normalize_targets(reference,vectors,rho,eps):
    ref=np.asarray(reference,np.float32);vv=np.asarray(vectors,float);norm=np.linalg.norm(vv,axis=1)
    assert np.all(np.isfinite(vv)) and rho>0 and eps>0
    eligible=bool(np.all(norm>=eps));out=[]
    if eligible:
        for s,n in zip(vv,norm):
            intended=-rho*s/n;ideal=ref.astype(float)+intended;target=ideal.astype(np.float32)
            actual=target.astype(float)-ref.astype(float);rounding=float(np.linalg.norm(actual-intended))
            bound=float(np.linalg.norm(np.spacing(target).astype(float)))/2+1e-10
            assert rounding<=bound and abs(np.linalg.norm(actual)-rho)<=bound
            assert rho/n<=4+1e-12
            out.append(dict(target=target.tolist(),intended_norm=rho,actual_norm=float(np.linalg.norm(actual)),
                            norm_error=float(np.linalg.norm(actual)-rho),rounding_norm=rounding,rounding_bound=bound,
                            raw_norm=float(n),amplification=float(rho/n),direction_cosine=float(actual@intended/(np.linalg.norm(actual)*rho))))
    return dict(eligible=eligible,raw_norms=norm.tolist(),under_eps_groups=np.flatnonzero(norm<eps).tolist(),targets=out)
