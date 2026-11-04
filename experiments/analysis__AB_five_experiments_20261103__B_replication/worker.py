"""Frozen second-artifact B study; canonical reviewed launch only."""
import argparse, json, time
from pathlib import Path
import numpy as np
from ab_confirmatory_20261101.prepare import ROOT,sha
from ab_confirmatory_20261101.baselines_b import fit_cell,predict
from research_checks.gate import digest
from research_checks.persistence import immutable
from analysis.Qwen06_ABC_extension_20261102.bundle_runtime import BundleRuntime

HERE=Path(__file__).resolve().parent
DOSES=[.05,.1,.25,.5,1.,2.]
METHODS=['TC','FROZEN','TAYLOR','RIDGE','MEAN','ZERO']

def plain(x):
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,dict):return {k:plain(v) for k,v in x.items()}
    if isinstance(x,list):return [plain(v) for v in x]
    if isinstance(x,np.generic):return x.item()
    return x

def unwrap(p):
    x=json.loads(Path(p).read_text());assert digest(x['payload'])==x['payload_sha256'];return x['payload']

def operations(docs,controls):
    ops=[]
    def add(x):ops.append(dict(id=x,kind='forward'))
    for d in docs:
        i=d['id'];add('capture_'+i)
        if d['split']=='FIT':
            add('fitbase_'+i)
            for j in range(6):add(f'fitend_{i}_{j}')
        else:
            for k in ['jvp','tcbase','frozen']:add(k+'_'+i)
            for j in range(6):
                for k in ['native','tc','suffix_NATIVE']+['suffix_'+m for m in METHODS if m!='ZERO']:
                    add(f'{k}_{i}_{j}')
    for i in controls:
        for k in ['sham_full','sham_tail','branch','edit_branch','input_full','output_full','edit_tail','tc_reference','tc_operator']:
            add('control_'+k+'_'+i)
    return dict(operations=ops)

