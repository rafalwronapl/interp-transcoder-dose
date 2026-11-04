import time,uuid
import numpy as np
from ab_confirmatory_20261101.runtime import Runtime
from analysis.B_norm_control_20261103.worker import preflight,summarize
from .common import *

def execute(out,docs,controls,cfg,groups,identity,ops,tail,tc,branch):
    runtime=Runtime(out,identity,ops)
    def calc(op,d,settings,fn):
        return runtime.compute(op,d,dict(operation=op,**settings),dict(answer_ids=d.get('answer_ids',[1304,668])),fn)
    # Eight explicit historical FIT controls, no new gradient calculation.
    for k,c in enumerate(controls):
        rec=c['record'];d=c['document'];y=np.asarray(rec['states']['y'],float);g=np.asarray(c['gradient'],float);gn=np.linalg.norm(g);assert gn>0
        h=.25*min(1e-3*max(1.,np.linalg.norm(y)),.01/gn)
        values=[]
        for j,(label,target) in enumerate([('sham',y),('plus',y+h*g/gn),('minus',y-h*g/gn),('parity',y)]):
            op='control_'+str(4*k+j);t=np.asarray(target,np.float32)
            value=float(calc(op,d,dict(target=t.tolist(),kind=label),lambda t=t:tail.margin(rec,t)));values.append(value)
        assert abs(values[0]-rec['states']['margin'])<=1e-4 and abs(values[3]-values[0])<=1e-4
        assert values[1]-values[0]>1e-4 and values[2]-values[0]<-1e-4
        put(out/'controls'/f'{k}.json',dict(values=values,h=h))
    records={}
    for d in docs:
        records[d['id']]=calc(d['id']+'_capture',d,dict(kind='exact_native_capture',ids=d['ids']),lambda d=d:tail.capture(d))
    for frame in sorted({d['frame'] for d in docs}):
        for side in [0,1]:
            d=next(d for d in docs if d['frame']==frame and d['side']==side);rec=records[d['id']];y=np.asarray(rec['states']['y'],np.float32)
            value=float(calc('fresh_parity_'+frame+'_s'+str(side),d,dict(kind='fresh_natural_fullhead_tail_parity',target=y.tolist()),lambda:tail.margin(rec,y)))
            assert abs(value-rec['states']['margin'])<=1e-4,'Fresh readout full-head/tail parity failed'
    items=[]
    for d in docs:
        rec=records[d['id']];other=records[d['donor']];x=np.asarray(rec['states']['x'],np.float32);xe=np.asarray(other['states']['x'],np.float32)
        def enc(op,z):return calc(op,d,dict(kind='TCencoding',input=z.tolist()),lambda:tc.encode(z))
        base=enc(d['id']+'_tcbase',x);end=enc(d['id']+'_tcend',xe)
        # FP32 subtract then add matches historical operator arithmetic.
        delta=np.asarray(end['output'],np.float32)-np.asarray(base['output'],np.float32)
        ref=(np.asarray(rec['states']['y'],np.float32)+delta).astype(np.float32)
        vectors=[group_vector(base['pre'],end['pre'],tc.threshold,tc.decoder,g) for g in groups]
        item=normalize_targets(ref,vectors,cfg['rho'],cfg['eps']);item.update(cell=d['id'],document=d,reference_target=ref.tolist(),native_input=xe.tolist())
        put(out/'targets'/(d['id']+'.json'),item);items.append(item)
    targetfiles={p.relative_to(out).as_posix():sha(p) for p in sorted((out/'targets').glob('*.json'))}
    put(out/'TARGETS_FROZEN.json',dict(files=targetfiles,before_any_scientific_suffix=True,before_any_native_endpoint=True,contexts=len(items),eligible=sum(i['eligible'] for i in items),identity=identity))
    rows=[]
    for item in items:
        d=item['document'];rec=records[d['id']];tag=d['id'];xe=np.asarray(item['native_input'],np.float32)
        native=np.asarray(calc(tag+'_nativebranch',d,dict(kind='native_branch',input=xe.tolist()),lambda:branch(xe)),np.float32)
        known={};measured={}
        scientific=[('NATIVE',native),('FULL',np.asarray(item['reference_target'],np.float32))]
        scientific += list(zip(ARMS,[np.asarray(t['target'],np.float32) for t in item['targets']])) if item['eligible'] else []
        for arm,target in scientific:
            op=tag+'_'+arm;key=target.tobytes()
            if key in known:
                value=known[key];put(out/'aliases'/(op+'.json'),dict(target_sha256=digest(target.tolist()),value=value))
            else:
                value=float(calc(op,d,dict(kind='scientific_suffix',target=target.tolist(),targets_freeze_sha256=sha(out/'TARGETS_FROZEN.json')),lambda target=target:tail.margin(rec,target)));known[key]=value
            measured[arm]=value
        if not item['eligible']:
            for arm in ARMS:put(out/'skips'/(tag+'_'+arm+'.json'),dict(reason='joint_all6_norm_failure',under_eps_groups=item['under_eps_groups']))
        truth=measured['NATIVE'];ref=measured['FULL']
        row=dict(cell=tag,document=d,eligible=item['eligible'],raw_norms=item['raw_norms'],native_margin=truth,reference_margin=ref,reference_loss=(ref-truth)**2)
        if item['eligible']:row.update(margins={a:measured[a] for a in ARMS},effects={a:measured[a]-ref for a in ARMS},loss={a:(measured[a]-truth)**2 for a in ARMS})
        put(out/'results'/(tag+'.json'),row);rows.append(row)
    result={f:summarize([r for r in rows if r['document']['frame']==f]) for f in sorted({d['frame'] for d in docs})}
    result['primary_so_when']=summarize([r for r in rows if r['document']['frame'] in ['so','when']])
    # Prior helper's numerical aggregation is reused; override inherited posthoc label.
    for f,s in result.items():
        s['scope']='Prospectively fixed fresh-name conditional direction diagnostic; readout-specific, no native circuit claim'
        selected=[r for r in rows if r['eligible'] and (r['document']['frame'] in ['so','when'] if f=='primary_so_when' else r['document']['frame']==f)]
        blocks=sorted({r['document']['block'] for r in selected})
        s['group_mean_absolute_effect']={a:float(np.mean([np.mean([abs(r['effects'][a]) for r in selected if r['document']['block']==b]) for b in blocks])) if blocks else None for a in ARMS}
    put(out/'SUMMARY.json',result)
    aliases={p.stem for p in (out/'aliases').glob('*.json')};skips={p.stem for p in (out/'skips').glob('*.json')}
    assert set(runtime.ops)==runtime.attempts|aliases|skips and not(runtime.attempts&aliases or runtime.attempts&skips or aliases&skips)
    return dict(forward_attempts=len(runtime.attempts),backward_attempts=0,aliases=len(aliases),skips=len(skips)),result

