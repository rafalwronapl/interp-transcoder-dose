"""B exact-tail qualification and prospective PILOT/TEST acquisition.

New module: never changes frozen FIT worker or refits learned parameters.
Model calls require an independent contract and canonical launcher.
"""
import argparse,json,time
from pathlib import Path
import numpy as np
from research_checks.gate import digest
from research_checks.persistence import immutable
from .prepare import ROOT,sha
from .runtime import Runtime
from .baselines_b import predict

DEPENDENCIES=['__init__.py','worker_b_evaluate.py','native_tail_b.py','native.py','runtime.py','prepare.py','baselines_b.py','transcoder.py']
METHODS=['TC','FROZEN','TAYLOR','MEAN','RIDGE']

def schedule(cfg,docs):
    ops=[]
    def add(name,kind='forward'):ops.append(dict(id=name,kind=kind))
    technical=cfg['phase']=='TAIL_QUALIFICATION'
    for d in docs:
        i=d['id'];add('capture_'+i);add('tail_gradient_'+i);add('tail_backward_'+i,'backward');add('tc_base_'+i)
        if technical:add('full_gradient_'+i);add('full_backward_'+i,'backward')
        for operator in ['full','projected']:
            add(f'jvp_{i}_{operator}')
            if not technical:add(f'frozen_{i}_{operator}')
            for ci,_ in enumerate(cfg['doses']):
                tag=f'{i}_{operator}_{ci}';add('native_endpoint_'+tag);add('tc_endpoint_'+tag)
                for method in ['NATIVE']+(['TC','TAYLOR'] if technical else METHODS):
                    add(f'tail_{tag}_{method}')
                    if technical:add(f'full_{tag}_{method}')
    return dict(operations=ops)

def unwrap(path):
    obj=json.loads(Path(path).read_text(encoding='utf-8'))
    if obj['payload_sha256']!=digest(obj['payload']):raise ValueError('corrupt immutable '+str(path))
    return obj['payload']