def measure(cfg,engine,runtime,docs,tokens,out):
    caps={};done=0;start=time.monotonic();readout=dict(answer_ids=cfg['answer_ids'],orientation='she-minus-he')
    def run(ids,document,settings,fn):
        return runtime.compute(ids[0],document,settings,readout,lambda:plain(fn()),extra_operations=ids[1:])
    def status(stage):
        p=out/'STATUS.tmp';p.write_text(json.dumps(dict(stage=stage,completed_documents=done,
          total_documents=len(docs),logical_attempts=len(runtime.attempts),scheduled=len(runtime.ops),elapsed=time.monotonic()-start)))
        p.replace(out/'STATUS.json')
    # TEST states are not collected until fitting and technical checks finish.
    fitdocs=[d for d in docs if d['split']=='FIT'];testdocs=[d for d in docs if d['split']=='TEST']
    for d in fitdocs:
        caps[d['id']]=run(['capture_'+d['id']],d,dict(mode='capture',tokens=tokens[d['id']]),lambda d=d:engine.capture(tokens[d['id']]))
        done+=1;status('FIT_capture')
    for i in cfg['controls']:
        d=next(d for d in fitdocs if d['id']==i);r=caps[i];donor=caps[d['donor']]
        ids=['control_'+k+'_'+i for k in ['sham_full','sham_tail','branch','edit_branch','input_full','output_full','edit_tail','tc_reference','tc_operator']]
        checks=run(ids,d,dict(mode='technical',tokens=tokens[i],capture=digest(r),donor=digest(donor)),lambda:engine.controls(r,donor,tokens[i],cfg['gates']))
        if not checks['passed']:raise ValueError('Technical control failed '+i+': '+str(checks))
    fitpath=out/'frozen_fit.json'
    native={}
    for d in fitdocs:
        i=d['id'];r=caps[i];v=np.asarray(caps[d['donor']]['states']['x'])-r['states']['x']
        ids=['fitbase_'+i]+[f'fitend_{i}_{j}' for j in range(6)]
        def endpoints(r=r,v=v):
            z=np.asarray(r['states']['x']);n0=engine.branch(z)
            return dict(delta=v,base=n0,ends=[engine.branch(z+c*v) for c in DOSES])
        native[i]=run(ids,d,dict(mode='FIT_native_endpoints',capture=digest(r),donor=digest(caps[d['donor']])),endpoints)
    if fitpath.exists():fit=unwrap(fitpath)
    else:
        cells={}
        for frame in ['so','when','pooled']:
            ds=[d for d in fitdocs if frame=='pooled' or d['frame']==frame]
            for j,c in enumerate(DOSES):
                x=[c*np.asarray(native[d['id']]['delta']) for d in ds]
                y=[np.asarray(native[d['id']]['ends'][j])-native[d['id']]['base'] for d in ds]
                cells[f'{frame}_{j}']=plain(fit_cell(x,y,[d['side'] for d in ds]))
        fit=dict(cells=cells,fit_ids=[d['id'] for d in fitdocs],scope='FIT vectors only; lambda=.01; no TEST states or labels')
        immutable(fitpath,fit)
    for d in testdocs:
        caps[d['id']]=run(['capture_'+d['id']],d,dict(mode='capture',tokens=tokens[d['id']]),lambda d=d:engine.capture(tokens[d['id']]))
        done+=1;status('TEST_capture')
    rows=[];completed=0
    for d in testdocs:
        i=d['id'];r=caps[i];v=np.asarray(caps[d['donor']]['states']['x'])-r['states']['x']
        ids=[k+'_'+i for k in ['jvp','tcbase','frozen']]
        for j in range(6):
            ids += [f'{k}_{i}_{j}' for k in ['native','tc','suffix_NATIVE']+['suffix_'+m for m in METHODS if m!='ZERO']]
        def evaluate(r=r,v=v,d=d):
            z=np.asarray(r['states']['x']);y=np.asarray(r['states']['y']);m0=float(r['states']['margin'])
            n0,tangent=engine.jvp(z,v);tc0=engine.tc(z);frozen=engine.frozen(z,v)
            if np.linalg.norm(n0-y)/max(np.linalg.norm(y),1e-30)>cfg['gates']['branch_relative']:raise ValueError('Branch anchor mismatch')
            data=[]
            for j,c in enumerate(DOSES):
                n1=engine.branch(z+c*v);tc1=engine.tc(z+c*v)
                cell=fit['cells'][('pooled' if d['frame']=='transfer' else d['frame'])+f'_{j}']
                learned=predict(cell,c*v,d['side'])
                pred=dict(NATIVE=n1-n0,TC=(tc1.astype(np.float32)-tc0.astype(np.float32)).astype(float),
                    FROZEN=(np.float32(c)*frozen.astype(np.float32)).astype(float),
                    TAYLOR=(np.float32(c)*tangent.astype(np.float32)).astype(float),
                    RIDGE=learned['ridge'],MEAN=learned['mean'])
                margins={k:engine.margin(r,(y+val).astype(np.float32))-m0 for k,val in pred.items()}
                margins['ZERO']=0.
                data.append(dict(dose=c,native=margins.pop('NATIVE'),predictions=margins))
            return data
        values=run(ids,d,dict(mode='TEST_curve',capture=digest(r),donor=digest(caps[d['donor']]),fit=digest(fit)),evaluate)
        rows.extend(dict(document=i,block=d['block'],frame=d['frame'],side=d['side'],**v) for v in values)
        completed+=1
        p=out/'STATUS.tmp';p.write_text(json.dumps(dict(stage='TEST_curve',completed=completed,total=len(testdocs),logical_attempts=len(runtime.attempts),scheduled=len(runtime.ops),elapsed=time.monotonic()-start)));p.replace(out/'STATUS.json')
    immutable(out/'rows.json',rows)
    # Fixed descriptive block-bootstrap intervals, no population/family qualification claim.
    summary=[]
    for frame in ['so','when','transfer','main_mixture']:
        for c in DOSES:
            rr=[r for r in rows if r['dose']==c and (r['frame'] in ['so','when'] if frame=='main_mixture' else r['frame']==frame)]
            blocks=sorted({r['block'] for r in rr})
            for method in METHODS:
                e=np.array([np.mean([(r['predictions'][method]-r['native'])**2 for r in rr if r['block']==b]) for b in blocks])
                s=np.array([np.mean([r['native']**2 for r in rr if r['block']==b]) for b in blocks])
                rng=np.random.default_rng(20261103);idx=rng.integers(0,len(blocks),(1999,len(blocks)))
                ratio=np.sqrt(e[idx].mean(1)/np.maximum(s[idx].mean(1),1e-300))
                summary.append(dict(frame=frame,dose=c,method=method,blocks=len(blocks),rms_error=float(np.sqrt(e.mean())),
                    native_rms=float(np.sqrt(s.mean())),relative_rms=float(np.sqrt(e.mean()/s.mean())) if s.mean()>0 else None,
                    nominal_block_percentile95=np.quantile(ratio,[.025,.975]).tolist(),inference='descriptive, fixed artifact and FIT; nominal pointwise block interval'))
    immutable(out/'summary.json',summary)
    return dict(rows=len(rows),cells=len(summary),logical_forward=len(runtime.attempts),scheduled=len(runtime.ops))

