"""Bounded cache-adopting residual/switch interventions, exact native suffix."""
import argparse, json, math, uuid, time
from pathlib import Path
import numpy as np
from research_checks.gate import digest
from research_checks.persistence import immutable
from ab_confirmatory_20261101.runtime import Runtime
from analysis.B_mechanism_20261102.common import ROOT,read,sha,unwrap
from analysis.B_mechanism_20261102.worker import source,validate_rounding
from .geometry import residual_target,feature_arms,ARMS

def publish_status(source,target):
    # Telemetry only: transient Windows readers must not terminate scientific work.
    for attempt in range(20):
        try:source.replace(target);return
        except PermissionError:time.sleep(.05)
    return

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
    w=np.asarray(unwrap(ROOT/cfg['frozen_fit'])['direction'],float)
    assert np.isclose(np.linalg.norm(w),1,rtol=0,atol=1e-8)
    runtime=Runtime(out,dict(model=digest(ident),code=digest(manifest)),ops)
    adoption=read(ROOT/cfg['adoption'])
    def adopted(entry):
        assert entry['cache'] in manifest and entry['receipt'] in manifest
        return source(entry)
    captures={k:adopted(v)['result'] for k,v in idx['captures'].items()}
    documents={d['id']:d for d in idx['documents']}
    for k,v in idx['captures'].items():
        p=adopted(v);q=p['request'];rec=p['result'];tokens=q['document']['tokens']
        assert q['document']['document']==documents[k] and rec['ids']==tokens['ids']
        assert rec['layer']==15 and rec['answer_ids']==[1304,668] and tokens['position']==len(tokens['ids'])-1
    saved={}
    for c in idx['cells']:
        a=adopted(c['native']);b=adopted(c['tc']);e=adopted(c['tcend']);base=adopted(c['tcbase']);fr=adopted(c['frozen'])
        for p in [a,b,e,base,fr]:
            assert p['request']['document']['document']==c['document']
            assert p['request']['model_identity']==digest(ident)
            assert p['request']['readout']['answer_ids']==[1304,668]
        assert a['request']['intervention']['method']=='NATIVE' and b['request']['intervention']['method']=='TC'
        assert fr['request']['intervention']['method']=='FROZEN'
        assert e['request']['intervention']['mode']=='TC_endpoint' and base['request']['intervention']['mode']=='TC_base'
        z=np.asarray(captures[c['document']['id']]['states']['x'],float)
        donor=np.asarray(captures[c['document']['donor']]['states']['x'],float)
        edit=np.asarray(e['request']['intervention']['edit'],float)
        if c['operator']=='full':assert np.array_equal(edit,c['dose']*(donor-z))
        else:
            assert c['operator']=='projected' and c['dose'] in [.05,1.]
            assert np.array_equal(edit,c['dose']*(((donor-z)@w)*w))
        saved[c['id']]=dict(n=np.asarray(a['request']['intervention']['target'],np.float32),
            t=np.asarray(b['request']['intervention']['target'],np.float32),truth=float(a['result']),original=float(b['result']),
            edit=np.asarray(e['request']['intervention']['edit'],float),endpoint=np.asarray(e['result'],np.float32),
            base=np.asarray(base['result']['output'],np.float32),frozen=float(fr['result']))
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
        if op in adoption['operations']:
            item=adoption['operations'][op];old=unwrap(ROOT/item['cache']);q=old['request']
            assert q['document']==doc
            if item.get('qualification'):
                assert q['intervention']['threads']==2 and q['intervention']['input']==settings['x']
            else:
                assert q['intervention']==dict(operation_id=op,**settings)
                assert q['model_identity']==digest(ident)
            for key in [op,*extra]:
                immutable(out/'aliases'/f'{key}.json',dict(adopted=item,operation=key))
            return old['result']
        return runtime.compute(op,doc,dict(operation_id=op,**settings),dict(answer_ids=[1304,668],orientation='she-minus-he'),fn,extra_operations=extra)
    def encode(op,doc,x):
        def f():
            torch.set_num_threads(cfg['tc_threads'])
            try:
                with torch.inference_mode():y,p,m=tc.forward(torch.tensor(x,dtype=torch.float32))
            finally:torch.set_num_threads(cfg['threads'])
            return dict(output=y.tolist(),pre=p.tolist())
        return calc(op,doc,dict(kind='TC_encoding',x=np.asarray(x).tolist()),f)
    def decode(h):
        torch.set_num_threads(cfg['tc_threads'])
        try:
            with torch.inference_mode():return (torch.tensor(h,dtype=torch.float32)@tc.wdec+tc.bdec).numpy()
        finally:torch.set_num_threads(cfg['threads'])
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
        assert unwrap(ROOT/adoption['feature_selection'])['top']==top.tolist()
        assert unwrap(ROOT/adoption['feature_selection'])['random']==random.tolist()
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
            p0=np.asarray(base['pre']);h0=(np.maximum(p0,0)*(p0>th)).astype(np.float32)
            decoded_known={h0.tobytes():s['base'],full.astype(np.float32).tobytes():full_out}
            known={n.tobytes():s['truth'],t.tobytes():s['original']};loss={'RR':(s['original']-s['truth'])**2,'FROZEN':(s['frozen']-s['truth'])**2};norms={};rounding={}
            margins={'RR':s['original'],'FROZEN':s['frozen']};signed={k:v-s['truth'] for k,v in margins.items()};deltas={}
            def measure(arm,target):
                op=tag+'_'+arm
                if target is None:
                    immutable(out/'skips'/f'{op}.json',dict(reason='zero partner residual'));return None
                key=target.tobytes()
                if key in known:
                    value=known[key];immutable(out/'aliases'/f'{op}.json',dict(margin=value,target_sha256=digest(target.tolist())))
                else:
                    value=calc(op,d,dict(target=target.tolist(),arm=arm,cell=tag),lambda:tail.margin(rec,target));known[key]=value
                norms[arm]=float(np.linalg.norm(target.astype(float)-n));margins[arm]=value;signed[arm]=value-s['truth'];deltas[arm]=target.astype(float)-n
                return (value-s['truth'])**2
            for arm,partner in zip(['partner1','partner7'],c['partners']):
                p=saved[partner];target,details=residual_target(n,t,p['n'],p['t'])
                if target is not None:
                    rv=t.astype(float)-n;pr=p['t'].astype(float)-p['n'];ideal=n.astype(float)+np.linalg.norm(rv)*pr/np.linalg.norm(pr)
                    rounding[arm]=validate_rounding(n.astype(float),ideal,target,float(np.linalg.norm(rv)))
                loss[arm]=measure(arm,target)
            for arm,h in arms.items():
                dop='decode_'+tag+'_'+arm;key=h.tobytes()
                if key in decoded_known:
                    decoded=decoded_known[key]
                    immutable(out/'aliases'/f'{dop}.json',dict(reason='Exact feature vector same decoder',features_sha256=digest(h.tolist()),output=decoded.tolist()))
                else:
                    decoded=np.asarray(calc(dop,d,dict(features=h.tolist()),lambda h=h:decode(h).tolist()),np.float32)
                    decoded_known[key]=decoded
                pred=(decoded-s['base']).astype(np.float32).astype(float);target=(y+pred).astype(np.float32)
                loss[arm]=measure(arm,target)
            interactions={k:signed['RR']-signed['ONLY_'+k]-signed['EXCEPT_'+k]+signed['BASE'] for k in ['top','random']}
            interactions['ON_OFF']=signed['RR']-signed['ON']-signed['OFF']+signed['BASE']
            row=dict(cell=tag,document=d,operator=c['operator'],dose=c['dose'],loss=loss,norms=norms,rounding=rounding,features=meta,
                native_margin=s['truth'],margins=margins,signed_errors=signed,finite_interactions=interactions,
                base_minus_frozen=signed['BASE']-signed['FROZEN'],
                group_vector_norms={a:float(np.linalg.norm(v-deltas['BASE'])) for a,v in deltas.items() if a in ARMS})
            immutable(out/'results'/f'{tag}.json',row);rows.append(row)
            tmp=out/'STATUS.tmp';tmp.write_text(json.dumps(dict(cells=len(rows),total=768,attempted=len(runtime.attempts),scheduled=len(ops['operations']))));publish_status(tmp,out/'STATUS.json')
        groups={}
        for frame in ['so','when','transfer','pooled']:
            for operator in ['full','projected']:
                for dose in [.05,1.]:
                    rr=[r for r in rows if (frame=='pooled' or r['document']['frame']==frame) and r['operator']==operator and r['dose']==dose]
                    groups[f'{frame}/{operator}/{dose}']={a:dict(mean_loss=float(np.mean([r['loss'][a] for r in rr if r['loss'][a] is not None])) if any(r['loss'][a] is not None for r in rr) else None,
                        mean_signed_error=float(np.mean([r['signed_errors'][a] for r in rr if r['loss'][a] is not None])) if any(r['loss'][a] is not None for r in rr) else None,
                        defined=sum(r['loss'][a] is not None for r in rr)) for a in ['RR','FROZEN','partner1','partner7',*ARMS]}
        immutable(out/'SUMMARY.json',dict(scope='posthoc fixed32blocks; finite descriptive, no population inference',groups=groups))
        aliases={p.stem for p in (out/'aliases').glob('*.json')};skips={p.stem for p in (out/'skips').glob('*.json')}
        assert not (runtime.attempts&aliases or runtime.attempts&skips or aliases&skips)
        assert set(runtime.ops)==runtime.attempts|aliases|skips
        immutable(out/'stage_completed.json',dict(files={p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file() and p.name not in ['stage_completed.json','STATUS.json']},
            attempted={k:sum(runtime.ops[a]==k for a in runtime.attempts) for k in ['forward','backward']},aliases=len(list((out/'aliases').glob('*.json'))),skips=len(list((out/'skips').glob('*.json')))))
    finally:tail.close()
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);main(p.parse_args().config)
