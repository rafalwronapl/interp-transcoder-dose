"""Independent actual cache/alias/control/statistic audit; no model calls."""
import hashlib,json
from datetime import datetime
from pathlib import Path
import numpy as np
from research_checks.gate import digest

ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'analysis/B_norm_control_20261103';OUT=BASE/'run';REVIEW=BASE/'review'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def unwrap(p):
    v=read(p);assert digest(v['payload'])==v['payload_sha256'],str(p);return v['payload']
def source(e):
    v=unwrap(ROOT/e['cache']);r=unwrap(ROOT/e['receipt']);assert digest(v['request'])==r['request'];return v
def progress(phase):
    (REVIEW/'completion_audit_status.json').write_text(json.dumps(dict(phase=phase))+'\n');print(phase,flush=True)
snap=read(BASE/'completion_snapshot.json');assert digest(snap['payload'])==snap['snapshot_sha256']
for p,h in snap['payload']['files'].items():assert sha(ROOT/p)==h,p
progress('completion_snapshot_hashes_verified')
queue=read(BASE/'queue_snapshot_v2.json');assert digest(queue['payload'])==queue['snapshot_sha256']
for p,h in queue['payload']['files'].items():
    if p not in snap['payload']['files']:assert sha(ROOT/p)==h,p
qcfg=read(BASE/'queue_config.json');finished=unwrap(BASE/'queue_finished.json')
assert finished['B_returncode']==0 and sha(ROOT/qcfg['A_exit_receipt'])==finished['A_exit_receipt_sha256']
assert read(ROOT/qcfg['A_exit_receipt'])['returncode']==0
launches=[p for p in (ROOT/'operations').glob('research_launch_*.json') if read(p).get('snapshot_sha256')==qcfg['B_snapshot_sha256']]
assert len(launches)==1 and read(launches[0])['returncode']==0
cfg=read(BASE/'config.json');sealed=unwrap(OUT/'stage_completed.json');targets_seal=unwrap(BASE/'TARGETS_FROZEN.json');index=unwrap(BASE/'stage2_index.json')
identity=unwrap(OUT/'identity.json');schedule=unwrap(OUT/'schedule.json');planned={v['id'] for v in schedule['operations']}
assert len(planned)==776 and all(v['kind']=='forward' for v in schedule['operations'])
records=[json.loads(line) for line in (OUT/'ledger.jsonl').read_text().splitlines()]
for r in records:assert digest(r['record'])==r['sha256']
attempts={r['record']['operation']:r['record'] for r in records if r['record']['event']=='attempt'}
assert len(attempts)==420
aliases={p.stem:unwrap(p) for p in (OUT/'aliases').glob('*.json')};assert len(aliases)==356
assert not set(attempts)&set(aliases) and set(attempts)|set(aliases)==planned
assert not list((OUT/'skips').glob('*.json')) and len(list((OUT/'model_load_attempts').glob('*.json')))==1
assert sealed['accounting']==dict(forward_attempts=420,backward_attempts=0,aliases=356,skips=0)
frozen_at=datetime.fromisoformat(read(BASE/'TARGETS_FROZEN.json')['created_utc'])
assert all(datetime.fromisoformat(r['utc'])>frozen_at for r in attempts.values())
cache_checked=0
def observed(op,target,record,document):
    global cache_checked
    v=unwrap(OUT/'cache'/(attempts[op]['request']+'.json'));q=v['request']
    assert digest(q)==attempts[op]['request'] and q['model_identity']==identity['model'] and q['code_identity']==identity['code']
    np.testing.assert_array_equal(np.asarray(q['intervention']['target'],np.float32),np.asarray(target,np.float32))
    assert q['document']['record']==record and q['document']['document']==document
    assert q['readout']==dict(answer_ids=[1304,668],orientation='she-minus-he')
    cache_checked+=1;return float(v['result'])
arms=['top32']+['control_'+str(i) for i in range(20261103,20261108)]
rows={p.stem:unwrap(p) for p in (OUT/'results').glob('*.json')};assert len(rows)==128
norms=[];amp=[]
for entry in index['items']:
    row=rows[entry['cell']];target=unwrap(BASE/entry['target']);cap=source(entry['capture'])['result'];tc=source(entry['tc']);native=source(entry['native'])
    assert row['eligible'] and target['eligible'] and row['document']==target['document']
    truth=float(native['result']);reference=float(tc['result']);ref_target=np.asarray(target['reference_target'],np.float32)
    assert row['native_margin']==truth and row['reference_margin']==reference
    np.testing.assert_array_equal(ref_target,np.asarray(tc['request']['intervention']['target'],np.float32))
    known={ref_target.tobytes():reference}
    for arm,t in zip(arms,target['targets']):
        op=entry['cell']+'_'+arm;vector=np.asarray(t['target'],np.float32);key=vector.tobytes()
        if key in known:
            a=aliases[op];assert a['target_sha256']==digest(vector.tolist());assert a['margin']==known[key];value=a['margin']
        else:
            assert op in attempts;value=observed(op,vector,cap,target['document']);known[key]=value
        assert row['margins'][arm]==value and row['effects'][arm]==value-reference
        assert row['loss'][arm]==(value-truth)**2 and row['reference_loss']==(reference-truth)**2
        n=float(np.linalg.norm(vector.astype(float)-ref_target.astype(float)));norms.append(n);amp.append(t['amplification'])
        assert abs(n-cfg['rho'])<=t['rounding_bound'] and t['amplification']<=4