class Engine:
    def __init__(self,cfg):
        import torch
        from transformers import AutoModelForCausalLM
        from safetensors.torch import load_file
        from ab_confirmatory_20261101.native_tail_b import ExactTail
        from ab_confirmatory_20261101.transcoder import Transcoder
        torch.set_num_threads(cfg['threads']);self.torch=torch
        model,info=AutoModelForCausalLM.from_pretrained(str(ROOT/cfg['model']),local_files_only=True,dtype=torch.float32,attn_implementation='eager',low_cpu_mem_usage=True,output_loading_info=True)
        tied=model.get_input_embeddings().weight.data_ptr()==model.get_output_embeddings().weight.data_ptr()
        if set(info.get('missing_keys',[]))-({'lm_head.weight'} if tied else set()) or info.get('mismatched_keys') or info.get('error_msgs'):raise ValueError('Incomplete model')
        self.tail=ExactTail(model.eval().float(),cfg['layer'],cfg['answer_ids'])
        folder=ROOT/cfg['tc'];meta=json.loads((folder/'config.json').read_text());layer=cfg['layer']
        if meta['hf_hook_point_in']!=f'model.layers.{layer}.pre_feedforward_layernorm.output' or meta['hf_hook_point_out']!=f'model.layers.{layer}.post_feedforward_layernorm.output' or meta['architecture']!='jump_relu' or meta['affine_connection']:raise ValueError('TC hook/skip mismatch')
        self.tcstate=load_file(str(folder/'params.safetensors'));self.transcoder=Transcoder(self.tcstate)
        if self.transcoder.skip is not None:raise ValueError('unexpected skip')
    def tensor(self,x):return self.torch.tensor(x,dtype=self.torch.float32)
    def branch(self,x):
        with self.torch.inference_mode():return self.tail.native.branch(self.tensor(x)).double().numpy()
    def tc(self,x):
        with self.torch.inference_mode():return self.transcoder.forward(self.tensor(x))[0].double().numpy()
    def frozen(self,z,v):
        with self.torch.inference_mode():
            t=self.transcoder;p=self.tensor(z)@t.wenc+t.benc;m=(p>t.threshold)&(p>0)
            return (((self.tensor(v)@t.wenc)*m)@t.wdec).double().numpy()
    def jvp(self,z,v):
        p,t=self.torch.func.jvp(self.tail.native.branch,(self.tensor(z),),(self.tensor(v),))
        return p.detach().double().numpy(),t.detach().double().numpy()
    def capture(self,ids):return self.tail.capture(ids)
    def margin(self,r,y):return self.tail.margin(r,y)
    def controls(self,r,d,ids,gates):
        z=np.array(r['states']['x']);y=np.array(r['states']['y']);base=float(r['states']['margin']);v=np.array(d['states']['x'])-z
        shamfull=float(self.tail.native.forward(ids,'output',y)['margin'][0]);shamtail=self.margin(r,y);n0=self.branch(z);n1=self.branch(z+v)
        fullinput=float(self.tail.native.forward(ids,'input',(z+v).astype(np.float32))['margin'][0]);fulloutput=float(self.tail.native.forward(ids,'output',n1)['margin'][0]);tailoutput=self.margin(r,n1)
        with self.torch.inference_mode():
            st=self.tcstate;p=self.tensor(z)@st['w_enc'].float()+st['b_enc'].float();ref=((self.torch.relu(p)*(p>st['threshold'].float()))@st['w_dec'].float()+st['b_dec'].float()).double().numpy()
        actual=self.tc(z)
        values=dict(sham_full=abs(shamfull-base),sham_tail=abs(shamtail-base),branch=float(np.linalg.norm(n0-y)/max(np.linalg.norm(y),1e-30)),
            input_output=abs(fullinput-fulloutput),tail_output=abs(tailoutput-fulloutput),sensitivity=abs(fullinput-base),tc_reference=float(np.max(abs(ref-actual))))
        passed=all(np.isfinite(list(values.values()))) and max(values['sham_full'],values['sham_tail'],values['input_output'],values['tail_output'])<=gates['margin_absolute'] and values['branch']<=gates['branch_relative'] and values['tc_reference']<=1e-5 and values['sensitivity']>1e-7
        return dict(passed=bool(passed),**values)

