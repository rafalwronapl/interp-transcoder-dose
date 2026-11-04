"""Explicitly bind valid old measurements; never silently reuse code identities."""
from pathlib import Path
import json
from research_checks.gate import read,sha,digest
H=Path(__file__).resolve().parent;R=H.parents[2];rel=lambda p:p.relative_to(R).as_posix()
def put(n,x):(H/n).write_text(json.dumps(x,indent=2)+'\n')
def un(p):
 v=read(p);assert v['payload_sha256']==digest(v['payload']);return v['payload']
cfg=read(H/'config.json');manifest=dict(read(R/cfg['input_manifest'])['files']);adopt={}
def bind(p):manifest[rel(p)]=sha(p);return rel(p)
for receipt in sorted((H/'run/completed').glob('*.json')):
 v=un(receipt);op=v['operation']
 if op.endswith('_backward') or not(op.startswith('control_') or op.startswith('fit_')):continue
 cache=H/'run/cache'/(v['request']+'.json');assert digest(un(cache)['request'])==v['request']
 adopt[op]=dict(cache=bind(cache),receipt=bind(receipt),origin='actual1thread FIT/control measurement; no relabeling')
 if op.endswith('_gradient'):
  backward=H/'run/completed'/(op.removesuffix('_gradient')+'_backward.json')
  assert un(backward)['request']==v['request'];adopt[op]['backward_receipt']=bind(backward)
q=H/'qualification';assert un(q/'run/RESULT.json')['passed']
first=read(R/cfg['source_index'])['cells'][0]
for label,op in [('base','encode_base_'+first['document']['id']),('end','encode_end_'+first['id'])]:
 receipt=q/'run/completed'/(label+'.json');v=un(receipt);cache=q/'run/cache'/(v['request']+'.json');assert digest(un(cache)['request'])==v['request']
 adopt[op]=dict(cache=bind(cache),receipt=bind(receipt),origin='reviewed2thread qualification',qualification=True)
bind(q/'run/RESULT.json');bind(q/'completion_audit.json');bind(H/'run/FEATURE_SELECTION.json')
put('adoption_v3.json',dict(operations=adopt,feature_selection=rel(H/'run/FEATURE_SELECTION.json'),scope='Old controls/FIT retained at actual1thread;2qualifiedTCcalls retained at2threads. Other1threadTCresults preserved but unsuitable for bitwise historical aliases.'))
bind(H/'adoption_v3.json')
put('input_manifest_v3.json',dict(files=manifest))
cfg.update(output=rel(H/'run_v3'),input_manifest=rel(H/'input_manifest_v3.json'),adoption=rel(H/'adoption_v3.json'),tc_threads=2)
put('config_v3.json',cfg)
s=(H/'worker.py').read_text()
s=s.replace("runtime=Runtime(out,dict(model=digest(ident),code=digest(manifest)),ops)","runtime=Runtime(out,dict(model=digest(ident),code=digest(manifest)),ops)\n    adoption=read(ROOT/cfg['adoption'])")
s=s.replace("    def calc(op,doc,settings,fn,extra=()):\n",'''    def calc(op,doc,settings,fn,extra=()):
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
''')
s=s.replace("            with torch.inference_mode():y,p,m=tc.forward(torch.tensor(x,dtype=torch.float32))", "            torch.set_num_threads(cfg['tc_threads'])\n            try:\n                with torch.inference_mode():y,p,m=tc.forward(torch.tensor(x,dtype=torch.float32))\n            finally:torch.set_num_threads(cfg['threads'])")
s=s.replace("        with torch.inference_mode():return (torch.tensor(h,dtype=torch.float32)@tc.wdec+tc.bdec).numpy()", "        torch.set_num_threads(cfg['tc_threads'])\n        try:\n            with torch.inference_mode():return (torch.tensor(h,dtype=torch.float32)@tc.wdec+tc.bdec).numpy()\n        finally:torch.set_num_threads(cfg['threads'])")
s=s.replace("        bases={}","        assert unwrap(ROOT/adoption['feature_selection'])['top']==top.tolist()\n        assert unwrap(ROOT/adoption['feature_selection'])['random']==random.tolist()\n        bases={}")
s=s.replace("tmp.replace(out/'STATUS.json')", "publish_status(tmp,out/'STATUS.json')")
s=s.replace('import argparse, json, math, uuid','import argparse, json, math, uuid, time')
s=s.replace('def main(config):', '''def publish_status(source,target):
    # Telemetry only: transient Windows readers must not terminate scientific work.
    for attempt in range(20):
        try:source.replace(target);return
        except PermissionError:time.sleep(.05)
    return

def main(config):''')
(H/'worker_v3.py').write_text(s)
c=read(H/'contract.json');c['id']+='_RESUME_V3';c['primary_agent']='/root/b_second_artifact_five';c['purpose']+=' Exact historical2threadTC arithmetic; explicit adoption of valid actual1thread FIT/control cache, no tolerance relaxation.'
c['tracked_files'] += [rel(H/n) for n in ['worker_v3.py','prepare_resume.py','config_v3.json','adoption_v3.json']]
c['input_manifests']=[rel(H/'input_manifest_v3.json')];c['entrypoint']=dict(module='analysis.AB_five_experiments_20261103.B_mechanism.worker_v3',args=['--config',rel(H/'config_v3.json')]);put('contract_v3.json',c)
print('adopted_operations',len(adopt))
