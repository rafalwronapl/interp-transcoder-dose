"""Exact native suffixes at previously frozen norm-control targets."""
import json,math,time,uuid
from pathlib import Path
import numpy as np
from ab_confirmatory_20261101.runtime import Runtime
from .common import HERE,ROOT,read,sha,digest,unwrap,put,source,verify_manifest

ARMS=['top32']+['control_'+str(s) for s in range(20261103,20261108)]

def preflight(out,identity,ops):
    runtime=Runtime(out,identity,ops)  # identity/schedule checked before completion or loading
    for record in runtime.records:
        if record['event']!='attempt':continue
        assert record['operation'] in runtime.ops,'Attempt outside frozen schedule'
        p=out/'cache'/(record['request']+'.json')
        if not p.exists():raise ValueError('Uncertain reserved attempt; refuse native load')
        cached=unwrap(p);q=cached['request']
        assert digest(q)==record['request'] and q['model_identity']==identity['model'] and q['code_identity']==identity['code'],'Attempt cache identity mismatch'
    completed=out/'stage_completed.json'
    if completed.exists():
        for name,h in unwrap(completed)['files'].items():assert sha(out/name)==h,'Completed output changed'
        return True
    return False

def guarded_load(out,identity,ops,loader):
    if preflight(out,identity,ops):return None
    return loader()

def summarize(rows):
    eligible=[r for r in rows if r['eligible']];blocks=sorted({r['document']['block'] for r in rows})
    blockrows=[]
    for b in blocks:
        rr=[r for r in eligible if r['document']['block']==b]
        if not rr:continue
        increments={a:float(np.mean([r['loss'][a]-r['reference_loss'] for r in rr])) for a in ARMS}
        effects={a:float(np.mean([r['effects'][a] for r in rr])) for a in ARMS}
        blockrows.append(dict(block=b,eligible_contexts=len(rr),increments=increments,effects=effects,
                              top_minus_mean_controls=float(increments['top32']-np.mean([increments[a] for a in ARMS[1:]]))))
    contrasts=[r['top_minus_mean_controls'] for r in blockrows]
    return dict(contexts=len(rows),eligible_contexts=len(eligible),excluded_contexts=len(rows)-len(eligible),blocks=len(blocks),eligible_blocks=len(blockrows),
        primary='Mean across blocks of top32 squared-error increment minus equally averaged five-control increments; within block eligible contexts equally weighted.',
        primary_top_minus_controls=float(np.mean(contrasts)) if contrasts else None,block_contrasts=contrasts,block_results=blockrows,
        group_mean_increment={a:float(np.mean([r['increments'][a] for r in blockrows])) if blockrows else None for a in ARMS},
        group_mean_signed_effect={a:float(np.mean([r['effects'][a] for r in blockrows])) if blockrows else None for a in ARMS},
        scope='Posthoc norm-rescaled TC mask-direction diagnostic on eligible historical contexts; not equal native switching or circuit evidence')

def execute(out,items,controls,tail,identity,ops,parity_items):
    out.mkdir(parents=True,exist_ok=True);runtime=Runtime(out,identity,ops)
    def calc(op,doc,target,kind):
        return runtime.compute(op,doc,dict(kind=kind,target=np.asarray(target,np.float32).tolist()),
            dict(answer_ids=[1304,668],orientation='she-minus-he'),lambda:tail.margin(doc['record'],np.asarray(target,np.float32)))
    # The record is included in complete cache request identity via doc, rather
    # than relying on a mutable external prefix reference.
    for number,c in enumerate(controls):
        rec=c['record'];doc=dict(document=c['document'],record=rec);y=np.asarray(rec['states']['y'],float)
        value=float(calc('control_'+str(number)+'_sham',doc,y,'native_same_value'))
        assert abs(value-rec['states']['margin'])<=1e-4,'Native sham parity'
        g=np.asarray(c['gradient'],float);gn=np.linalg.norm(g);assert gn>0
        h=.5*min(1e-3*max(1.,np.linalg.norm(y)),.01/gn)
        effects={}
        for label,sign in [('plus',1),('minus',-1)]:
            target=(y+sign*h*g/gn).astype(np.float32)
            measured=float(calc('control_'+str(number)+'_'+label,doc,target,'new_half_historical_signed_probe'))
            effect=measured-value;expected=float(g@(target.astype(float)-y))
            assert math.isfinite(effect) and abs(effect)>1e-4 and effect*expected>0,'Nonzero signed sensitivity'
            effects[label]=effect
        put(out/'controls'/('control_'+str(number)+'.json'),dict(native_sham_error=value-rec['states']['margin'],effects=effects,h=h))
    for number,item in enumerate(parity_items):
        doc=dict(document=item['document'],record=item['record'])
        value=float(calc('reference_parity_'+str(number),doc,item['reference_target'],'TC_FULL_sham'))
        assert abs(value-item['reference_margin'])<=1e-4,'TC_FULL reference parity'
        put(out/'controls'/('reference_'+str(number)+'.json'),dict(error=value-item['reference_margin']))
    rows=[]
    for item in items:
        doc=item['document'];row=dict(cell=item['cell'],document=doc,eligible=item['eligible'],raw_norms=item['raw_norms'],under_eps_groups=item['under_eps_groups'])
        if not item['eligible']:
            for arm in ARMS:put(out/'skips'/(item['cell']+'_'+arm+'.json'),dict(reason='Joint ALL6 direction norm eligibility failed',under_eps_groups=item['under_eps_groups']))
        else:
            truth=item['native_margin'];ref=item['reference_margin'];known={np.asarray(item['reference_target'],np.float32).tobytes():ref}
            margins={};effects={};loss={}
            for arm,target in zip(ARMS,item['targets']):
                op=item['cell']+'_'+arm;t=np.asarray(target['target'],np.float32);key=t.tobytes()
                if key in known:
                    value=known[key];put(out/'aliases'/(op+'.json'),dict(reason='Byte-identical frozen target in same exact prefix',margin=value,target_sha256=digest(t.tolist())))
                else:
                    value=float(calc(op,dict(document=doc,record=item['record']),t,'frozen_norm_control_'+arm));known[key]=value
                assert math.isfinite(value);margins[arm]=value;effects[arm]=value-ref;loss[arm]=(value-truth)**2
            row.update(native_margin=truth,reference_margin=ref,reference_loss=(ref-truth)**2,margins=margins,effects=effects,loss=loss,
                       target_norms=[t['actual_norm'] for t in item['targets']],amplification=[t['amplification'] for t in item['targets']])
        put(out/'results'/(item['cell']+'.json'),row);rows.append(row)
    summary=summarize(rows);summary['per_frame']={f:summarize([r for r in rows if r['document']['frame']==f]) for f in sorted({r['document']['frame'] for r in rows})}
    put(out/'SUMMARY.json',summary)
    aliases={p.stem for p in (out/'aliases').glob('*.json')};skips={p.stem for p in (out/'skips').glob('*.json')}
    assert not(runtime.attempts&aliases or runtime.attempts&skips or aliases&skips)
    assert set(runtime.ops)==runtime.attempts|aliases|skips
    assert sum(runtime.ops[a]=='forward' for a in runtime.attempts)<=776
    return dict(forward_attempts=sum(runtime.ops[a]=='forward' for a in runtime.attempts),backward_attempts=0,aliases=len(aliases),skips=len(skips)),summary