def main():
    from importlib.metadata import version
    software=json.loads((HERE/'software_identity.json').read_text())
    for package,v in software['versions'].items():
        if version(package)!=v:raise ValueError('Software version changed '+package)
    for p,h in software['files'].items():
        if sha(p)!=h:raise ValueError('Software source changed '+p)
    cfg=json.loads((HERE/'config.json').read_text());docs=json.loads((HERE/'corpus.json').read_text())['documents'];tokens=json.loads((HERE/'tokens.json').read_text());ops=operations(docs,cfg['controls'])
    if ops!=json.loads((HERE/'operations.json').read_text()):raise ValueError('Schedule changed')
    manifest=json.loads((HERE/'input_manifest.json').read_text())
    for p,h in manifest['files'].items():
        if sha(ROOT/p)!=h:raise ValueError('Input changed '+p)
    files=json.loads((HERE/'code_manifest.json').read_text())['files']
    for p,h in files.items():
        if sha(ROOT/p)!=h:raise ValueError('Code changed '+p)
    identity=dict(model=digest(manifest),code=digest(dict(files=files,config=cfg)),corpus=sha(HERE/'corpus.json'),tokens=sha(HERE/'tokens.json'))
    out=HERE/'run';runtime=BundleRuntime(out,identity,ops)
    if (out/'completed.json').exists():
        c=unwrap(out/'completed.json')
        for f,h in c['files'].items():
            if sha(out/f)!=h:raise ValueError('Completed output changed')
        return
    immutable(out/'model_load_attempt.json',dict(identity=identity,attempt=1))
    if (out/'MODEL_STARTED').exists():raise ValueError('Prior model attempt exists; explicit reviewed resume required')
    (out/'MODEL_STARTED').write_text('one model load attempt\n')
    engine=Engine(cfg)
    result=measure(cfg,engine,runtime,docs,tokens,out)
    if len(runtime.attempts)!=len(runtime.ops):raise ValueError('Incomplete operations')
    immutable(out/'completed.json',dict(result=result,files={p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file() and p.name not in ['STATUS.json','completed.json','STATUS.tmp']}))
    (out/'STATUS.json').write_text(json.dumps(dict(stage='completed',**result)))

if __name__=='__main__':main()
