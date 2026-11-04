"""B fixed FIT acquisition; exact scheduled calls, two qualification gates.

No pretrained imports/loads on import. Invoke through research_checks launch.
Evaluation is deliberately rejected by this FIT-only executable.
"""
import argparse,json,time
from pathlib import Path
import numpy as np
from research_checks.gate import digest
from research_checks.persistence import immutable
from .prepare import ROOT,sha
from .runtime import Runtime
from .baselines_b import fit_cell

DOSES=(.05,.1,.25,.5,1.,2.)
DEPENDENCIES=['__init__.py','worker_b.py','prepare.py','native.py','runtime.py','baselines_b.py','transcoder.py']

def plain(value):
    if isinstance(value,np.ndarray):return value.tolist()
    if isinstance(value,dict):return {k:plain(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [plain(v) for v in value]
    if isinstance(value,np.generic):return value.item()
    return value

def schedule(config,documents):
    ops=[]
    def add(name,kind='forward'):ops.append(dict(id=name,kind=kind))
    for d in documents:
        i=d['id'];add('capture_'+i)
        if i in config['control_documents']:
            for k in ['sham_input','gradient','positive','full_head','donor_input','donor_output','tc_reference']:
                add(k+'_'+i)
            add('gradient_backward_'+i,'backward')
            add('tc_reference_independent_'+i)
        for operator in ['full','projected']:
            if i in config['control_documents']:
                add(f'jvp_{i}_{operator}')
                for h in ['0.001','0.0005']:
                    for sign in ['minus','plus']:add(f'fd_{i}_{operator}_{h}_{sign}')
            elif operator=='full':add('base_'+i)
            for ci in range(len(DOSES)):add(f'endpoint_{i}_{operator}_{ci}')
    if len({x['id'] for x in ops})!=len(ops):raise ValueError('duplicate operation')
    return dict(operations=ops)

def main(config_path):
    cfg=json.loads((ROOT/config_path).read_text(encoding='utf-8'))
    if cfg['study']!='B' or cfg['phase']!='FIT_ONLY':raise ValueError('B FIT-only worker')
    corpus=json.loads((ROOT/cfg['corpus']).read_text(encoding='utf-8'))
    tokens=json.loads((ROOT/cfg['tokens']).read_text(encoding='utf-8'))
    identities=json.loads((ROOT/cfg['model_identity']).read_text(encoding='utf-8'))
    for model in ['B','TC']:
        for name,meta in identities[model]['files'].items():
            if sha(name)!=meta['sha256']:raise ValueError('changed artifact '+name)
    docs=corpus['documents'];lookup={d['id']:d for d in docs}
    if len(lookup)!=len(docs) or len(docs)!=cfg['expected_documents']:raise ValueError('invalid corpus size')
    for d in docs:
        if d['study']!='B' or d['split']!='FIT' or d['donor'] not in lookup:raise ValueError('FIT scope violation')
        if lookup[d['donor']]['donor']!=d['id']:raise ValueError('invalid donor')
    controls=cfg['control_documents']
    if not controls or any(x not in lookup for x in controls):raise ValueError('missing qualification')
    if any(tokens[d['id']]['answer_ids']!=cfg['answer_ids'] for d in docs):raise ValueError('readout identity mismatch')
    ops=json.loads((ROOT/cfg['schedule']).read_text(encoding='utf-8'))
    if ops!=schedule(cfg,docs):raise ValueError('schedule differs from actual FIT recipe')
    sources={f'ab_confirmatory_20261101/{n}':sha(ROOT/'ab_confirmatory_20261101'/n) for n in DEPENDENCIES}
    identity=dict(model=digest(identities),code=digest(dict(sources=sources,config_sha256=sha(ROOT/config_path))),config=sha(ROOT/config_path),
                  corpus=sha(ROOT/cfg['corpus']),tokens=sha(ROOT/cfg['tokens']))
    out=ROOT/cfg['output'];runtime=Runtime(out,identity,ops)
    complete=out/'stage_completed.json'
    if complete.exists():
        r=json.loads(complete.read_text())
        if r['payload_sha256']!=digest(r['payload']):raise ValueError('corrupt completion')
        for name,h in r['payload']['files'].items():
            if sha(out/name)!=h:raise ValueError('changed completed evidence '+name)
        return
    import torch
    from transformers import AutoModelForCausalLM
    from .native import Native
    from .transcoder import load
    torch.set_num_threads(cfg['threads'])
    model,info=AutoModelForCausalLM.from_pretrained(identities['B']['folder'],local_files_only=True,
        dtype=torch.float32,attn_implementation='eager',low_cpu_mem_usage=True,output_loading_info=True)
    tied=model.get_input_embeddings().weight.data_ptr()==model.get_output_embeddings().weight.data_ptr()
    if set(info.get('missing_keys',[]))-({'lm_head.weight'} if tied else set()) or info.get('mismatched_keys') or info.get('error_msgs'):
        raise ValueError('incomplete model weights')
    native=Native(model.eval().float(),cfg['layer'],cfg['answer_ids']);tc=load(identities['TC']['folder'])
    started=time.monotonic();caps={};bases={};jvps={};qualification=[]
    def status(stage):
        payload=dict(stage=stage,captures=len(caps),total_captures=len(docs),completed_operations=len(list((out/'completed').glob('*.json'))),
                     scheduled_operations=len(ops['operations']),elapsed_seconds=time.monotonic()-started)
        tmp=out/'STATUS.tmp';tmp.write_text(json.dumps(payload,indent=2));tmp.replace(out/'STATUS.json')
    def compute(op,d,settings,fn,extra=()):
        return runtime.compute(op,dict(document=d,tokens=tokens[d['id']]),settings,
            dict(answer_ids=cfg['answer_ids'],orientation='she-minus-he'),fn,extra_operations=extra)
    def capture(d):
        i=d['id']
        def run():
            r=native.forward(tokens[i]['ids']);return {k:r[k][0].tolist() for k in ('R','x','y','margin')}
        caps[i]=compute('capture_'+i,d,dict(mode='natural',layer=cfg['layer']),run);status('capture')
    def branch(z):
        with torch.inference_mode():return native.branch(torch.tensor(z,dtype=torch.float32)).double().numpy().tolist()
    def forward(d,label,mode=None,value=None,full=False):
        return compute(label+'_'+d['id'],d,dict(mode=mode,value=plain(value),full_head=full,label=label),
            lambda:{k:v.tolist() for k,v in native.forward(tokens[d['id']]['ids'],mode,value,full_head=full).items()})
    def derivative_check(d,operator,delta):
        i=d['id'];z=np.asarray(caps[i]['x']);delta=np.asarray(delta)
        def jvp():
            x=torch.tensor(z,dtype=torch.float32);v=torch.tensor(delta,dtype=torch.float32)
            primal,tangent=torch.func.jvp(native.branch,(x,),(v,))
            return dict(primal=primal.detach().double().numpy().tolist(),tangent=tangent.detach().double().numpy().tolist())
        row=compute(f'jvp_{i}_{operator}',d,dict(kind='local_jvp',delta=delta.tolist()),jvp)
        n0=np.asarray(row['primal']);tangent=np.asarray(row['tangent']);jvps[(i,operator)]=tangent
        if i in bases and not np.array_equal(bases[i],n0):raise ValueError('JVP primal inconsistent')
        bases[i]=n0
        base_norm=float(np.linalg.norm(n0))
        if not np.isfinite(base_norm) or base_norm<=0:raise ValueError('zero/nonfinite native branch norm')
        base_error=float(np.linalg.norm(n0-np.asarray(caps[i]['y']))/base_norm)
        errors=[]
        for h in (.001,.0005):
            values=[]
            for sign in [-1,1]:
                name='minus' if sign<0 else 'plus';x=z+sign*h*delta
                values.append(np.asarray(compute(f'fd_{i}_{operator}_{h}_{name}',d,
                    dict(kind='local_fd',operator=operator,h=h,sign=sign),lambda x=x:branch(x))))
            err=float(np.linalg.norm((values[1]-values[0])/(2*h)-tangent));errors.append(err)
        tolerance=cfg['gates']['fd_base']*max(np.linalg.norm(n0),1)+cfg['gates']['fd_relative']*np.linalg.norm(tangent)
        passed=base_error<=cfg['gates']['branch_relative'] and all(np.isfinite(errors)) and max(errors)<=tolerance
        result=dict(document=i,operator=operator,base_norm=base_norm,tangent_norm=float(np.linalg.norm(tangent)),base_relative=base_error,fd_errors=errors,tolerance=float(tolerance),passed=bool(passed))
        immutable(out/'qualification'/f'{i}_{operator}_jvp.json',result)
        if not passed:raise ValueError('native derivative qualification failed')
        return result
    try:
        first=set(controls)|{lookup[i]['donor'] for i in controls}
        for d in docs:
            if d['id'] in first:capture(d)
        for i in controls:
            d=lookup[i];r=caps[i];donor=caps[d['donor']];z=np.asarray(r['x']);y=np.asarray(r['y']);delta=np.asarray(donor['x'])-z
            derivative_check(d,'full',delta)
            sham=forward(d,'sham_input','input',z)
            def gradient():
                leaf=torch.tensor([r['y']],dtype=torch.float32,requires_grad=True)
                return {k:v.tolist() for k,v in native.forward(tokens[i]['ids'],'output',leaf,gradient=True).items()}
            grad=compute('gradient_'+i,d,dict(mode='output_sham_gradient',value=r['y']),gradient,('gradient_backward_'+i,))
            g=np.asarray(grad['gradient'][0]);gn=np.linalg.norm(g)
            if not np.isfinite(gn) or gn<=0:raise ValueError('zero gradient sensitivity')
            amp=.01*max(np.linalg.norm(y),1);positive=forward(d,'positive','output',y+amp*g/gn)
            full=forward(d,'full_head',full=True);inp=forward(d,'donor_input','input',donor['x'])
            # Use same actual local endpoint for parity and later full c1 FIT label.
            n1=np.asarray(compute(f'endpoint_{i}_full_4',d,dict(kind='local_native',operator='full',dose=1.),lambda:branch(z+delta)))
            outpatch=forward(d,'donor_output','output',y+n1-bases[i])
            def reference():
                x=torch.tensor(z,dtype=torch.float32)
                with torch.inference_mode():
                    actual,_,_=tc.forward(x)
                    pre=torch.nn.functional.linear(x,tc.wenc.T,tc.benc)
                    active=torch.where(pre>tc.threshold,torch.clamp_min(pre,0),torch.zeros_like(pre))
                    expected=torch.nn.functional.linear(active,tc.wdec.T,tc.bdec)
                    if tc.skip is not None:expected=expected+torch.nn.functional.linear(x,tc.skip.T)
                return dict(actual=actual.double().tolist(),expected=expected.double().tolist())
            ref=compute('tc_reference_'+i,d,dict(kind='TC_formula_reference'),reference,('tc_reference_independent_'+i,))
            diff=np.asarray(ref['actual'])-ref['expected'];shamerr=max(abs(sham['margin'][0]-r['margin']),abs(grad['margin'][0]-r['margin']))
            floor=max(1e-5,10*shamerr,64*np.finfo(np.float32).eps*max(1,abs(r['margin'])))
            positive_change=positive['margin'][0]-r['margin']
            parity=max(abs(full['margin'][0]-r['margin']),abs(inp['margin'][0]-outpatch['margin'][0]))
            endpoint_norm=float(np.linalg.norm(n1))
            if not np.isfinite(endpoint_norm) or endpoint_norm<=0:raise ValueError('zero/nonfinite perturbed branch norm')
            brancherr=float(np.linalg.norm(np.asarray(inp['y'][0])-n1)/endpoint_norm)
            passed=(shamerr<=cfg['gates']['sham_abs'] and positive_change>floor and parity<=cfg['gates']['margin_parity'] and
                    brancherr<=cfg['gates']['branch_relative'] and np.max(np.abs(diff))<=1e-5 and np.linalg.norm(diff)<=1e-5*max(np.linalg.norm(ref['expected']),1))
            q=dict(document=i,sham=shamerr,gradient_norm=float(gn),positive_amplitude=float(amp),positive_change=positive_change,positive_floor=floor,margin_parity=parity,
                   endpoint_norm=endpoint_norm,branch_relative=brancherr,tc_max_absolute=float(np.max(np.abs(diff))),tc_difference_norm=float(np.linalg.norm(diff)),
                   tc_reference_norm=float(np.linalg.norm(ref['expected'])),passed=bool(passed))
            qualification.append(q)
        immutable(out/'gate1.json',qualification)
        if not all(q['passed'] for q in qualification):raise ValueError('gate1 failed before natural expansion')
        for d in docs:
            if d['id'] not in caps:capture(d)
        classes=np.asarray([d['side'] for d in docs]);z=np.array([caps[d['id']]['x'] for d in docs])
        w=z[classes==1].mean(0)-z[classes==0].mean(0);wn=np.linalg.norm(w)
        if not np.isfinite(wn) or wn<=0:raise ValueError('zero FIT direction')
        w=w/wn;immutable(out/'direction.json',dict(w=w.tolist(),identity=identity))
        gate2=[]
        for i in controls:
            d=lookup[i];delta=np.asarray(caps[d['donor']]['x'])-caps[i]['x']
            gate2.append(derivative_check(d,'projected',(delta@w)*w))
        immutable(out/'gate2.json',gate2)
        cells={};rows={}
        for d in docs:
            i=d['id'];r=caps[i];z=np.asarray(r['x']);delta=np.asarray(caps[d['donor']]['x'])-z
            if i not in bases:bases[i]=np.asarray(compute('base_'+i,d,dict(kind='local_native_base'),lambda z=z:branch(z)))
            for op,v in [('full',delta),('projected',(delta@w)*w)]:
                for ci,c in enumerate(DOSES):
                    edit=c*v;n1=np.asarray(compute(f'endpoint_{i}_{op}_{ci}',d,dict(kind='local_native',operator=op,dose=c),lambda z=z,edit=edit:branch(z+edit)))
                    label=n1-bases[i];key=f'{d["frame"]}_{op}_{ci}'
                    for k in [key,f'pooled_{op}_{ci}']:rows.setdefault(k,[]).append((edit,label,d['side']))
            status('FIT_endpoints')
        for key,values in rows.items():
            x,y,c=zip(*values);cells[key]=fit_cell(np.asarray(x),np.asarray(y),np.asarray(c))
        immutable(out/'FIT_B.json',plain(dict(identity=identity,direction=w,cells=cells,recipe='fixed32blocks_vector_only_lambda0.01')))
        status('completed')
        files={p.relative_to(out).as_posix():sha(p) for p in sorted(out.rglob('*')) if p.is_file() and p!=complete}
        immutable(complete,dict(identity=identity,files=files,phase='FIT_ONLY',operations=len(runtime.attempts)))
    finally:native.close()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--config',required=True);main(parser.parse_args().config)
