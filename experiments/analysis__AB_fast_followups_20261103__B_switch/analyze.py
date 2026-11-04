"""FIT-cache-only switch matching. No native/TC model classes or evaluations."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OLD=ROOT/'analysis/AB_five_experiments_20261103/B_mechanism'
SEEDS=[20261103,20261104,20261105,20261106,20261107]

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def digest(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))

def unwrap(p):
    v=read(p)
    if 'payload' in v:
        assert digest(v['payload'])==v['payload_sha256'],str(p)
        return v['payload']
    return v

def save(p,x):
    data=(json.dumps(x,indent=2,allow_nan=False)+'\n').encode()
    if p.exists():
        assert p.read_bytes()==data,'Refuse changed output '+str(p)
    else:p.write_bytes(data)

def terms(p,q,threshold):
    switch=(p>threshold)!=(q>threshold)
    coef=np.maximum(q,0)*((q>threshold).astype(float)-(p>threshold).astype(float))
    return switch,coef

def distributions(count,norm):
    return dict(count=count.tolist(),norm=norm.tolist(),mean_count=float(np.mean(count)),mean_norm=float(np.mean(norm)),
                count_quantiles=np.quantile(count,[0,.1,.25,.5,.75,.9,1]).tolist(),norm_quantiles=np.quantile(norm,[0,.1,.25,.5,.75,.9,1]).tolist())

def distances(c,n,tc,tn):
    return np.array([np.mean(np.abs(np.sort(c)-np.sort(tc))),np.mean(np.abs(np.sort(n)-np.sort(tn)))])

def match(switch,coef,dec,top,blocks,seeds=SEEDS,proposals=256):
    tc=switch[:,top].sum(1);tv=coef[:,top]@dec[top];tn=np.linalg.norm(tv,axis=1)
    # FIT heterogeneity tolerance, not an inferential equivalence margin:
    # 95th percentile balanced block-split Wasserstein distances (128 splits).
    unique=np.unique(blocks);assert len(unique)%2==0
    rng=np.random.default_rng(20261102);null=[]
    for _ in range(128):
        keep=np.isin(blocks,rng.permutation(unique)[:len(unique)//2]);null.append(distances(tc[keep],tn[keep],tc[~keep],tn[~keep]))
    tol=np.quantile(null,.95,axis=0);scale=np.maximum(tol,[1e-12,1e-12])
    available=np.setdiff1d(np.arange(dec.shape[0]),top)
    active=available[np.any(switch[:,available],axis=0)]
    inactive=available[~np.any(switch[:,available],axis=0)]
    pool=np.concatenate([active,inactive[:32]])
    groups=[]
    for seed in seeds:
        rng=np.random.default_rng(seed)
        # Start from strongest alternative individual contributions; random tie jitter
        # makes fixed seeds meaningful without consulting any readout.
        strength=np.mean(np.abs(coef[:,pool]),axis=0)*np.linalg.norm(dec[pool],axis=1)
        order=np.lexsort((rng.random(len(pool)),-strength));g=pool[order[:32]].copy()
        assert len(g)==32
        c=switch[:,g].sum(1);v=coef[:,g]@dec[g];n=np.linalg.norm(v,axis=1)
        objective=float(np.sum(distances(c,n,tc,tn)/scale))
        for _ in range(proposals):
            slot=int(rng.integers(32));new=int(rng.choice(pool))
            if new in g:continue
            old=int(g[slot]);cc=c-switch[:,old]+switch[:,new]
            vv=v-coef[:,old,None]*dec[old]+coef[:,new,None]*dec[new];nn=np.linalg.norm(vv,axis=1)
            obj=float(np.sum(distances(cc,nn,tc,tn)/scale))
            if obj<objective-1e-12:
                g[slot]=new;c=cc;v=vv;n=nn;objective=obj
        dist=distances(c,n,tc,tn)
        groups.append(dict(seed=seed,features=sorted(g.tolist()),objective=objective,W1_count_norm=dist.tolist(),
                           within_FIT_heterogeneity_tolerance=bool(np.all(dist<=tol)),distribution=distributions(c,n)))
    # Absolute count envelope: even ALL non-top features cannot exceed this.
    maxcount=switch[:,available].sum(1)
    return dict(top_distribution=distributions(tc,tn),tolerance_count_norm=tol.tolist(),tolerance_definition='95th percentile of 128 fixed-seed balanced whole-block splits of top32 FIT distributions; descriptive only',
                alternative_switching_features=active.tolist(),all_alternatives_count=maxcount.tolist(),
                contexts_top_count_exceeds_all_alternatives=int(np.sum(tc>maxcount)),
                mean_top_count=float(np.mean(tc)),mean_all_alternatives_count=float(np.mean(maxcount)),
                count_mean_deficit_lower_bound=float(max(0,np.mean(tc)-np.mean(maxcount))),groups=groups)

def validate_pair(entry,doc,op):
    p=ROOT/entry['cache'];v=unwrap(p);r=unwrap(ROOT/entry['receipt']);q=v['request']
    assert digest(q)==p.stem==r['request'] and r['operation']==op
    assert q['document']==doc and doc['split']=='FIT'
    assert q['intervention']['operation_id']==op and q['intervention']['kind']=='TC_encoding'
    return v

def run():
    manifest=read(HERE/'input_manifest.json')['files']
    for name,h in manifest.items():assert sha(ROOT/name)==h,'Changed input '+name
    idx=read(OLD/'source_index.json');adopt=read(OLD/'adoption_v3.json')
    ident=read(ROOT/'analysis/AB_confirmatory_execution_20261101/B_fit_primary_v1/model_identity.json')
    top=unwrap(OLD/'run_v3/FEATURE_SELECTION.json')['top'];historic=unwrap(ROOT/adopt['feature_selection'])
    assert historic['top']==top and len(top)==len(set(top))==32
    rows=[];p=[];q=[];captures={}
    for item in idx['fit']:
        doc=item['document'];cp=ROOT/item['capture']['cache'];cap=unwrap(cp)
        receipt=unwrap(ROOT/item['capture']['receipt'])
        assert digest(cap['request'])==cp.stem==receipt['request']
        assert receipt['operation']=='capture_'+doc['id'] and doc['split']=='FIT'
        captures[doc['id']]=cap['result']['x']
    for item in idx['fit']:
        doc=item['document'];op='fit_'+doc['id']
        a=validate_pair(adopt['operations'][op+'_base'],doc,op+'_base')
        b=validate_pair(adopt['operations'][op+'_end'],doc,op+'_end')
        assert a['request']['model_identity']==b['request']['model_identity']==digest(ident)
        assert a['request']['intervention']['x']==captures[doc['id']]
        assert b['request']['intervention']['x']==captures[doc['donor']]
        p.append(a['result']['pre']);q.append(b['result']['pre']);rows.append(doc)
    # Selective access to already stored numeric arrays, never model loading.
    from safetensors import safe_open
    with safe_open(str(Path(ident['TC']['folder'])/'params.safetensors'),framework='np') as f:
        threshold=f.get_tensor('threshold').astype(float);dec=f.get_tensor('w_dec').astype(float)
    switch,coef=terms(np.asarray(p),np.asarray(q),threshold)
    scores=np.mean(np.abs(coef),axis=0)*np.linalg.norm(dec,axis=1)
    expected=np.lexsort((np.arange(len(scores)),-scores))[:32].tolist()
    assert expected==top,'Historical top32 ranking differs'
    assert np.allclose(scores,historic['scores'],rtol=1e-12,atol=1e-12)
    result=match(switch,coef,dec,top,np.array([r['block'] for r in rows]))
    result.update(schema_version=1,scope='Historical FIT only, full operator dose1, so frame, 64 blocks/128 documents; no TEST readouts',
                  documents=rows,top=top,seeds=SEEDS,native_loads=0,TC_model_loads=0,native_forwards=0,TC_forwards=0,
                  tensor_keys_accessed=['threshold','w_dec'],input_manifest_sha256=sha(HERE/'input_manifest.json'),
                  missing_conditions=['full dose .05 FIT endpoints','projected dose .05 and1 FIT endpoints','when and transfer FIT frames'],
                  warning='No causal/readout conclusion. Controls are candidates only and only valid within observed FIT scope; count/norm tolerance does not guarantee TEST balance.')
    save(HERE/'FIT_FEASIBILITY.json',result)
    save(HERE/'FROZEN_GROUPS.json',dict(top=top,groups=[dict(seed=g['seed'],features=g['features']) for g in result['groups']],
                                         condition=dict(operator='full',dose=1,frame='so'),status='FIT candidates; B-MASK not launched',input_manifest_sha256=sha(HERE/'input_manifest.json')))
    print(json.dumps({k:result[k] for k in ['alternative_switching_features','contexts_top_count_exceeds_all_alternatives','mean_top_count','mean_all_alternatives_count','tolerance_count_norm']}))

def fixtures():
    s,c=terms(np.array([[2.,0.,2.,-2.],[0.,2.,3.,-3.]]),np.array([[.5,2.,3.,-3.],[2.,.5,1.,-2.]]),np.ones(4))
    assert s.tolist()==[[True,True,False,False],[True,True,True,False]]
    assert c[0].tolist()==[-.5,2.,0.,0.] and c[1].tolist()==[2.,-.5,-1.,0.]
    dec=np.array([[2.,0.],[0.,1.],[-1.,0.],[3.,2.]])
    assert np.array_equal(c[0]@dec,[-1.,2.])
    assert np.linalg.norm((c[0,:2]@dec[:2]))!=np.sum(np.abs(c[0,:2])*np.linalg.norm(dec[:2],axis=1))
    assert np.array_equal(distances([0,2],[1,3],[2,0],[3,1]),[0,0])
    # Sufficient pool with zero/nonzero alternatives, reproducible bounded optimizer.
    rng=np.random.default_rng(1);ss=rng.random((8,72))>.5;cc=ss*rng.normal(size=ss.shape);dd=rng.normal(size=(72,3))
    args=(ss,cc,dd,list(range(32)),np.repeat(np.arange(4),2))
    a=match(*args,seeds=[1],proposals=4);b=match(*args,seeds=[1],proposals=4)
    assert a==b and len(a['groups'][0]['features'])==32 and not set(a['groups'][0]['features'])&set(range(32))
    save(HERE/'fixtures.json',dict(passed=True,checks=['ON/OFF incl positive subthreshold and negative ReLU','sum-vector norm not sum row norms','distribution distance permutation invariant','fixed-seed matching reproducible/disjoint32'],native_loads=0,TC_model_loads=0,pretrained_forwards=0))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--fixtures',action='store_true');a=p.parse_args()
    fixtures() if a.fixtures else run()