def main():
    verify_manifest(HERE/'stage2_input_manifest.json');cfg=read(HERE/'config.json');out=ROOT/cfg['output']
    ident=read(ROOT/cfg['model_identity']);identity=dict(model=digest(ident),code=sha(HERE/'stage2_input_manifest.json'));ops=read(HERE/'stage2_schedule.json')
    if preflight(out,identity,ops):return
    seal=unwrap(HERE/'TARGETS_FROZEN.json')
    for name,h in seal['files'].items():assert sha(HERE/name)==h,'Frozen target changed'
    idx=unwrap(HERE/'stage2_index.json');items=[]
    for entry in idx['items']:
        item=unwrap(HERE/entry['target']);cap=source(entry['capture']);tc=source(entry['tc']);native=source(entry['native'])
        assert cap['request']['document']['document']==tc['request']['document']['document']==native['request']['document']['document']==item['document']
        assert tc['request']['intervention']['method']=='TC' and native['request']['intervention']['method']=='NATIVE'
        assert np.array_equal(np.asarray(item['reference_target'],np.float32),np.asarray(tc['request']['intervention']['target'],np.float32))
        item.update(record=cap['result'],reference_margin=float(tc['result']),native_margin=float(native['result']));items.append(item)
    controls=[]
    for e in idx['controls']:
        cap=source(e['capture']);gradient=source(e['gradient']);assert cap['request']['document']['document']==gradient['request']['document']['document']
        controls.append(dict(record=cap['result'],document=cap['request']['document']['document'],gradient=gradient['result']['gradient']))
    parity_items=[next(i for i in items if i['cell']==name) for name in idx['reference_parity_cells']]
    def load_native():
        import torch
        from transformers import AutoModelForCausalLM
        from ab_confirmatory_20261101.native_tail_b import ExactTail
        torch.set_num_threads(cfg['threads']);put(out/'model_load_attempts'/(uuid.uuid4().hex+'.json'),dict(folder=ident['B']['folder']))
        model,info=AutoModelForCausalLM.from_pretrained(ident['B']['folder'],local_files_only=True,dtype=torch.float32,attn_implementation='eager',low_cpu_mem_usage=True,output_loading_info=True)
        tied=model.get_input_embeddings().weight.data_ptr()==model.get_output_embeddings().weight.data_ptr()
        if set(info.get('missing_keys',[]))-({'lm_head.weight'} if tied else set()) or info.get('mismatched_keys') or info.get('error_msgs'):raise ValueError('Checkpoint load mismatch')
        return ExactTail(model.eval().float(),15,[1304,668])
    tail=guarded_load(out,identity,ops,load_native)
    if tail is None:return
    try:accounting,summary=execute(out,items,controls,tail,identity,ops,parity_items)
    finally:tail.close()
    put(out/'stage_completed.json',dict(files={p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file() and p.name!='stage_completed.json'},accounting=accounting,
        targets_freeze_sha256=sha(HERE/'TARGETS_FROZEN.json'),native_loads=len(list((out/'model_load_attempts').glob('*.json'))),TC_loads=0,TC_forwards=0,new_prefix_forwards=0,contexts=summary['contexts'],eligible=summary['eligible_contexts']))
    print(accounting)
if __name__=='__main__':main()
