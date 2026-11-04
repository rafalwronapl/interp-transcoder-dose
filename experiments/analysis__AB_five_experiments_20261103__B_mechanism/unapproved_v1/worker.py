"""Bounded cache-adopting residual/switch interventions, exact native suffix."""
import argparse, json, math, uuid
from pathlib import Path
import numpy as np
from research_checks.gate import digest
from research_checks.persistence import immutable
from ab_confirmatory_20261101.runtime import Runtime
from analysis.B_mechanism_20261102.common import ROOT,read,sha,unwrap
from analysis.B_mechanism_20261102.worker import source,validate_rounding
from .geometry import residual_target,feature_arms,ARMS

def main(config):
    cfg=read(ROOT/config);out=ROOT/cfg['output'];manifest=read(ROOT/cfg['input_manifest'])['files']
    for name,h in manifest.items():
        if sha(ROOT/name)!=h:raise ValueError('Changed input '+name)
    if (out/'stage_completed.json').exists():
        seal=unwrap(out/'stage_completed.json')
        for name,h in seal['files'].items():
            if sha(out/name)!=h:raise ValueError('Changed output '+name)
        return
    idx=read(ROOT/cfg['source_index']);ops=read(ROOT/cfg['schedule']);ident=read(ROOT/cfg['model_identity'])
    runtime=Runtime(out,dict(model=digest(ident),code=digest(manifest)),ops)
    def adopted(entry):
        assert entry['cache'] in manifest and entry['receipt'] in manifest
        return source(entry)
    captures={k:adopted(v)['result'] for k,v in idx['captures'].items()}
    saved={}
    for c in idx['cells']:
        a=adopted(c['native']);b=adopted(c['tc']);e=adopted(c['tcend']);base=adopted(c['tcbase'])
        for p in [a,b,e,base]:
            assert p['request']['document']['document']==c['document']
            assert p['request']['model_identity']==digest(ident)
            assert p['request']['readout']['answer_ids']==[1304,668]
        assert a['request']['intervention']['method']=='NATIVE' and b['request']['intervention']['method']=='TC'
        saved[c['id']]=dict(n=np.asarray(a['request']['intervention']['target'],np.float32),
            t=np.asarray(b['request']['intervention']['target'],np.float32),truth=float(a['result']),original=float(b['result']),
            edit=np.asarray(e['request']['intervention']['edit'],float),endpoint=np.asarray(e['result'],np.float32),
            base=np.asarray(base['result']['output'],np.float32))
    import torch
    from transformers import AutoModelForCausalLM
    from ab_confirmatory_20261101.native_tail_b import ExactTail
    from ab_confirmatory_20261101.transcoder import load
    torch.set_num_threads(cfg['threads'])
    immutable(out/'model_load_attempts'/f'{uuid.uuid4().hex}.json',dict(native=ident['B']['folder'],TC=ident['TC']['folder']))
    model,info=AutoModelForCausalLM.from_pretrained(ident['B']['folder'],local_files_only=True,dtype=torch.float32,
        attn_implementation='eager',low_cpu_mem_usage=True,output_loading_info=True)
    tied=model.get_input_embeddings().weight.data_ptr()==model.get_output_embeddings().weight.data_ptr()
    if set(info.get('missing_keys',[]))-({'lm_head.weight'} if tied else set()) or info.get('mismatched_keys') or info.get('error_msgs'):raise ValueError('Checkpoint load')
    tail=ExactTail(model.eval().float(),15,[1304,668]);tc=load(ident['TC']['folder'])
    def calc(op,doc,settings,fn,extra=()):
        return runtime.compute(op,doc,settings,dict(answer_ids=[1304,668],orientation='she-minus-he'),fn,extra_operations=extra)
    def encode(op,doc,x):
        def f():
            with torch.inference_mode():y,p,m=tc.forward(torch.tensor(x,dtype=torch.float32))
            return dict(output=y.tolist(),pre=p.tolist())
        return calc(op,doc,dict(kind='TC_encoding',x=np.asarray(x).tolist()),f)
    def decode(h):
        with torch.inference_mode():return (torch.tensor(h,dtype=torch.float32)@tc.wdec+tc.bdec).numpy()
    try:
        for i,item in idx['controls'].items():
            cp=adopted(item['capture']);rec=cp['result'];doc=cp['request']['document']['document'];old=adopted(item['gradient'])['result']
            y=np.asarray(rec['states']['y'],float);g=np.asarray(old['gradient'],float);gn=np.linalg.norm(g)
            tag='control_'+i
            new=calc(tag+'_gradient',doc,dict(target=y.tolist()),lambda:tail.gradient(rec,y),(tag+'_backward',))
            ng=np.asarray(new['gradient']);assert abs(new['margin']-rec['states']['margin'])<=1e-4
            assert gn>0 and np.linalg.norm(ng-g)/gn<=1e-4 and np.max(np.abs(ng-g))<=1e-5
            h=min(1e-3*max(1.,np.linalg.norm(y)),.01/gn);effects={}
            for label,sign in [('plus',1),('minus',-1)]:
                target=(y+sign*h*g/gn).astype(np.float32)
                value=calc(tag+'_'+label,doc,dict(target=target.tolist()),lambda target=target:tail.margin(rec,target))
                effect=value-new['margin'];assert math.isfinite(effect) and abs(effect)>1e-4 and effect*float(g@(target-y))>0
                effects[label]=effect
            immutable(out/'controls'/f'{i}.json',dict(effects=effects,gradient_parity=float(np.linalg.norm(ng-g)/gn)))
        fitcaps={v['document']['id']:adopted(v['capture'])['result'] for v in idx['fit']}
        scores=np.zeros(len(tc.threshold));th=tc.threshold.numpy();dec_norm=np.linalg.norm(tc.wdec.numpy().astype(float),axis=1)
        for v in idx['fit']:
            d=v['document'];i=d['id'];z=np.asarray(fitcaps[i]['x']);end=np.asarray(fitcaps[d['donor']]['x'])
            a=encode('fit_'+i+'_base',d,z);b=encode('fit_'+i+'_end',d,end)
            p=np.asarray(a['pre']);q=np.asarray(b['pre']);scores+=np.abs(np.maximum(q,0)*((q>th).astype(float)-(p>th).astype(float)))*dec_norm
        scores/=len(idx['fit']);top=np.lexsort((np.arange(len(scores)),-scores))[:32]
        random=np.random.default_rng(20261103).choice(np.setdiff1d(np.arange(len(scores)),top),32,replace=False)
        immutable(out/'FEATURE_SELECTION.json',dict(top=top.tolist(),random=random.tolist(),scores=scores.tolist(),source='FIT only, frozen before TEST new evaluation'))
        bases={}
        for d in idx['documents']:
            rec=captures[d['id']];assert rec['layer']==15 and rec['answer_ids']==[1304,668]
            bases[d['id']]=encode('encode_base_'+d['id'],d,rec['states']['x'])
        rows=[]
        for c in idx['cells']:
            tag=c['id'];d=c['document'];rec=captures[d['id']];s=saved[tag];n=s['n'];t=s['t'];y=np.asarray(rec['states']['y'],float)
            z=np.asarray(rec['states']['x'],float);base=bases[d['id']]
            end=encode('encode_end_'+tag,d,z+s['edit'])
            # Same single-vector kernels as accepted TC outputs.
            if not np.array_equal(np.asarray(base['output'],np.float32),s['base']) or not np.array_equal(np.asarray(end['output'],np.float32),s['endpoint']):raise ValueError('TC reencoding parity')
            arms,meta=feature_arms(base['pre'],end['pre'],th,top,random)
            full=np.maximum(np.asarray(end['pre']),0)*(np.asarray(end['pre'])>th)
            full_out=np.asarray(calc('decode_'+tag+'_FULL',d,dict(features=full.tolist()),lambda:decode(full.astype(np.float32)).tolist()),np.float32)
            assert np.array_equal(full_out,s['endpoint'])
            known={n.tobytes():s['truth'],t.tobytes():s['original']};loss={'RR':(s['original']-s['truth'])**2};norms={};rounding={}
            def measure(arm,target):
                op=tag+'_'+arm
                if target is None:
                    immutable(out/'skips'/f'{op}.json',dict(reason='zero partner residual'));return None
                key=target.tobytes()
                if key in known:
                    value=known[key];immutable(out/'aliases'/f'{op}.json',dict(margin=value,target_sha256=digest(target.tolist())))
                else:
                    value=calc(op,d,dict(target=target.tolist(),arm=arm,cell=tag),lambda:tail.margin(rec,target));known[key]=value
                norms[arm]=float(np.linalg.norm(target.astype(float)-n));return (value-s['truth'])**2
            for arm,partner in zip(['partner1','partner7'],c['partners']):
                p=saved[partner];target,details=residual_target(n,t,p['n'],p['t'])
                if target is not None:
                    rv=t.astype(float)-n;pr=p['t'].astype(float)-p['n'];ideal=n.astype(float)+np.linalg.norm(rv)*pr/np.linalg.norm(pr)
                    rounding[arm]=validate_rounding(n.astype(float),ideal,target,float(np.linalg.norm(rv)))
                loss[arm]=measure(arm,target)
            for arm,h in arms.items():
                decoded=np.asarray(calc('decode_'+tag+'_'+arm,d,dict(features=h.tolist()),lambda h=h:decode(h).tolist()),np.float32)
                pred=(decoded-s['base']).astype(np.float32).astype(float);target=(y+pred).astype(np.float32)
                loss[arm]=measure(arm,target)
            row=dict(cell=tag,document=d,operator=c['operator'],dose=c['dose'],loss=loss,norms=norms,rounding=rounding,features=meta)
            immutable(out/'results'/f'{tag}.json',row);rows.append(row)
            tmp=out/'STATUS.tmp';tmp.write_text(json.dumps(dict(cells=len(rows),total=768,attempted=len(runtime.attempts),scheduled=len(ops['operations']))));tmp.replace(out/'STATUS.json')
        groups={}
        for frame in ['so','when','transfer','pooled']:
            for operator in ['full','projected']:
                for dose in [.05,1.]:
                    rr=[r for r in rows if (frame=='pooled' or r['document']['frame']==frame) and r['operator']==operator and r['dose']==dose]
                    groups[f'{frame}/{operator}/{dose}']={a:dict(mean_loss=float(np.mean([r['loss'][a] for r in rr if r['loss'][a] is not None])),defined=sum(r['loss'][a] is not None for r in rr)) for a in ['RR','partner1','partner7',*ARMS]}
        immutable(out/'SUMMARY.json',dict(scope='posthoc fixed32blocks; finite descriptive, no population inference',groups=groups))
        immutable(out/'stage_completed.json',dict(files={p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file() and p.name not in ['stage_completed.json','STATUS.json']},
            attempted={k:sum(runtime.ops[a]==k for a in runtime.attempts) for k in ['forward','backward']},aliases=len(list((out/'aliases').glob('*.json'))),skips=len(list((out/'skips').glob('*.json')))))
    finally:tail.close()
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);main(p.parse_args().config)