def main():
    verify();cfg=read(HERE/'config.json');ident=read(ROOT/cfg['model_identity']);ops=read(HERE/'schedule.json');out=HERE/'run'
    identity=dict(model=digest(ident),code=sha(HERE/'input_manifest.json'))
    if preflight(out,identity,ops):return
    docs=read(HERE/'corpus.json')['documents'];groups=read(ROOT/cfg['groups_source']);groups=[groups['top']]+[g['features'] for g in groups['groups']]
    controls=[]
    for e in read(HERE/'controls.json'):
        cap=source(e['capture']);grad=source(e['gradient']);assert cap['request']['document']['document']==grad['request']['document']['document']
        controls.append(dict(record=cap['result'],document=cap['request']['document']['document'],gradient=grad['result']['gradient']))
    import torch
    from transformers import AutoModelForCausalLM
    from ab_confirmatory_20261101.native_tail_b import ExactTail
    from ab_confirmatory_20261101.transcoder import load
    torch.set_num_threads(cfg['threads']);put(out/'model_load_attempts'/(uuid.uuid4().hex+'.json'),dict(native=ident['B']['folder'],TC=ident['TC']['folder']))
    model,info=AutoModelForCausalLM.from_pretrained(ident['B']['folder'],local_files_only=True,dtype=torch.float32,attn_implementation='eager',low_cpu_mem_usage=True,output_loading_info=True)
    tied=model.get_input_embeddings().weight.data_ptr()==model.get_output_embeddings().weight.data_ptr()
    assert not(set(info.get('missing_keys',[]))-({'lm_head.weight'} if tied else set()) or info.get('mismatched_keys') or info.get('error_msgs'))
    model=model.eval().float();raw=ExactTail(model,15,[1304,668]);rawtc=load(ident['TC']['folder'])
    class Tail:
        def setread(self,ids):raw.native.answers=list(ids)
        def capture(self,d):self.setread(d['answer_ids']);return raw.capture(d['ids'])
        def margin(self,rec,target):self.setread(rec['answer_ids']);return raw.margin(rec,target)
    class TC:
        threshold=rawtc.threshold.numpy().astype(float);decoder=rawtc.wdec.numpy().astype(float)
        def encode(self,z):
            with torch.inference_mode():y,p,m=rawtc.forward(torch.tensor(z,dtype=torch.float32))
            return dict(output=y.tolist(),pre=p.tolist())
    def branch(z):
        with torch.inference_mode():return raw.native.branch(torch.tensor(z,dtype=torch.float32)).tolist()
    try:accounting,result=execute(out,docs,controls,cfg,groups,identity,ops,Tail(),TC(),branch)
    finally:raw.close()
    put(out/'stage_completed.json',dict(files={p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file() and p.name!='stage_completed.json'},accounting=accounting,contexts=len(docs),model_loads=len(list((out/'model_load_attempts').glob('*.json')))))
    print(accounting)
if __name__=='__main__':main()
