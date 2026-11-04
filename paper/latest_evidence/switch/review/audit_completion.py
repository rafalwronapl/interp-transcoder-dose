"""Recompute actual FIT arithmetic and post-run universal norm bound."""
import json
from pathlib import Path
import numpy as np
from safetensors import safe_open
from analysis.AB_fast_followups_20261103.B_switch import analyze as a

r=a.read(a.HERE/'FIT_FEASIBILITY.json');idx=a.read(a.OLD/'source_index.json');ad=a.read(a.OLD/'adoption_v3.json')
ident=a.read(a.ROOT/'analysis/AB_confirmatory_execution_20261101/B_fit_primary_v1/model_identity.json')
p=[];q=[]
for it in idx['fit']:
    doc=it['document'];assert doc['split']=='FIT'
    for dest,arm in [(p,'base'),(q,'end')]:
        op='fit_'+doc['id']+'_'+arm
        dest.append(a.validate_pair(ad['operations'][op],doc,op)['result']['pre'])
with safe_open(str(Path(ident['TC']['folder'])/'params.safetensors'),framework='np') as f:
    t=f.get_tensor('threshold').astype(float);dec=f.get_tensor('w_dec').astype(float)
p=np.array(p);q=np.array(q)
switch=(p>t)!=(q>t)
coef=np.maximum(q,0)*((q>t).astype(float)-(p>t).astype(float))
top=np.array(r['top']);tc=switch[:,top].sum(1);tn=np.linalg.norm(coef[:,top]@dec[top],axis=1)
np.testing.assert_array_equal(tc,r['top_distribution']['count'])
np.testing.assert_allclose(tn,r['top_distribution']['norm'],rtol=1e-12)
assert len(p)==128 and len(set(d['document']['block'] for d in idx['fit']))==32
assert {d['document']['frame'] for d in idx['fit']}=={'so','when'}
for group in r['groups']:
    g=group['features'];c=switch[:,g].sum(1);n=np.linalg.norm(coef[:,g]@dec[g],axis=1)
    np.testing.assert_array_equal(c,group['distribution']['count'])
    np.testing.assert_allclose(n,group['distribution']['norm'],rtol=1e-12,atol=1e-10)
    np.testing.assert_allclose(group['W1_count_norm'],[np.mean(np.abs(np.sort(c)-np.sort(tc))),np.mean(np.abs(np.sort(n)-np.sort(tn)))],rtol=1e-12)
    assert not group['within_FIT_heterogeneity_tolerance']
scores=np.mean(abs(coef),axis=0)*np.linalg.norm(dec,axis=1)
alt=np.setdiff1d(np.arange(len(scores)),top)
bound=float(np.sort(scores[alt])[-32:].sum());deficit=float(np.mean(tn)-bound)
certificate=a.read(a.HERE/'ANALYTIC_NORM_BOUND.json')
assert np.isclose(bound,certificate['max_mean_norm_upper_bound'],rtol=1e-12)
assert np.isclose(deficit,certificate['W1_norm_lower_bound'],rtol=1e-12)
assert deficit>r['tolerance_count_norm'][1]
blocks=np.array([d['document']['block'] for d in idx['fit']]);unique=np.unique(blocks);rng=np.random.default_rng(20261102);null=[]
for _ in range(128):
    keep=np.isin(blocks,rng.permutation(unique)[:len(unique)//2])
    null.append([np.mean(np.abs(np.sort(tc[keep])-np.sort(tc[~keep]))),np.mean(np.abs(np.sort(tn[keep])-np.sort(tn[~keep])))])
np.testing.assert_allclose(np.quantile(null,.95,axis=0),r['tolerance_count_norm'],rtol=1e-12)
out=dict(passed=True,FIT_documents=128,FIT_blocks=32,FIT_frames=['so','when'],all_five_controls_recomputed=True,
    tolerances_recomputed=True,triangle_upper_bound=bound,W1_lower_bound=deficit,
    norm_band_infeasibility_for_disjoint32_in_observed_condition=True,native_calls=0,
    scope='Only historical so+when/full/dose1 FIT pooled, fixed W1 band and switch definition; post-run algebraic certificate, no causal uniqueness')
Path(__file__).with_name('independent_completion_audit.json').write_text(json.dumps(out,indent=2)+'\n')
print(out)
