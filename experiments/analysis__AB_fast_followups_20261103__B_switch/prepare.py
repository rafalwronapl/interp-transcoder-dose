"""Read-only cache inventory and input freeze; no scientific matching."""
import json,struct
from pathlib import Path
from analyze import HERE,ROOT,OLD,read,sha,save,unwrap

def main():
    idx=read(OLD/'source_index.json');a=read(OLD/'adoption_v3.json')
    identpath=ROOT/'analysis/AB_confirmatory_execution_20261101/B_fit_primary_v1/model_identity.json'
    ident=read(identpath);tensor=Path(ident['TC']['folder'])/'params.safetensors'
    with tensor.open('rb') as f:
        n=struct.unpack('<Q',f.read(8))[0];metadata=json.loads(f.read(n))
    names=[identpath,tensor,Path(ident['TC']['folder'])/'config.json',
           OLD/'source_index.json',OLD/'adoption_v3.json',OLD/'config_v3.json',OLD/'worker_v3.py',OLD/'geometry.py',
           OLD/'run_v3/FEATURE_SELECTION.json',ROOT/a['feature_selection'],
           ROOT/'ab_confirmatory_20261101/transcoder.py',ROOT/'ab_confirmatory_20261101/runtime.py',
           ROOT/'research_checks/gate.py',ROOT/'research_checks/persistence.py',ROOT/'research_checks/reachability.py',ROOT/'research_checks/__init__.py',
           ROOT/'plans/DALSZE_EKSPERYMENTY_A_B_20261103.txt',HERE/'analyze.py',HERE/'prepare.py',HERE/'PROTOCOL.txt',HERE/'fixtures.json']
    inventory=[]
    for item in idx['fit']:
        d=item['document'];assert d['split']=='FIT'
        names.extend([ROOT/item['capture']['cache'],ROOT/item['capture']['receipt']])
        for arm in ['base','end']:
            op='fit_'+d['id']+'_'+arm;e=a['operations'][op]
            names.extend([ROOT/e['cache'],ROOT/e['receipt']])
            v=unwrap(ROOT/e['cache']);assert v['request']['document']==d
            inventory.append(dict(operation=op,cache=e['cache'],receipt=e['receipt'],pre_shape=[len(v['result']['pre'])],output_shape=[len(v['result']['output'])]))
    actual=sha(tensor);assert actual==ident['TC']['files'][str(tensor)]['sha256']
    save(HERE/'INVENTORY.json',dict(fit_documents=len(idx['fit']),fit_blocks=len({i['document']['block'] for i in idx['fit']}),
        frames=sorted({i['document']['frame'] for i in idx['fit']}),cached_measured_condition=dict(operator='full',dose=1),
        preactivation_records=inventory,safetensors=dict(path=tensor.relative_to(ROOT).as_posix(),sha256=actual,metadata=metadata,permitted_value_keys=['threshold','w_dec']),
        missing=['FIT .05 full endpoint preactivations','FIT .05 and1 projected endpoint preactivations','when/transfer FIT frame preactivations'],
        no_new_native_calls_needed_for_observed_condition=True,native_model_loads=0,TC_model_loads=0,pretrained_forwards=0))
    names.append(HERE/'INVENTORY.json')
    save(HERE/'input_manifest.json',dict(files={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(set(names))}))
    prefix=HERE.relative_to(ROOT).as_posix()
    save(HERE/'schedule.json',dict(operations=[]))
    gates=[dict(id=k,category=k,evidence=prefix+'/fixtures.json',pointer='/passed',op='eq',expected=True,
                reason='Cache-only analysis; detailed synthetic evidence and exact input inventory independently reviewed; no hooks/pretrained operations.') for k in ['hooks','data','pilot','accounting','restart']]
    save(HERE/'contract.json',dict(schema_version=1,id='AB_FAST_B_FIT_20261103',kind='experiment',primary_agent='/root/b_switch_fit',
        purpose='FIT-only switch-control feasibility using cached preactivations and two stored parameter arrays; zero pretrained evaluations.',
        tracked_files=[prefix+'/analyze.py',prefix+'/prepare.py',prefix+'/PROTOCOL.txt',prefix+'/fixtures.json',prefix+'/INVENTORY.json'],tracked_trees=[],
        input_manifests=[prefix+'/input_manifest.json'],gates=gates,circuits=[],structural_scope='No causal circuit or suffix executed; cache vector algebra only. No TEST readouts.',
        entrypoint=dict(module='analysis.AB_fast_followups_20261103.B_switch.analyze',args=[]),schedule=prefix+'/schedule.json',budget=dict(forward=0,backward=0)))
    print('Frozen',len(set(names)),'inputs;',len(inventory),'FIT preactivation vectors; no model calls.')

if __name__=='__main__':main()
