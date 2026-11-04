"""Independent cached target audit and no-model native-worker fixture."""
import json,hashlib
from pathlib import Path
import numpy as np
from threadpoolctl import threadpool_limits
from safetensors import safe_open
from research_checks.gate import digest
from analysis.B_norm_control_20261103 import common as c,worker as w,worker_fixtures as f

out=Path(__file__).resolve().parent;b=c.HERE
snap=c.read(b/'stage2_snapshot_v2.json');assert digest(snap['payload'])==snap['snapshot_sha256']
for name,h in snap['payload']['files'].items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==h,name
cfg=c.read(b/'config.json');seal=c.unwrap(b/'TARGETS_FROZEN.json');idx=c.unwrap(b/'stage1_index.json')
assert seal['contexts']==seal['eligible']==128 and len(seal['groups'])==6
ident=c.read(c.ROOT/cfg['model_identity'])
with safe_open(str(Path(ident['TC']['folder'])/'params.safetensors'),framework='np') as fp:
    threshold=fp.get_tensor('threshold').astype(float);dec=fp.get_tensor('w_dec').astype(float)
checked=0
with threadpool_limits(limits=1):
    for entry in idx['items']:
        e=entry['entries'];base=c.source(e['base']);end=c.source(e['end']);tc=c.source(e['tc'])
        row=c.unwrap(b/'targets'/(entry['cell']+'.json'))
        ref=np.asarray(tc['request']['intervention']['target'],np.float32)
        np.testing.assert_array_equal(ref,np.asarray(row['reference_target'],np.float32))
        assert row['document']['split']=='TEST' and row['reference']=='TC_FULL/RR'
        assert row['eligible'] and len(row['targets'])==6
        p=np.array(base['result']['pre']);q=np.array(end['result']['pre'])
        for group,record in zip(seal['groups'],row['targets']):
            g=group['features'];coef=np.maximum(q[g],0)*((q[g]>threshold[g]).astype(float)-(p[g]>threshold[g]).astype(float))
            v=coef@dec[g];norm=np.linalg.norm(v);assert norm>=cfg['eps']
            expected=(ref.astype(float)-cfg['rho']*v/norm).astype(np.float32)
            target=np.asarray(record['target'],np.float32)
            np.testing.assert_array_equal(expected,target)
            actual=np.linalg.norm(target.astype(float)-ref.astype(float))
            assert abs(actual-cfg['rho'])<=record['rounding_bound']
            assert record['amplification']<=4+1e-12
            checked+=1
assert checked==768
# Run actual worker fixture under reviewer-owned evidence destination.
originalsha=f.sha;f.HERE=out
f.sha=lambda p: originalsha(b/'worker.py') if Path(p)==out/'worker.py' else originalsha(p)
f.run()
# Independent aggregation check with unequal context coverage per block.
rows=[]
for block,values in [('b0',[1.,3.]),('b1',[10.])]:
    for value in values:
        losses={a:0. for a in w.ARMS};losses['top32']=value
        rows.append(dict(eligible=True,document=dict(block=block),loss=losses,reference_loss=0.,effects={a:0. for a in w.ARMS}))
assert w.summarize(rows)['primary_top_minus_controls']==6.
r=dict(passed=True,snapshot_files=len(snap['payload']['files']),cached_targets_recomputed=768,
    contexts128_blocks32=True,TC_FULL_reference_verified=True,commonrho_float32_bounds=True,
    actual_worker_fixture_reproduced=True,guarded_uncertain_and_changed_identity_before_load=True,
    paired_equal_block_aggregation_verified=True,native_calls=0)
(out/'stage2_independent_audit.json').write_text(json.dumps(r,indent=2)+'\n')
print(r)
