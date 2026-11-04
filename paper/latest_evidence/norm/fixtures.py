"""Synthetic numerical and persistence checks; zero pretrained imports/calls."""
import tempfile
from pathlib import Path
import numpy as np
from .common import HERE,put,unwrap,sha,group_vector,normalize_targets

def main():
    checks={}
    # OFF positive endpoint below threshold is a real nonzero contribution.
    v=group_vector([2,0],[.5,2],[1,1],[[2,0],[0,1]],[0,1]);assert np.array_equal(v,[-1,2])
    checks['OFF_and_ON_terms_preserved']=True
    ref=np.array([100.,-30.,10.],np.float32);vec=np.array([[1.,2.,0.],[-2.,1.,3.],[0.,-1.,0.]])
    a=normalize_targets(ref,vec,1.,.25);assert a['eligible'] and len(a['targets'])==3
    assert all(abs(t['actual_norm']-1)<=t['rounding_bound'] for t in a['targets'])
    assert all(t['direction_cosine']>1-1e-9 for t in a['targets'])
    checks['common_norm_and_negative_group_direction_after_float32']=True
    b=normalize_targets(ref,[vec[0],np.zeros(3)],1.,.25);assert not b['eligible'] and b['targets']==[] and b['under_eps_groups']==[1]
    checks['joint_context_exclusion_no_zero_direction_substitution']=True
    c=normalize_targets(ref,[vec[0],[.25,0,0]],1.,.25);assert c['eligible'] and c['targets'][1]['amplification']==4
    checks['nonzero_threshold_boundary_cap4']=True
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)/'x.json';put(p,a);before=p.read_bytes();put(p,a);assert p.read_bytes()==before
        try:put(p,b)
        except ValueError:pass
        else:raise AssertionError('Changed output accepted')
        p.write_bytes(b'broken')
        try:unwrap(p)
        except Exception:pass
        else:raise AssertionError('Corruption accepted')
    checks['immutable_replay_changed_request_and_corruption_rejected']=True
    put(HERE/'fixtures.json',dict(passed=all(checks.values()),checks=checks,pretrained_calls=0,model_loads=0))
    print(checks)
if __name__=='__main__':main()
