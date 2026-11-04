"""Independent synthetic checks only; no actual FIT matching."""
from pathlib import Path
import tempfile,json
import numpy as np
from analysis.AB_fast_followups_20261103.B_switch import analyze as a
p=np.array([[2.,0.,2.,-1.],[0.,2.,.5,2.]])
q=np.array([[.5,2.,3.,-2.],[2.,.5,2.,3.]])
t=np.ones(4);dec=np.array([[1.,1.],[-1.,2.],[2.,-1.],[3.,0.]])
s,c=a.terms(p,q,t)
h1=np.maximum(q,0)*(q>t);base=np.maximum(q,0)*(p>t)
np.testing.assert_array_equal(c,h1-base)
np.testing.assert_allclose(c@dec,h1@dec-base@dec)
assert c[0,0]==-.5
# Exact same marginal distributions must have zero W1 under reordering.
np.testing.assert_array_equal(a.distances(np.array([0,1,2]),np.array([3.,2.,1.]),np.array([2,0,1]),np.array([1.,3.,2.])),[0,0])
rng=np.random.default_rng(66);ss=rng.random((12,80))<.2;cc=ss*rng.normal(size=(12,80));dd=rng.normal(size=(80,5))
top=np.arange(32);blocks=np.repeat(np.arange(6),2)
r=a.match(ss,cc,dd,top,blocks,seeds=[1,2],proposals=8)
assert r==a.match(ss,cc,dd,top,blocks,seeds=[1,2],proposals=8)
assert r['count_mean_deficit_lower_bound']==max(0,r['mean_top_count']-r['mean_all_alternatives_count'])
for group in r['groups']:
    g=group['features'];assert len(g)==32 and len(set(g))==32 and not set(g)&set(top)
    np.testing.assert_array_equal(group['distribution']['count'],ss[:,g].sum(1))
    np.testing.assert_allclose(group['distribution']['norm'],np.linalg.norm(cc[:,g]@dd[g],axis=1),atol=1e-12)
    np.testing.assert_allclose(group['W1_count_norm'],a.distances(ss[:,g].sum(1),np.linalg.norm(cc[:,g]@dd[g],axis=1),ss[:,top].sum(1),np.linalg.norm(cc[:,top]@dd[top],axis=1)),atol=1e-12)
with tempfile.TemporaryDirectory() as td:
    f=Path(td)/'r.json';a.save(f,r);before=f.read_bytes();a.save(f,r);assert before==f.read_bytes()
    try:a.save(f,{'changed':True})
    except AssertionError:pass
    else:raise AssertionError('Changed result accepted')
result=dict(passed=True,OFF_positive_subthreshold=True,switch_sum_vector_identity=True,
    W1_marginal_computation=True,recomputed_group_norm_and_counts=True,disjoint_unique32=True,
    fixed_seed_deterministic=True,changed_output_rejected=True,native_calls=0,actual_FIT_matching_runs=0)
Path(__file__).with_name('independent_pre_run_audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(result)
