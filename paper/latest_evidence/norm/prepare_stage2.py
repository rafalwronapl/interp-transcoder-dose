"""Build exact suffix-only schedule and full provenance/weight manifest."""
import json
from pathlib import Path
from .common import HERE,ROOT,read,unwrap,sha,put
from .worker import ARMS

def main():
    cfg=read(HERE/'config.json');old=read(ROOT/cfg['historical_index']);idx=unwrap(HERE/'stage1_index.json');seal=unwrap(HERE/'TARGETS_FROZEN.json')
    bycell={c['id']:c for c in old['cells']};items=[]
    names=[HERE/x for x in ['PLAN.txt','config.json','FIT_SCALE_FREEZE.json','common.py','worker.py','prepare_stage2.py','worker_fixtures.py','worker_fixtures_v2.json','TARGETS_FROZEN.json']]
    names += [ROOT/x for x in read(HERE/'stage1_input_manifest.json')['files']]
    for i in idx['items']:
        c=bycell[i['cell']];entry=dict(cell=i['cell'],target='targets/'+i['cell']+'.json',capture=i['entries']['capture'],tc=i['entries']['tc'],native=c['native'])
        names.append(HERE/entry['target']);names.extend([ROOT/c['native']['cache'],ROOT/c['native']['receipt']]);items.append(entry)
    controls=[old['controls'][k] for k in sorted(old['controls'])[:2]]
    for control in controls:
        for e in control.values():names.extend([ROOT/e['cache'],ROOT/e['receipt']])
    parity=[next(i['cell'] for i in idx['items'] if i['document']['frame']==f) for f in cfg['frames']]
    put(HERE/'stage2_index.json',dict(items=items,controls=controls,reference_parity_cells=parity));names.append(HERE/'stage2_index.json')
    ident=read(ROOT/cfg['model_identity'])
    for name,v in ident['B']['files'].items():
        p=Path(name);assert sha(p)==v['sha256'],'Changed native identity '+name;names.append(p)
    dependencies=['ab_confirmatory_20261101/__init__.py','ab_confirmatory_20261101/runtime.py','ab_confirmatory_20261101/native.py','ab_confirmatory_20261101/native_tail_b.py','research_checks/__init__.py','research_checks/gate.py','research_checks/persistence.py','research_checks/reachability.py']
    names.extend(ROOT/x for x in dependencies)
    manifest=dict(files={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(set(names))})
    (HERE/'stage2_input_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    ops=dict(operations=[dict(id='control_'+str(k)+'_'+a,kind='forward') for k in range(2) for a in ['sham','plus','minus']]+
             [dict(id='reference_parity_'+str(k),kind='forward') for k in range(2)]+
             [dict(id=i['cell']+'_'+a,kind='forward') for i in items for a in ARMS])
    assert len(ops['operations'])==cfg['max_forward']==776
    (HERE/'stage2_schedule.json').write_text(json.dumps(ops,indent=2)+'\n',encoding='utf-8')
    prefix=HERE.relative_to(ROOT).as_posix();evidence=prefix+'/worker_fixtures_v2.json'
    contract=dict(schema_version=1,id='B_NORM_NATIVE_SUFFIX_20261103',kind='experiment',primary_agent='/root/b_switch_fit',
        purpose='Posthoc exact native-readout response to fixedFITnorm-rescaled TCgroupmask directions. All targets/eligibility frozen before new readout; no TC/native prefix calls.',
        tracked_files=[prefix+'/worker.py',prefix+'/common.py',prefix+'/PLAN.txt',prefix+'/config.json',prefix+'/TARGETS_FROZEN.json',prefix+'/stage2_index.json',prefix+'/stage2_input_manifest.json',prefix+'/worker_fixtures.py',prefix+'/worker_fixtures_v2.json'],
        tracked_trees=[],input_manifests=[prefix+'/stage2_input_manifest.json'],gates=[dict(id=k,category=k,evidence=evidence,pointer='/payload/passed',op='eq',expected=True,reason='Actual worker synthetic suffix fixture verifiescontrols,sharedprefix targets,alias/skipbudget,blockaggregation,immutable replay and uncertainattempt failure; historical exact tail adapter remains unchanged.') for k in ['hooks','data','pilot','accounting','restart']],
        circuits=[],structural_scope='Exact post-MLP L15last-positionreplacement to dynamicnativeL16/L17attention+MLP and finalnorm/head. Existing audited ExactTail adapter reused; all required downstreamstates reachable; savedgradient signed halfstep probes recheck nonzero numerical sensitivity.',
        entrypoint=dict(module='analysis.B_norm_control_20261103.worker',args=[]),schedule=prefix+'/stage2_schedule.json',budget=dict(forward=776,backward=0))
    (HERE/'stage2_contract.json').write_text(json.dumps(contract,indent=2)+'\n',encoding='utf-8')
    print(dict(bound_inputs=len(manifest['files']),logical_forwards=len(ops['operations']),eligible=seal['eligible'],skipped_contexts=seal['missing'],new_TC_calls=0,new_prefix_calls=0))
if __name__=='__main__':main()
