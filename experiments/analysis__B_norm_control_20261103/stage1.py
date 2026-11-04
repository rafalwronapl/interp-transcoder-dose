"""Cache-only target freeze. No native/TC model instantiation or evaluations."""
import numpy as np
from pathlib import Path
from .common import HERE,ROOT,read,sha,digest,unwrap,put,source,verify_manifest,group_vector,normalize_targets

def main():
    verify_manifest(HERE/'stage1_input_manifest.json');cfg=read(HERE/'config.json');freeze=read(HERE/'FIT_SCALE_FREEZE.json')
    assert freeze['config_sha256']==sha(HERE/'config.json') and freeze['FIT_source_sha256']==sha(ROOT/cfg['fit_source'])
    groups=read(ROOT/cfg['groups_source']);groups=[dict(name='top32',features=groups['top'])]+[dict(name='control_'+str(g['seed']),features=g['features']) for g in groups['groups']]
    assert len(groups)==6 and all(len(g['features'])==len(set(g['features']))==32 for g in groups)
    ident=read(ROOT/cfg['model_identity']);params=Path(ident['TC']['folder'])/'params.safetensors'
    assert sha(params)==ident['TC']['files'][str(params)]['sha256']
    from safetensors import safe_open
    with safe_open(str(params),framework='np') as f:
        threshold=f.get_tensor('threshold').astype(float);decoder=f.get_tensor('w_dec').astype(float)
    out=HERE/'targets';out.mkdir(exist_ok=True);rows=[]
    for item in unwrap(HERE/'stage1_index.json')['items']:
        entries=item['entries'];d=item['document'];cap=source(entries['capture']);base=source(entries['base']);end=source(entries['end'])
        tc=source(entries['tc']);tcbase=source(entries['tcbase']);tcend=source(entries['tcend'])
        rec=cap['result'];assert rec['layer']==15 and rec['answer_ids']==[1304,668]
        assert cap['request']['document']['document']==d and tc['request']['document']['document']==d
        assert tc['request']['intervention']['method']=='TC'
        assert tcbase['request']['intervention']['mode']=='TC_base' and tcend['request']['intervention']['mode']=='TC_endpoint'
        for v in [cap,base,end,tc,tcbase,tcend]:assert v['request']['model_identity']==digest(ident)
        x0=base['request']['intervention'].get('x',base['request']['intervention'].get('input'))
        x1=end['request']['intervention'].get('x',end['request']['intervention'].get('input'))
        assert np.array_equal(np.asarray(x0),rec['states']['x'])
        assert np.array_equal(np.asarray(x1),np.asarray(rec['states']['x'])+np.asarray(tcend['request']['intervention']['edit']))
        assert np.array_equal(np.asarray(base['result']['output'],np.float32),np.asarray(tcbase['result']['output'],np.float32))
        assert np.array_equal(np.asarray(end['result']['output'],np.float32),np.asarray(tcend['result'],np.float32))
        reference=np.asarray(tc['request']['intervention']['target'],np.float32)
        vectors=[group_vector(base['result']['pre'],end['result']['pre'],threshold,decoder,g['features']) for g in groups]
        row=normalize_targets(reference,vectors,cfg['rho'],cfg['eps'])
        row.update(cell=item['cell'],document=d,reference_target=reference.tolist(),reference='TC_FULL/RR',group_names=[g['name'] for g in groups],
                   target_construction='TC_FULL_target-rho*S_group/norm(S_group); no native error D used',capture=entries['capture'],tc=entries['tc'])
        put(out/(item['cell']+'.json'),row);rows.append(row)
    seal=dict(files={p.relative_to(HERE).as_posix():sha(p) for p in sorted(out.glob('*.json'))},input_manifest_sha256=sha(HERE/'stage1_input_manifest.json'),
              FIT_scale_freeze_sha256=sha(HERE/'FIT_SCALE_FREEZE.json'),groups=groups,contexts=len(rows),eligible=sum(r['eligible'] for r in rows),
              missing=sum(not r['eligible'] for r in rows),native_model_loads=0,TC_model_loads=0,native_forwards=0,TC_forwards=0,
              before_new_readouts=True,scope='posthoc32blocks/so+when/full1; fixedFITscale and groups')
    put(HERE/'TARGETS_FROZEN.json',seal);print(dict(contexts=seal['contexts'],eligible=seal['eligible'],missing=seal['missing'],new_forwards=0))
if __name__=='__main__':main()