def main(config_path):
    cfg=json.loads((ROOT/config_path).read_text(encoding='utf-8'))
    if cfg['phase'] not in ('TAIL_QUALIFICATION','PILOT','TEST'):raise ValueError('invalid evaluation phase')
    technical=cfg['phase']=='TAIL_QUALIFICATION'
    if sha(ROOT/cfg['frozen_fit'])!=cfg['frozen_fit_sha256']:raise ValueError('FIT changed')
    fit=unwrap(ROOT/cfg['frozen_fit'])
    docs=json.loads((ROOT/cfg['corpus']).read_text())['documents'];tokens=json.loads((ROOT/cfg['tokens']).read_text())
    if len({d['id'] for d in docs})!=len(docs):raise ValueError('duplicate evaluation document')
    ids={d['id'] for d in docs}
    for d in docs:
        if d['study']!='B' or d['donor'] not in ids:raise ValueError('missing B donor')
        expected='FIT' if technical else cfg['phase']
        if d['split']!=expected or (technical and d['frame']!='transfer'):raise ValueError('split scope violation')
    if not technical:
        if cfg['doses']!=[.05,.1,.25,.5,1.,2.]:raise ValueError('changed dose grid')
        proof=unwrap(ROOT/cfg['tail_qualification'])
        if not proof['passed'] or sha(ROOT/cfg['tail_qualification'])!=cfg['tail_qualification_sha256']:raise ValueError('unqualified tail')
        if not cfg.get('statistical_preparation_approved'):raise ValueError('PILOT/TEST statistics not frozen')
        # The reviewed contract must bind the actual statistical approval, not
        # treat this configBoolean alone as sufficient evidence.
    ident=json.loads((ROOT/cfg['model_identity']).read_text())
    for item in ident.values():
        for name,meta in item['files'].items():
            if sha(name)!=meta['sha256']:raise ValueError('model bytes changed')
    if fit['identity']['model']!=digest(ident):raise ValueError('FIT/model identity mismatch')
    ops=json.loads((ROOT/cfg['schedule']).read_text())
    if ops!=schedule(cfg,docs):raise ValueError('schedule not exact')
    sources={f'ab_confirmatory_20261101/{n}':sha(ROOT/'ab_confirmatory_20261101'/n) for n in DEPENDENCIES}
    identity=dict(model=digest(ident),code=digest(dict(sources=sources,config_sha256=sha(ROOT/config_path))),
        corpus=sha(ROOT/cfg['corpus']),tokens=sha(ROOT/cfg['tokens']),fit=cfg['frozen_fit_sha256'])
    out=ROOT/cfg['output'];runtime=Runtime(out,identity,ops);complete=out/'stage_completed.json'
    if complete.exists():
        previous=unwrap(complete)
        for name,h in previous['files'].items():
            if sha(out/name)!=h:raise ValueError('completed evidence changed')
        return
    import torch
    from transformers import AutoModelForCausalLM
    from .native_tail_b import ExactTail
    from .transcoder import load
    torch.set_num_threads(cfg['threads'])
    model,info=AutoModelForCausalLM.from_pretrained(ident['B']['folder'],local_files_only=True,dtype=torch.float32,
        attn_implementation='eager',low_cpu_mem_usage=True,output_loading_info=True)
    tied=model.get_input_embeddings().weight.data_ptr()==model.get_output_embeddings().weight.data_ptr()
    if set(info.get('missing_keys',[]))-({'lm_head.weight'} if tied else set()) or info.get('mismatched_keys') or info.get('error_msgs'):
        raise ValueError('incomplete model')
    tail=ExactTail(model.eval().float(),cfg['layer'],cfg['answer_ids']);tc=load(ident['TC']['folder'])
    w=np.asarray(fit['direction'],np.float64)
    if not np.isclose(np.linalg.norm(w),1,atol=1e-8,rtol=0):raise ValueError('invalid frozen direction')
    caps={};qualification=[];started=time.monotonic()
    def compute(op,d,settings,function,extra=()):
        return runtime.compute(op,dict(document=d,tokens=tokens[d['id']]),settings,
            dict(answer_ids=cfg['answer_ids'],orientation='she-minus-he'),function,extra_operations=extra)
    def status(stage):
        temp=out/'STATUS.tmp';temp.write_text(json.dumps(dict(stage=stage,captures=len(caps),total_captures=len(docs),
            completed_operations=len(list((out/'completed').glob('*.json'))),scheduled_operations=len(ops['operations']),elapsed_seconds=time.monotonic()-started)))
        temp.replace(out/'STATUS.json')
    try:
        for d in docs:
            caps[d['id']]=compute('capture_'+d['id'],d,dict(mode='natural_with_exact_boundary'),lambda d=d:tail.capture(tokens[d['id']]['ids']))
            status('capture')
        for d in docs:
            i=d['id'];record=caps[i];r=record['states'];donor=caps[d['donor']]['states']
            z=np.asarray(r['x']);y=np.asarray(r['y']);delta=np.asarray(donor['x'])-z
            gradient=compute('tail_gradient_'+i,d,dict(mode='tail_gradient',output=y.tolist()),lambda:tail.gradient(record,y),('tail_backward_'+i,))
            g=np.asarray(gradient['gradient']);baseline_parity=abs(gradient['margin']-r['margin'])
            if not np.isfinite(baseline_parity) or baseline_parity>cfg['gates']['margin_parity']:
                raise ValueError('tail natural margin mismatch')
            if technical:
                fullg=compute('full_gradient_'+i,d,dict(mode='full_gradient',output=y.tolist()),
                    lambda:tail.native.gradient(tokens[i]['ids'],y[None])[0].tolist(),('full_backward_'+i,))
                gn=np.linalg.norm(fullg)
                if not np.isfinite(gn) or gn<=0:raise ValueError('zero/nonfinite full gradient')
                diff=g-np.asarray(fullg);grad_rel=float(np.linalg.norm(diff)/gn);grad_abs=float(np.max(np.abs(diff)))
                if baseline_parity>cfg['gates']['margin_parity'] or grad_rel>cfg['gates']['gradient_relative'] or grad_abs>cfg['gates']['gradient_absolute']:
                    raise ValueError('tail base/gradient mismatch')
            def tcbase():
                with torch.inference_mode():v,pre,mask=tc.forward(torch.tensor(z,dtype=torch.float32))
                return dict(output=v.double().tolist(),active=torch.where(mask & (pre>0))[0].tolist())
            base=compute('tc_base_'+i,d,dict(mode='TC_base'),tcbase);tc0=np.asarray(base['output']);native0=None
            for operator,v in [('full',delta),('projected',(delta@w)*w)]:
                def jvp(v=v):
                    p,t=torch.func.jvp(tail.native.branch,(torch.tensor(z,dtype=torch.float32),),(torch.tensor(v,dtype=torch.float32),))
                    return dict(primal=p.detach().double().tolist(),tangent=t.detach().double().tolist())
                derivative=compute(f'jvp_{i}_{operator}',d,dict(mode='native_JVP',delta=v.tolist()),jvp)
                n0=np.asarray(derivative['primal']);tangent=np.asarray(derivative['tangent'])
                anchor_norm=float(np.linalg.norm(y));anchor_absolute=float(np.max(np.abs(n0-y)))
                anchor_relative=float(np.linalg.norm(n0-y)/anchor_norm) if anchor_norm>0 else float('inf')
                if not np.isfinite(anchor_relative) or anchor_relative>cfg['gates']['branch_relative']:
                    raise ValueError('native branch capture anchor mismatch')
                if native0 is not None and not np.array_equal(native0,n0):raise ValueError('inconsistent JVP base')
                native0=n0
                def frozen(v=v):
                    mask=torch.zeros(tc.threshold.shape,dtype=torch.bool);mask[base['active']]=True
                    with torch.inference_mode():
                        x=torch.tensor(v,dtype=torch.float32);a=((x@tc.wenc)*mask)@tc.wdec
                        if tc.skip is not None:a=a+x@tc.skip
                    return a.double().tolist()
                if not technical:
                    frozen_v=np.asarray(compute(f'frozen_{i}_{operator}',d,dict(mode='frozen_TC_direction',delta=v.tolist()),frozen))
                for ci,c in enumerate(cfg['doses']):
                    tag=f'{i}_{operator}_{ci}';edit=c*v
                    def endpoint():
                        with torch.inference_mode():return tail.native.branch(torch.tensor(z+edit,dtype=torch.float32)).double().tolist()
                    n1=np.asarray(compute('native_endpoint_'+tag,d,dict(mode='native_endpoint',edit=edit.tolist()),endpoint))
                    def tcend():
                        with torch.inference_mode():return tc.forward(torch.tensor(z+edit,dtype=torch.float32))[0].double().tolist()
                    t1=np.asarray(compute('tc_endpoint_'+tag,d,dict(mode='TC_endpoint',edit=edit.tolist()),tcend))
                    # TC and linearized forecasts retain actual float32 arithmetic.
                    pred=dict(NATIVE=n1-n0,TC=(t1.astype(np.float32)-tc0.astype(np.float32)).astype(np.float64),
                              TAYLOR=(np.float32(c)*tangent.astype(np.float32)).astype(np.float64))
                    if not technical:
                        pred['FROZEN']=(np.float32(c)*frozen_v.astype(np.float32)).astype(np.float64)
                        full_ci=[.05,.1,.25,.5,1.,2.].index(c)
                        cell=('pooled' if d['frame']=='transfer' else d['frame'])+f'_{operator}_{full_ci}'
                        learned=predict(fit['cells'][cell],edit,d['side'])
                        pred.update({k.upper():val for k,val in learned.items()})
                    margins={};parity=[]
                    for method,value in pred.items():
                        target=(y+value).astype(np.float32)
                        margins[method]=compute(f'tail_{tag}_{method}',d,dict(mode='tail_output',target=target.tolist(),method=method),lambda target=target:tail.margin(record,target))-r['margin']
                        if technical:
                            full=compute(f'full_{tag}_{method}',d,dict(mode='full_output',target=target.tolist(),method=method),
                                lambda target=target:float(tail.native.forward(tokens[i]['ids'],'output',target,full_head=True)['margin'][0]))-r['margin']
                            err=abs(full-margins[method]);parity.append(err)
                            if err>cfg['gates']['margin_parity']:raise ValueError('tail intervention parity failed')
                    truth=margins['NATIVE'];methods={}
                    for method,value in pred.items():
                        if method=='NATIVE':continue
                        methods[method]=dict(finite=margins[method],loss=float((margins[method]-truth)**2),
                            vector_error=float(np.sum((value-pred['NATIVE'])**2)),linear_native=float(g@pred['NATIVE']),
                            linear_predicted=float(g@value),linear_vs_linear_error=float((g@(value-pred['NATIVE']))**2),
                            linear_vs_finite_error=float((g@value-truth)**2))
                    methods['ZERO']=dict(finite=0.,loss=float(truth**2),vector_error=float(np.sum(pred['NATIVE']**2)))
                    e0=tc0-n0;e1=t1-n1;error=(t1-tc0)-(n1-n0)
                    result=dict(document=d,operator=operator,dose=c,native_change=truth,native_signal=float(truth**2),methods=methods,
                        anchors=dict(margin_absolute=baseline_parity,branch_relative=anchor_relative,branch_absolute=anchor_absolute),
                        endpoints=dict(e0=e0.tolist(),e1=e1.tolist(),energy0=float(e0@e0),energy1=float(e1@e1),mixed=float(-2*e1@e0),
                            delta_error_energy=float(error@error),identity_max=float(np.max(np.abs(error-(e1-e0)))),
                            fp32_delta_discrepancy_max=float(np.max(np.abs(pred['TC']-(t1-tc0))))),tail_parity_max=max(parity) if parity else None)
                    immutable(out/'results'/i/f'{operator}_{ci}.json',result)
            if technical:qualification.append(dict(document=i,base_parity=baseline_parity,gradient_relative=grad_rel,gradient_absolute=grad_abs,passed=True))
            status('tail_evaluation')
        if technical:immutable(out/'qualification.json',dict(records=qualification,passed=all(q['passed'] for q in qualification),
            scope='exact full-native tail output/gradient parity; no scientific hypothesis result'))
        status('completed')
        files={p.relative_to(out).as_posix():sha(p) for p in sorted(out.rglob('*')) if p.is_file() and p!=complete}
        immutable(complete,dict(identity=identity,files=files,phase=cfg['phase'],attempted_operations=len(runtime.attempts)))
    finally:tail.close()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);main(p.parse_args().config)
