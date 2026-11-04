"""Freeze exact cache inputs before target construction; no model loading."""
import json
from pathlib import Path
from .common import HERE,ROOT,read,sha,put,operation

def main():
    cfg=read(HERE/'config.json');idx=read(ROOT/cfg['historical_index']);run=ROOT/cfg['historical_run'];ident=read(ROOT/cfg['model_identity'])
    cells=[c for c in idx['cells'] if c['document']['frame'] in cfg['frames'] and c['operator']==cfg['operator'] and c['dose']==cfg['dose']]
    assert len(cells)==cfg['expected_contexts'] and len({c['document']['block'] for c in cells})==cfg['expected_blocks']
    names=[HERE/x for x in ['PLAN.txt','config.json','FIT_SCALE_FREEZE.json','common.py','prepare_stage1.py','stage1.py','fixtures.py','fixtures.json']]
    names += [ROOT/cfg[k] for k in ['groups_source','fit_source','historical_index','model_identity']]
    names += [ROOT/'analysis/AB_five_experiments_20261103/B_mechanism'/x for x in ['worker_v3.py','geometry.py']]
    names += [ROOT/'ab_confirmatory_20261101/transcoder.py',ROOT/'research_checks/gate.py',ROOT/'research_checks/persistence.py',ROOT/'research_checks/reachability.py',ROOT/'research_checks/__init__.py']
    names += [Path(ident['TC']['folder'])/'params.safetensors',Path(ident['TC']['folder'])/'config.json']
    items=[]
    for c in cells:
        doc=c['document'];base,extra0=operation(run,'encode_base_'+doc['id']);end,extra1=operation(run,'encode_end_'+c['id'])
        names+=extra0+extra1
        entries=dict(base=base,end=end,capture=idx['captures'][doc['id']],tc=c['tc'],tcbase=c['tcbase'],tcend=c['tcend'])
        for e in entries.values():names.extend([ROOT/e['cache'],ROOT/e['receipt']])
        items.append(dict(cell=c['id'],document=doc,entries=entries))
    put(HERE/'stage1_index.json',dict(items=items));names.append(HERE/'stage1_index.json')
    (HERE/'stage1_input_manifest.json').write_text(json.dumps(dict(files={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(set(names))}),indent=2)+'\n',encoding='utf-8')
    prefix=HERE.relative_to(ROOT).as_posix();evidence=prefix+'/fixtures.json'
    contract=dict(schema_version=1,id='B_NORM_TARGET_FREEZE_20261103',kind='experiment',primary_agent='/root/b_switch_fit',purpose='Freeze norm-matched TC mask-direction targets and eligibility before new readouts; cache algebra only.',
        tracked_files=[prefix+'/stage1_input_manifest.json',prefix+'/stage1_index.json',prefix+'/PLAN.txt',prefix+'/config.json',prefix+'/FIT_SCALE_FREEZE.json',prefix+'/common.py',prefix+'/stage1.py',prefix+'/prepare_stage1.py',prefix+'/fixtures.py',prefix+'/fixtures.json'],
        tracked_trees=[],input_manifests=[prefix+'/stage1_input_manifest.json'],gates=[dict(id=k,category=k,evidence=evidence,pointer='/payload/passed',op='eq',expected=True,reason='Detailed synthetic cache-target construction, matched norm and joint eligibility; zero pretrained stage.') for k in ['hooks','data','pilot','accounting','restart']],circuits=[],structural_scope='No circuit/native suffix executed; cache-only prediction-vector algebra.',
        entrypoint=dict(module='analysis.B_norm_control_20261103.stage1',args=[]),schedule=prefix+'/stage1_schedule.json',budget=dict(forward=0,backward=0))
    (HERE/'stage1_schedule.json').write_text(json.dumps(dict(operations=[]))+'\n',encoding='utf-8')
    (HERE/'stage1_contract.json').write_text(json.dumps(contract,indent=2)+'\n',encoding='utf-8')
    print('Frozen inputs',len(set(names)),'contexts',len(cells),'frames',cfg['frames'])
if __name__=='__main__':main()