assert len(norms)==768 and cache_checked==412
progress('all412_scientific_caches_and356_exact_aliases_verified')
# Recheck actual technical probes, including new half-step rather than historical repeats.
for number,entry in enumerate(index['controls']):
    cap=source(entry['capture']);gradient=source(entry['gradient']);record=cap['result'];document=cap['request']['document']['document']
    y=np.array(record['states']['y']);g=np.array(gradient['result']['gradient']);gn=np.linalg.norm(g)
    sham=observed('control_'+str(number)+'_sham',y,record,document);assert abs(sham-record['states']['margin'])<=1e-4
    old_h=min(1e-3*max(1.,np.linalg.norm(y)),.01/gn)
    for label,sign in [('plus',1),('minus',-1)]:
        t=(y+sign*.5*old_h*g/gn).astype(np.float32);old=(y+sign*old_h*g/gn).astype(np.float32)
        assert not np.array_equal(t,old)
        value=observed('control_'+str(number)+'_'+label,t,record,document);effect=value-sham
        assert abs(effect)>1e-4 and effect*float(g@(t.astype(float)-y))>0
for number,cell in enumerate(index['reference_parity_cells']):
    entry=next(e for e in index['items'] if e['cell']==cell);target=unwrap(BASE/entry['target']);cap=source(entry['capture'])['result'];tc=source(entry['tc'])
    value=observed('reference_parity_'+str(number),target['reference_target'],cap,target['document']);assert abs(value-float(tc['result']))<=1e-4
assert cache_checked==420
first_science=min(datetime.fromisoformat(r['utc']) for op,r in attempts.items() if not op.startswith(('control_','reference_parity_')))
assert all(datetime.fromisoformat(r['utc'])<first_science for op,r in attempts.items() if op.startswith(('control_','reference_parity_')))
analysis=unwrap(BASE/'FINAL_ANALYSIS.json');summary=unwrap(OUT/'SUMMARY.json');blocks=sorted({r['document']['block'] for r in rows.values()});assert len(blocks)==32
def bm(fn,rr=None):
    rr=list(rows.values()) if rr is None else rr
    return float(np.mean([np.mean([fn(r) for r in rr if r['document']['block']==b]) for b in blocks]))
for arm in arms:
    vals=dict(MSE=bm(lambda r:r['loss'][arm]),MSE_increment=bm(lambda r:r['loss'][arm]-r['reference_loss']),signed_effect=bm(lambda r:r['effects'][arm]),absolute_effect=bm(lambda r:abs(r['effects'][arm])))
    for key,v in vals.items():assert np.isclose(v,analysis['metrics'][arm][key],rtol=1e-13,atol=1e-14)
contrast=bm(lambda r:r['loss']['top32']-np.mean([r['loss'][a] for a in arms[1:]]))
assert np.isclose(contrast,summary['primary_top_minus_controls'],rtol=1e-13)
for frame in ['so','when']:
    rr=[r for r in rows.values() if r['document']['frame']==frame];assert len(rr)==64
    value=bm(lambda r:r['loss']['top32']-np.mean([r['loss'][a] for a in arms[1:]]),rr)
    assert np.isclose(value,summary['per_frame'][frame]['primary_top_minus_controls'],rtol=1e-13)
result=dict(passed=True,snapshot_sha256=snap['snapshot_sha256'],snapshot_files=len(snap['payload']['files']),
    scientific_cache_margins412_verified=True,all356_aliases_byte_exact_in_same_prefix=True,
    raw_native_and_RR_labels_verified=True,all8_actual_controls_passed_before_readouts=True,
    targets768_matched_float32norm_range=[min(norms),max(norms)],maximum_amplification=max(amp),
    block32_context128_metrics_and_frame_contrasts_recomputed=True,primary_top_minus_controls=contrast,
    forward_attempts=420,exact_aliases=356,model_loads=1,TC_calls=0,new_prefix_calls=0,backwards=0,
    queue_and_canonical_exit_chain_verified=True,native_calls_by_reviewer=0)
(REVIEW/'independent_completion_audit.json').write_text(json.dumps(result,indent=2)+'\n');progress('complete');print(result)
